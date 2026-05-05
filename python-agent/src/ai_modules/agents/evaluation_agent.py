"""Evaluation agent backed by AgentCoreLoop and LLM-generated reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import EvaluationGenerator, PlanningLLMClientFactory
from src.ai_modules.models import (
    EvaluationDimension,
    EvaluationPayload,
    ProgressPayload,
    ProgressSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_evaluation_system_prompt
from src.ai_modules.runtime import (
    SystemSnapshot,
)

LOGGER = logging.getLogger(__name__)


class EvaluationAgent(PlaceholderAgent):
    """Evaluate learner readiness and feed planning context."""

    def __init__(
        self,
        llm_client: Any | None = None,
        generator: Any | None = None,
    ) -> None:
        super().__init__("Evaluation Agent", "evaluation")
        self.llm_client = llm_client or PlanningLLMClientFactory.create()
        self.generator = generator

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_evaluation_system_prompt(snapshot)

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
        payload = await self._run_agent_core_loop(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
        )
        params["evaluationResult"] = payload.model_dump(by_alias=True)

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=45,
                message="已完成能力评估",
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
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> EvaluationPayload:
        try:
            # Step 1: Aggregate behavior (deterministic)
            aggregated = self._tool_aggregate_behavior(tool_input={}, params=params, snapshot=snapshot)

            # Step 2: Generate report (1 LLM call)
            return await self._safe_evaluate(
                params=params, snapshot=snapshot, system_prompt=system_prompt,
                aggregated_behavior=aggregated,
            )
        except Exception:
            LOGGER.warning("Evaluation failed, falling back.", exc_info=True)
            return self._fallback_evaluation(params=params, snapshot=snapshot)

    def _tool_aggregate_behavior(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        del tool_input
        profile = params.get("profile", {})
        evaluation = params.get("evaluationResult", {})
        judge_result = params.get("judgeResult", {})
        messages = params.get("messages", [])
        structured_summary = params.get("structuredConversationSummary", {})

        weaknesses = self._unique_items(
            [
                *list(profile.get("knowledgeGaps", [])),
                *list(evaluation.get("weaknesses", [])),
                *list(judge_result.get("weakKnowledgeTags", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        focus = self._unique_items(
            [
                *list(evaluation.get("nextFocus", [])),
                *weaknesses[:3],
                snapshot.current_chapter,
            ]
        )
        strengths = self._unique_items(
            [
                *list(evaluation.get("strengths", [])),
                "愿意持续练习" if params.get("practiceQuestionBatch") else "",
                "具备学习上下文" if params.get("learningContext") else "",
                "最近有复习记录" if snapshot.recent_activities else "",
            ]
        )
        learner_messages = [
            str(message.get("content", ""))
            for message in messages
            if isinstance(message, dict) and message.get("role") == "user"
        ]
        aggregated = {
            "profile": profile,
            "learningContext": params.get("learningContext", {}),
            "judgeResult": judge_result,
            "messages": messages,
            "structuredConversationSummary": structured_summary,
            "snapshot": {
                "studentLevel": snapshot.student_level,
                "knowledgeGaps": snapshot.knowledge_gaps,
                "recentMistakes": snapshot.recent_mistakes,
                "preferredStyle": snapshot.preferred_style,
            },
            "behaviorSignals": {
                "messageCount": len(messages),
                "learnerQuestionCount": len(learner_messages),
                "recentMistakeCount": len(snapshot.recent_mistakes),
                "practiceAccuracy": judge_result.get("accuracy"),
                "conversationKeywords": learner_messages[-3:],
            },
            "candidateStrengths": strengths or ["愿意配合学习"],
            "candidateWeaknesses": weaknesses or ["薄弱点待补充"],
            "recommendedFocus": focus or ["核心概念", "适用条件"],
        }
        params["aggregatedEvaluationContext"] = aggregated
        return aggregated

    async def _tool_generate_report(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        aggregated = params.get("aggregatedEvaluationContext") or tool_input
        payload = await self._safe_evaluate(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
            aggregated_behavior=aggregated if isinstance(aggregated, dict) else {},
        )
        return payload.model_dump(by_alias=True)

    async def _safe_evaluate(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
        aggregated_behavior: dict[str, Any],
    ) -> EvaluationPayload:
        try:
            generator = self.generator or EvaluationGenerator()
            return await generator.evaluate(
                system_prompt=system_prompt,
                context_payload=self._build_context_payload(
                    params=params,
                    snapshot=snapshot,
                    aggregated_behavior=aggregated_behavior,
                ),
            )
        except Exception:
            return self._fallback_evaluation(
                params=params,
                snapshot=snapshot,
                aggregated_behavior=aggregated_behavior,
            )

    def _build_context_payload(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        aggregated_behavior: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "profile": params.get("profile", {}),
            "learningContext": params.get("learningContext", {}),
            "judgeResult": params.get("judgeResult", {}),
            "messages": params.get("messages", []),
            "snapshot": {
                "studentLevel": snapshot.student_level,
                "knowledgeGaps": snapshot.knowledge_gaps,
                "recentMistakes": snapshot.recent_mistakes,
                "preferredStyle": snapshot.preferred_style,
            },
            "aggregatedBehavior": aggregated_behavior,
        }

    def _fallback_evaluation(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        aggregated_behavior: dict[str, Any] | None = None,
    ) -> EvaluationPayload:
        profile = params.get("profile", {})
        gaps = self._unique_items(
            [
                *list(profile.get("knowledgeGaps", [])),
                *list((aggregated_behavior or {}).get("candidateWeaknesses", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        level = str(profile.get("studentLevel") or snapshot.student_level or "BASIC")
        focus = self._unique_items(
            list((aggregated_behavior or {}).get("recommendedFocus", [])) or gaps[:3]
        )
        strengths = self._unique_items(
            list((aggregated_behavior or {}).get("candidateStrengths", []))
        )
        dimensions = [
            EvaluationDimension(
                name="knowledge_foundation",
                level=level,
                evidence=f"当前识别到的薄弱点: {', '.join(gaps) or '暂无'}",
                recommendation="优先复习核心概念和适用条件。",
            ),
            EvaluationDimension(
                name="problem_solving",
                level="BASIC" if gaps else "INTERMEDIATE",
                evidence=f"近期错误: {', '.join(snapshot.recent_mistakes) or '暂无'}",
                recommendation="做题前先判断条件，再给出理由。",
            ),
        ]
        return EvaluationPayload(
            overallLevel=level,
            strengths=strengths or ["愿意配合练习", "具备基础学习上下文"],
            weaknesses=gaps or ["薄弱点待补充"],
            nextFocus=focus or ["核心概念", "适用条件"],
            dimensions=dimensions,
            summaryText=(
                f"当前评估等级为 {level}，"
                f"建议优先聚焦 {', '.join((focus or gaps[:3])[:3]) or '核心概念与适用条件'}。"
            ),
        )

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
