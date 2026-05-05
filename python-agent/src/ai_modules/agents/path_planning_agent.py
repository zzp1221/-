"""Path planning agent backed by AgentCoreLoop and learning-plan persistence."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import LearningPathGenerator, PlanningLLMClientFactory
from src.ai_modules.memory import (
    InMemoryLearningPlanStore,
    LearningPlanStore,
    PostgresLearningPlanStore,
)
from src.ai_modules.models import (
    LearningPlanPayload,
    LearningPlanStep,
    ProgressPayload,
    ProgressSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_path_planning_system_prompt
from src.ai_modules.runtime import (
    SystemSnapshot,
)


class PathPlanningAgent(PlaceholderAgent):
    """Produce a sequenced learning plan from evaluation and profile context."""

    def __init__(
        self,
        llm_client: Any | None = None,
        learning_plan_store: LearningPlanStore | None = None,
        generator: Any | None = None,
    ) -> None:
        super().__init__("Path Planning Agent", "path_planning")
        self.llm_client = llm_client or PlanningLLMClientFactory.create()
        self.learning_plan_store = learning_plan_store or PostgresLearningPlanStore()
        self.fallback_learning_plan_store = InMemoryLearningPlanStore()
        self.generator = generator

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_path_planning_system_prompt(snapshot)

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> AsyncIterator[SSEEvent]:
        del service_type
        user_id = str(params.get("userId") or "00000000-0000-0000-0000-000000000001")
        core_loop_result = await self._run_agent_core_loop(
            user_id=user_id,
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
        )
        payload = LearningPlanPayload.model_validate(core_loop_result["learningPath"])
        params["learningPath"] = payload.model_dump(by_alias=True)
        params["learningPlanPersistence"] = core_loop_result["persistence"]

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=75,
                message="已生成学习路径",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text=payload.summary_text),
        )

    async def _run_agent_core_loop(
        self,
        *,
        user_id: str,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        try:
            # Step 1: Analyze profile (deterministic)
            planning_context = self._tool_analyze_profile(tool_input={}, params=params, snapshot=snapshot)

            # Step 2: Generate path (1 LLM call)
            plan = await self._safe_plan(
                params=params, snapshot=snapshot, system_prompt=system_prompt,
                planning_context=planning_context,
            )

            # Step 3: Save to store (deterministic)
            metadata = await self._safe_save_learning_plan(
                user_id=user_id, course_id=self._resolve_course_id(params),
                plan=plan, trigger_source=self._resolve_trigger_source(params),
            )
            return {
                "learningPath": plan.model_dump(by_alias=True),
                "persistence": metadata,
                "summaryText": plan.summary_text,
            }
        except Exception:
            fallback_plan = self._fallback_plan(params=params, snapshot=snapshot)
            fallback_metadata = await self._safe_save_learning_plan(
                user_id=user_id, course_id=self._resolve_course_id(params),
                plan=fallback_plan, trigger_source=self._resolve_trigger_source(params),
            )
            return {
                "learningPath": fallback_plan.model_dump(by_alias=True),
                "persistence": fallback_metadata,
                "summaryText": fallback_plan.summary_text,
            }

    def _tool_analyze_profile(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        del tool_input
        evaluation = params.get("evaluationResult", {})
        profile = params.get("profile", {})
        judge_result = params.get("judgeResult", {})
        focus = self._unique_items(
            [
                *list(evaluation.get("nextFocus", [])),
                *list(judge_result.get("weakKnowledgeTags", [])),
                *list(profile.get("knowledgeGaps", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        context = {
            "goal": self._resolve_goal(params),
            "targetPeriod": str(params.get("targetPeriod") or "").strip() or "7天",
            "weeklyHours": str(params.get("weeklyHours") or "").strip() or "6",
            "currentProgress": str(params.get("currentProgress") or "").strip() or "已完成基础概念，准备进入案例训练",
            "studentLevel": str(
                profile.get("studentLevel")
                or evaluation.get("overallLevel")
                or snapshot.student_level
                or "BASIC"
            ),
            "weaknesses": self._unique_items(
                [
                    *list(evaluation.get("weaknesses", [])),
                    *list(profile.get("knowledgeGaps", [])),
                    *list(snapshot.knowledge_gaps),
                ]
            ),
            "nextFocus": focus or ["核心概念", "适用条件"],
            "preferredStyle": str(
                profile.get("learningPreference")
                or snapshot.preferred_style
                or "step_by_step"
            ),
            "recentMistakes": list(snapshot.recent_mistakes),
            "triggerSource": self._resolve_trigger_source(params),
        }
        params["pathPlanningContext"] = context
        return context

    async def _tool_generate_path(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        analysis = params.get("pathPlanningContext") or tool_input
        payload = await self._safe_plan(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
            planning_context=analysis if isinstance(analysis, dict) else {},
        )
        serialized = payload.model_dump(by_alias=True)
        params["draftLearningPath"] = serialized
        return serialized

    async def _tool_update_path_plan(
        self,
        *,
        tool_input: dict[str, Any],
        user_id: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        draft_payload = params.get("draftLearningPath") or tool_input
        plan = LearningPlanPayload.model_validate(draft_payload)
        metadata = await self._safe_save_learning_plan(
            user_id=user_id,
            course_id=self._resolve_course_id(params),
            plan=plan,
            trigger_source=self._resolve_trigger_source(params),
        )
        return {
            "learningPath": plan.model_dump(by_alias=True),
            "persistence": metadata,
            "summaryText": plan.summary_text,
        }

    async def _safe_plan(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
        planning_context: dict[str, Any],
    ) -> LearningPlanPayload:
        try:
            generator = self.generator or LearningPathGenerator()
            return await generator.plan(
                system_prompt=system_prompt,
                context_payload=self._build_context_payload(
                    params=params,
                    snapshot=snapshot,
                    planning_context=planning_context,
                ),
            )
        except Exception:
            return self._fallback_plan(
                params=params,
                snapshot=snapshot,
                planning_context=planning_context,
            )

    def _build_context_payload(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        planning_context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "evaluationResult": params.get("evaluationResult", {}),
            "profile": params.get("profile", {}),
            "learningContext": params.get("learningContext", {}),
            "plannerInputs": {
                "targetPeriod": str(params.get("targetPeriod") or "").strip(),
                "weeklyHours": str(params.get("weeklyHours") or "").strip(),
                "currentProgress": str(params.get("currentProgress") or "").strip(),
            },
            "judgeResult": params.get("judgeResult", {}),
            "snapshot": {
                "studentLevel": snapshot.student_level,
                "knowledgeGaps": snapshot.knowledge_gaps,
                "preferredStyle": snapshot.preferred_style,
            },
            "planningContext": planning_context,
        }

    def _fallback_plan(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        planning_context: dict[str, Any] | None = None,
    ) -> LearningPlanPayload:
        evaluation = params.get("evaluationResult", {})
        planning_context = planning_context or {}
        target_period = str(planning_context.get("targetPeriod") or params.get("targetPeriod") or "7天").strip()
        weekly_hours = str(planning_context.get("weeklyHours") or params.get("weeklyHours") or "6").strip()
        current_progress = str(
            planning_context.get("currentProgress")
            or params.get("currentProgress")
            or "已完成基础概念，准备进入案例训练"
        ).strip()
        weaknesses = self._unique_items(
            [
                *list(planning_context.get("weaknesses", [])),
                *list(evaluation.get("weaknesses", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        goal = str(planning_context.get("goal") or self._resolve_goal(params))
        steps = [
            LearningPlanStep(
                title="阶段 1：梳理概念与案例入口",
                objective=f"结合当前进度“{current_progress}”，先补齐 {weaknesses[0] if weaknesses else '核心概念'}，为进入案例训练做准备",
                activities=["阅读核心讲义", "整理概念与适用条件", "挑选 1 个典型案例做拆解"],
                successCriteria="能独立说出定义、条件和一个反例",
            ),
            LearningPlanStep(
                title="阶段 2：案例迁移训练",
                objective=f"按每周约 {weekly_hours} 小时的投入，把知识点迁移到 3-5 个典型案例中",
                activities=["先口头分析案例", "再动手实现关键步骤", "记录错误与修正策略"],
                successCriteria="连续 3 个案例能先讲清判断依据，再完成实现",
            ),
            LearningPlanStep(
                title="阶段 3：总结与复盘",
                objective=f"在 {target_period} 内形成可复用的解题与实现模板，完成一次阶段复盘",
                activities=["复盘错题/错例", "总结通用模板", "输出一份学习笔记或讲解"],
                successCriteria="能独立解释一个完整场景，并给出可迁移的解决步骤",
            ),
        ]
        return LearningPlanPayload(
            goal=goal,
            duration=target_period,
            milestones=self._unique_items(
                [
                    "完成概念梳理",
                    "进入案例训练",
                    "形成复盘闭环",
                    *(planning_context.get("nextFocus", [])[:1] if planning_context else []),
                ]
            ),
            steps=steps,
            summaryText=(
                f"已生成一个 {target_period} 的学习路径，"
                f"按每周约 {weekly_hours} 小时推进，围绕“{goal}”优先覆盖 {', '.join(weaknesses[:3]) or '核心概念'}。"
            ),
        )

    async def _safe_save_learning_plan(
        self,
        *,
        user_id: str,
        course_id: str | None,
        plan: LearningPlanPayload,
        trigger_source: str,
    ) -> dict[str, Any]:
        try:
            metadata = await self.learning_plan_store.save_plan(
                user_id=user_id,
                course_id=course_id,
                plan=plan,
                trigger_source=trigger_source,
            )
            self.fallback_learning_plan_store.active_plans_by_user[user_id] = {
                **metadata,
                "learningPath": plan.model_dump(by_alias=True),
                "summaryText": plan.summary_text,
            }
            return metadata
        except Exception:
            return await self.fallback_learning_plan_store.save_plan(
                user_id=user_id,
                course_id=course_id,
                plan=plan,
                trigger_source=trigger_source,
            )

    def _resolve_goal(self, params: dict[str, Any]) -> str:
        evaluation = params.get("evaluationResult", {})
        return str(
            params.get("goal")
            or params.get("currentProgress")
            or (params.get("pathPlanningContext") or {}).get("goal")
            or (evaluation.get("nextFocus") or ["提升当前薄弱点"])[0]
            or "提升当前薄弱点"
        )

    def _resolve_trigger_source(self, params: dict[str, Any]) -> str:
        if params.get("manualRefresh"):
            return "MANUAL_REFRESH"
        if params.get("judgeResult"):
            return "PRACTICE_RESULT"
        if params.get("evaluationResult"):
            return "EVALUATION"
        if params.get("profileUpdate"):
            return "PROFILE_UPDATE"
        return "INITIAL"

    def _resolve_course_id(self, params: dict[str, Any]) -> str | None:
        return params.get("courseId")

    def _unique_items(self, items: list[Any]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for item in items:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            normalized.append(text)
        return normalized
