"""Profile agent backed by AgentCoreLoop and profile persistence tools."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import ProfileAnalyzer, ProfileLLMClientFactory
from src.ai_modules.memory import InMemoryProfileStore, PostgresProfileStore, ProfileStore
from src.ai_modules.models import (
    LearnerProfileSnapshot,
    ProgressPayload,
    ProgressSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.models.profile import LearnerProfileDimensions
from src.ai_modules.prompts import build_profile_system_prompt
from src.ai_modules.runtime import (
    AgentCoreLoop,
    PermissionLevel,
    RecoveryEngine,
    RecoveryFailureType,
    SystemSnapshot,
    ToolRegistry,
)


class ProfileAgent(PlaceholderAgent):
    """Extract and persist learner profile dimensions from dialogue."""

    def __init__(
        self,
        profile_store: ProfileStore | None = None,
        llm_client: Any | None = None,
        profile_analyzer: Any | None = None,
        heartbeat_interval_seconds: float = 15.0,
    ) -> None:
        super().__init__("Profile Agent", "profiling")
        self.profile_store = profile_store or PostgresProfileStore()
        self.fallback_profile_store = InMemoryProfileStore()
        self.llm_client = llm_client or ProfileLLMClientFactory.create()
        self.profile_analyzer = profile_analyzer or ProfileAnalyzer()
        self.recovery_engine = RecoveryEngine()
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_profile_system_prompt(snapshot)

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
        del service_type, snapshot
        user_id = str(params.get("userId") or "00000000-0000-0000-0000-000000000001")
        next_seq = seq
        profile_task = asyncio.create_task(
            self._run_agent_core_loop(
                user_id=user_id,
                params=params,
                system_prompt=system_prompt,
            )
        )
        while not profile_task.done():
            try:
                core_loop_result = await asyncio.wait_for(
                    asyncio.shield(profile_task),
                    timeout=self.heartbeat_interval_seconds,
                )
                break
            except TimeoutError:
                yield ProgressSSEEvent(
                    taskId=task_id,
                    traceId=trace_id,
                    seq=next_seq,
                    payload=ProgressPayload(
                        stage=self.stage_name,
                        percent=88,
                        message="画像更新仍在执行中，请稍候",
                    ),
                )
                next_seq += 1
        else:
            core_loop_result = await profile_task

        core_loop_result = core_loop_result if "core_loop_result" in locals() else await profile_task
        params["profileUpdate"] = core_loop_result

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=90,
                message="已完成画像分析并写入快照",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq + 1,
            payload=ResultChunkPayload(
                text=core_loop_result["summaryText"],
            ),
        )

    async def _run_agent_core_loop(
        self,
        *,
        user_id: str,
        params: dict[str, Any],
        system_prompt: str,
    ) -> dict[str, Any]:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="read_profile",
            fn=lambda tool_input: self._tool_read_profile(tool_input=tool_input, user_id=user_id),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Read current learner profile snapshot.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="analyze_dialogue",
            fn=lambda tool_input: self._tool_analyze_dialogue(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Analyze dialogue and extract learner profile dimensions. Returns dimensions dict.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="update_profile",
            fn=lambda tool_input: self._tool_update_profile(tool_input=tool_input, user_id=user_id, params=params),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Persist learner profile dimensions into storage. Pass the output of analyze_dialogue directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "knowledgeFoundation": {"type": "string"},
                    "learningGoal": {"type": "string"},
                    "weakPoints": {"type": "array", "items": {"type": "string"}},
                    "confidenceLevel": {"type": "string"},
                    "summaryText": {"type": "string"},
                },
                "additionalProperties": True,
            },
        )

        result = await AgentCoreLoop(
            llm_client=self.llm_client,
            tool_registry=tool_registry,
            recovery_engine=RecoveryEngine(),
            max_iterations=5,
            agent_level=PermissionLevel.SYSTEM_WRITE,
        ).run(
            system_prompt=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"请基于当前对话为用户 {user_id} 更新画像。",
                }
            ],
        )
        if not result.tool_results:
            return {"summaryText": result.final_text}
        update_output = result.tool_results[-1].output
        return update_output if isinstance(update_output, dict) else {"summaryText": result.final_text}

    async def _tool_read_profile(
        self,
        *,
        tool_input: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any]:
        del tool_input
        snapshot = await self._safe_read_profile(user_id)
        if snapshot is None:
            return {"exists": False}
        return {
            "exists": True,
            "userId": snapshot.user_id,
            "version": snapshot.version,
            "profile": snapshot.profile.model_dump(by_alias=True),
        }

    async def _tool_analyze_dialogue(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        messages = params.get("messages") or params.get("conversation") or []
        structured_summary = params.get("structuredConversationSummary", {})
        profile_context = params.get("profile", {})
        judge_result = params.get("judgeResult", {})
        practice_batch = params.get("practiceQuestionBatch", {})
        joined_user_content = " ".join(
            str(item.get("content", ""))
            for item in messages
            if isinstance(item, dict) and item.get("role") == "user"
        )
        practice_context_text = self._build_practice_context_text(
            judge_result=judge_result,
            practice_batch=practice_batch,
        )
        combined_text = " ".join(part for part in [joined_user_content, practice_context_text] if part)
        context_payload = {
            "messages": messages,
            "structuredConversationSummary": structured_summary,
            "profile": profile_context,
            "judgeResult": judge_result,
            "practiceQuestionBatch": practice_batch,
            "combinedUserText": combined_text,
            "profileSource": str(params.get("profileSource") or "CONVERSATION"),
        }
        try:
            dimensions = await self.profile_analyzer.analyze(context_payload=context_payload)
        except Exception:
            learning_goal = self._infer_learning_goal(structured_summary, combined_text)
            if judge_result and not structured_summary.get("learnerGoal"):
                topic = practice_batch.get("topic") or "当前主题"
                learning_goal = f"掌握{topic}相关知识点"
            weak_points = self._infer_weak_points(structured_summary, combined_text)
            practice_weak_tags = list(judge_result.get("weakKnowledgeTags", []))
            if practice_weak_tags:
                weak_points = practice_weak_tags
            confidence_level = self._infer_confidence(combined_text)
            if judge_result:
                accuracy = float(judge_result.get("accuracy", 0.0))
                if accuracy >= 0.8:
                    confidence_level = "MEDIUM"
                elif accuracy < 0.5:
                    confidence_level = "LOW"

            dimensions = LearnerProfileDimensions(
                knowledgeFoundation=self._infer_knowledge_foundation(combined_text, profile_context),
                learningGoal=learning_goal,
                professionalBackground=str(profile_context.get("professionalBackground") or "未提供"),
                learningPreference=self._infer_learning_preference(structured_summary, combined_text),
                cognitiveStyle=self._infer_cognitive_style(combined_text),
                weakPoints=weak_points,
                learningPace=self._infer_learning_pace(combined_text),
                confidenceLevel=confidence_level,
                source=str(params.get("profileSource") or "CONVERSATION"),
                summaryText="",
            )
            summary_text = self._build_summary_text(dimensions)
            dimensions.summary_text = summary_text
        serialized_dimensions = dimensions.model_dump(by_alias=True)
        params["analyzedProfileDimensions"] = serialized_dimensions
        return serialized_dimensions

    async def _tool_update_profile(
        self,
        *,
        tool_input: dict[str, Any],
        user_id: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        analyzed_dimensions = self._latest_analyzed_dimensions(params)
        dimensions = LearnerProfileDimensions.model_validate(analyzed_dimensions or tool_input)
        snapshot = await self._safe_update_profile(
            user_id=user_id,
            dimensions=dimensions,
            source_session_id=params.get("conversationId"),
        )
        return {
            "userId": snapshot.user_id,
            "version": snapshot.version,
            "summaryText": snapshot.profile.summary_text,
            "dimensions": snapshot.profile.model_dump(by_alias=True),
        }

    def _latest_analyzed_dimensions(self, params: dict[str, Any]) -> dict[str, Any] | None:
        return params.get("analyzedProfileDimensions")

    def _build_practice_context_text(
        self,
        *,
        judge_result: dict[str, Any],
        practice_batch: dict[str, Any],
    ) -> str:
        if not judge_result:
            return ""
        topic = str(practice_batch.get("topic") or "当前主题")
        summary = str(judge_result.get("summary") or "")
        weak_tags = ", ".join(str(tag) for tag in judge_result.get("weakKnowledgeTags", []))
        return " ".join(part for part in [topic, summary, weak_tags] if part)

    async def _safe_read_profile(self, user_id: str) -> LearnerProfileSnapshot | None:
        try:
            return await self.profile_store.read_profile(user_id)
        except Exception:
            return await self.fallback_profile_store.read_profile(user_id)

    async def _safe_update_profile(
        self,
        *,
        user_id: str,
        dimensions: LearnerProfileDimensions,
        source_session_id: str | None,
    ) -> LearnerProfileSnapshot:
        async def operation() -> LearnerProfileSnapshot:
            snapshot = await self.profile_store.update_profile(
                user_id=user_id,
                dimensions=dimensions,
                source_session_id=source_session_id,
            )
            self.fallback_profile_store.snapshots[user_id] = snapshot
            return snapshot

        async def fallback_operation() -> LearnerProfileSnapshot:
            snapshot = await self.fallback_profile_store.update_profile(
                user_id=user_id,
                dimensions=dimensions,
                source_session_id=source_session_id,
            )
            await self.recovery_engine.recover_profile_update_failed(
                user_id=user_id,
                fallback_payload={
                    "version": snapshot.version,
                    "summaryText": snapshot.profile.summary_text,
                },
            )
            return snapshot

        return await self.recovery_engine.call_with_recovery(
            failure_type=RecoveryFailureType.PROFILE_UPDATE_FAILED,
            operation=operation,
            fallback_operation=fallback_operation,
        )

    def _infer_knowledge_foundation(self, text: str, profile_context: dict[str, Any]) -> str:
        if profile_context.get("studentLevel"):
            return str(profile_context["studentLevel"])
        if any(keyword in text for keyword in ("不太懂", "刚学", "入门")):
            return "BASIC"
        if any(keyword in text for keyword in ("熟悉", "会做", "复习")):
            return "INTERMEDIATE"
        return "UNKNOWN"

    def _infer_learning_goal(self, structured_summary: dict[str, Any], text: str) -> str:
        goal = structured_summary.get("learnerGoal")
        if goal:
            return str(goal)
        for keyword in ("掌握", "复习", "理解", "提高"):
            if keyword in text:
                return text[:32]
        return "待补充学习目标"

    def _infer_learning_preference(self, structured_summary: dict[str, Any], text: str) -> str:
        preferred = structured_summary.get("preferredHelpStyle")
        if preferred:
            return str(preferred)
        if "例子" in text:
            return "example_first"
        if "一步步" in text or "详细" in text:
            return "step_by_step"
        return "concept_then_question"

    def _infer_cognitive_style(self, text: str) -> str:
        if "为什么" in text or "原理" in text:
            return "reasoning_oriented"
        if "怎么做" in text or "步骤" in text:
            return "procedural_oriented"
        return "mixed"

    def _infer_weak_points(self, structured_summary: dict[str, Any], text: str) -> list[str]:
        weak_points = list(structured_summary.get("knownGaps", []))
        if weak_points:
            return weak_points
        if "分不清" in text:
            return ["概念区分不清"]
        if "总错" in text:
            return ["题目条件判断不稳"]
        return []

    def _infer_learning_pace(self, text: str) -> str:
        if "慢一点" in text or "一步步" in text:
            return "steady"
        if "尽快" in text:
            return "fast"
        return "normal"

    def _infer_confidence(self, text: str) -> str:
        if any(keyword in text for keyword in ("不太懂", "不会", "总错")):
            return "LOW"
        if any(keyword in text for keyword in ("会", "熟悉", "掌握")):
            return "MEDIUM"
        return "UNKNOWN"

    def _build_summary_text(self, dimensions: LearnerProfileDimensions) -> str:
        return (
            f"画像更新完成：知识基础={dimensions.knowledge_foundation}，"
            f"学习目标={dimensions.learning_goal}，"
            f"学习偏好={dimensions.learning_preference}，"
            f"认知风格={dimensions.cognitive_style}，"
            f"薄弱点={', '.join(dimensions.weak_points) or '暂无'}，"
            f"信心度={dimensions.confidence_level}。"
        )
