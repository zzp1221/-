"""Tutor agent backed by AgentCoreLoop, structured compaction and persisted memory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import TutorLLMClientFactory
from src.ai_modules.memory import MongoConversationSummaryStore
from src.ai_modules.models import (
    DialogState,
    ProgressPayload,
    ProgressSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_tutor_system_prompt
from src.ai_modules.runtime import (
    AgentCoreLoop,
    ConversationCompactor,
    PermissionLevel,
    RecoveryEngine,
    SnapshotBuilder,
    SystemSnapshot,
    ToolRegistry,
)


class TutorAgent(PlaceholderAgent):
    """Guide the learner using recent dialogue and retrieved evidence."""

    def __init__(
        self,
        compactor: ConversationCompactor | None = None,
        summary_store: Any | None = None,
        llm_client: Any | None = None,
    ) -> None:
        super().__init__("Tutor Agent", "tutoring")
        self.compactor = compactor or ConversationCompactor()
        self.summary_store = summary_store or MongoConversationSummaryStore()
        self.llm_client = llm_client or TutorLLMClientFactory.create()

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_tutor_system_prompt(snapshot)

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
        conversation = self._extract_conversation(params)
        compaction_result = self.compactor.compact(conversation)
        params["compactedConversation"] = compaction_result.compacted_messages
        params["structuredConversationSummary"] = compaction_result.structured_summary.model_dump(
            by_alias=True
        )
        params["conversationSummary"] = compaction_result.summary

        persisted_summary = await self._load_persisted_summary(
            conversation_id=self._conversation_id(params, task_id),
            user_id=params.get("userId"),
        )
        if compaction_result.was_compacted:
            await self._persist_summary(
                params=params,
                task_id=task_id,
                structured_summary=compaction_result.structured_summary.model_dump(by_alias=True),
            )

        strategy = self._select_strategy(snapshot=snapshot, params=params)
        response_text = await self._run_agent_core_loop(
            system_prompt=system_prompt,
            params=params,
            snapshot=snapshot,
            persisted_summary=persisted_summary,
        )
        dialog_state = DialogState(
            conversationId=self._conversation_id(params, task_id),
            turnId=f"{task_id}-turn",
            pedagogyStrategy=strategy,
            nextAction="ask_follow_up",
        )

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=75 if compaction_result.was_compacted else 60,
                message=(
                    "已压缩历史对话并通过 AgentCoreLoop 生成辅导回答"
                    if compaction_result.was_compacted
                    else "已通过 AgentCoreLoop 生成辅导回答"
                ),
            ),
            dialogState=dialog_state,
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(text=response_text),
            dialogState=dialog_state,
        )

    def _extract_conversation(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        candidates = params.get("messages") or params.get("conversation") or []
        if not isinstance(candidates, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "role": item.get("role", "user"),
                    "content": item.get("content", ""),
                }
            )
        return normalized

    def _select_strategy(self, *, snapshot: SystemSnapshot, params: dict[str, Any]) -> str:
        retrieval_result = params.get("retrievalResult", {})
        documents = retrieval_result.get("documents", [])
        if snapshot.knowledge_gaps and documents:
            return "retrieval_grounded_scaffold"
        if snapshot.knowledge_gaps:
            return "diagnostic_scaffold"
        return "concept_explain_then_check"

    async def _run_agent_core_loop(
        self,
        *,
        system_prompt: str,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        persisted_summary: dict[str, Any] | None,
    ) -> str:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="load_conversation_memory",
            fn=lambda tool_input: self._tool_load_conversation_memory(
                tool_input=tool_input,
                persisted_summary=persisted_summary,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="Load the latest structured conversation summary from persistent memory.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_compacted_context",
            fn=lambda tool_input: self._tool_read_compacted_context(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="Read the latest structured compacted conversation context.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_retrieval_evidence",
            fn=lambda tool_input: self._tool_read_retrieval_evidence(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="Read the retrieved evidence supporting the tutoring answer.",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )

        core_loop = AgentCoreLoop(
            llm_client=self.llm_client,
            tool_registry=tool_registry,
            recovery_engine=RecoveryEngine(),
            max_iterations=4,
            agent_level=PermissionLevel.READ_ONLY,
        )
        user_query = str(
            params.get("query")
            or params.get("message")
            or params.get("rewrittenQuery")
            or params.get("structuredConversationSummary", {}).get("lastUserMessage")
            or "当前主题"
        )
        result = await core_loop.run(
            system_prompt=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"请基于当前对话上下文和检索证据，对 `{user_query}` 给出一段辅导回答，"
                        "并在结尾提出一个追问。"
                    ),
                }
            ],
        )
        return result.final_text

    async def _load_persisted_summary(
        self,
        *,
        conversation_id: str,
        user_id: str | None,
    ) -> dict[str, Any] | None:
        try:
            document = await self.summary_store.get_latest_summary(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        except Exception:
            return None
        if document is None:
            return None
        return document.model_dump(by_alias=True)

    async def _persist_summary(
        self,
        *,
        params: dict[str, Any],
        task_id: str,
        structured_summary: dict[str, Any],
    ) -> None:
        from src.ai_modules.memory import ConversationSummaryDocument

        document = ConversationSummaryDocument(
            conversationId=self._conversation_id(params, task_id),
            userId=params.get("userId"),
            taskId=task_id,
            topicFocus=structured_summary.get("topicFocus", []),
            learnerGoal=structured_summary.get("learnerGoal"),
            knownGaps=structured_summary.get("knownGaps", []),
            unresolvedQuestions=structured_summary.get("unresolvedQuestions", []),
            preferredHelpStyle=structured_summary.get("preferredHelpStyle"),
            lastUserMessage=structured_summary.get("lastUserMessage"),
            recentProgress=structured_summary.get("recentProgress", []),
            summaryText=structured_summary.get("summaryText", ""),
        )
        try:
            await self.summary_store.save_summary(document)
        except Exception:
            return

    def _conversation_id(self, params: dict[str, Any], task_id: str) -> str:
        return str(params.get("conversationId") or task_id)

    def _tool_load_conversation_memory(
        self,
        *,
        tool_input: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
    ) -> dict[str, Any]:
        del tool_input
        return persisted_summary or {}

    def _tool_read_compacted_context(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        summary = params.get("structuredConversationSummary", {})
        return {
            **summary,
            "recentMessages": params.get("compactedConversation", [])[-2:],
        }

    def _tool_read_retrieval_evidence(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        retrieval_result = params.get("retrievalResult", {})
        return {
            "query": params.get("query"),
            "rewrittenQuery": params.get("rewrittenQuery"),
            "documents": retrieval_result.get("documents", []),
            "sourcesSummary": retrieval_result.get("sourcesSummary", ""),
        }
