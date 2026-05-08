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
                percent=30 if compaction_result.was_compacted else 20,
                message=(
                    "已压缩历史对话，开始流式生成辅导回答"
                    if compaction_result.was_compacted
                    else "开始流式生成辅导回答"
                ),
            ),
            dialogState=dialog_state,
        )

        current_seq = seq + 1
        streamed = False
        try:
            async for token in self._try_direct_chat_stream(
                system_prompt=system_prompt,
                params=params,
                persisted_summary=persisted_summary,
            ):
                streamed = True
                yield ResultChunkSSEEvent(
                    taskId=task_id,
                    traceId=trace_id,
                    seq=current_seq,
                    payload=ResultChunkPayload(text=token, stage="tutoring"),
                    dialogState=dialog_state,
                )
                current_seq += 1
        except Exception:
            pass

        if not streamed:
            response_text = await self._run_agent_core_loop(
                system_prompt=system_prompt,
                params=params,
                snapshot=snapshot,
                persisted_summary=persisted_summary,
            )
            yield ResultChunkSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=current_seq,
                payload=ResultChunkPayload(text=response_text, stage="tutoring"),
                dialogState=dialog_state,
            )
            current_seq += 1

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
        """Select pedagogy strategy with Sigma-style Socratic as the default.

        - mastery_socratic: Socratic questioning + mastery rubric + misconception tracking
        - retrieval_grounded_scaffold: evidence-augmented Socratic tutoring
        - diagnostic_scaffold: gap-focused diagnostic breakdown
        """
        retrieval_result = params.get("retrievalResult", {})
        documents = retrieval_result.get("documents", [])
        profile = params.get("profile", {})
        has_misconceptions = bool(profile.get("misconceptions") or [])
        if snapshot.knowledge_gaps and documents:
            return "retrieval_grounded_scaffold"
        if snapshot.knowledge_gaps or has_misconceptions:
            return "diagnostic_scaffold"
        return "mastery_socratic"

    async def _run_agent_core_loop(
        self,
        *,
        system_prompt: str,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        persisted_summary: dict[str, Any] | None,
    ) -> str:
        del snapshot
        user_query = str(
            params.get("query")
            or params.get("message")
            or params.get("rewrittenQuery")
            or params.get("structuredConversationSummary", {}).get("lastUserMessage")
            or "当前主题"
        )
        try:
            return await self._try_direct_chat(
                system_prompt=system_prompt,
                user_query=user_query,
                params=params,
                persisted_summary=persisted_summary,
            )
        except (AttributeError, Exception):
            pass
        return await self._run_with_agent_core_loop(
            system_prompt=system_prompt,
            user_query=user_query,
            params=params,
            persisted_summary=persisted_summary,
        )

    async def _try_direct_chat(
        self,
        *,
        system_prompt: str,
        user_query: str,
        params: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
    ) -> str:
        client = self.llm_client.client
        memory_data = self._tool_load_conversation_memory(
            tool_input={}, persisted_summary=persisted_summary,
        )
        context_data = self._tool_read_compacted_context(tool_input={}, params=params)
        evidence_data = self._tool_read_retrieval_evidence(tool_input={}, params=params)
        profile_data = self._tool_read_profile_context(tool_input={}, params=params)
        enriched_message = self._build_enriched_message(
            user_query=user_query,
            memory=memory_data,
            context=context_data,
            evidence=evidence_data,
            profile=profile_data,
        )
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enriched_message},
            ],
        )
        message = client.extract_message(response)
        return client.extract_content(message)

    async def _try_direct_chat_stream(
        self,
        *,
        system_prompt: str,
        params: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
    ):
        """Stream tokens from the LLM for real-time tutoring display."""
        client = self.llm_client.client
        user_query = str(
            params.get("query")
            or params.get("message")
            or params.get("rewrittenQuery")
            or params.get("structuredConversationSummary", {}).get("lastUserMessage")
            or "当前主题"
        )
        memory_data = self._tool_load_conversation_memory(
            tool_input={}, persisted_summary=persisted_summary,
        )
        context_data = self._tool_read_compacted_context(tool_input={}, params=params)
        evidence_data = self._tool_read_retrieval_evidence(tool_input={}, params=params)
        profile_data = self._tool_read_profile_context(tool_input={}, params=params)
        enriched_message = self._build_enriched_message(
            user_query=user_query,
            memory=memory_data,
            context=context_data,
            evidence=evidence_data,
            profile=profile_data,
        )

        # Accumulate tokens in batches of 3 for smoother UI updates
        batch: list[str] = []
        async for token in client.chat_completion_stream(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enriched_message},
            ],
        ):
            batch.append(token)
            if len(batch) >= 3:
                yield "".join(batch)
                batch.clear()
        if batch:
            yield "".join(batch)

    def _build_enriched_message(
        self,
        *,
        user_query: str,
        memory: dict[str, Any],
        context: dict[str, Any],
        evidence: dict[str, Any],
        profile: dict[str, Any],
    ) -> str:
        parts: list[str] = []
        topic_focus = memory.get("topicFocus") or context.get("topicFocus") or []
        learner_goal = memory.get("learnerGoal") or context.get("learnerGoal") or ""
        known_gaps = memory.get("knownGaps") or context.get("knownGaps") or []
        unresolved = memory.get("unresolvedQuestions") or context.get("unresolvedQuestions") or []
        # Sigma: surface recorded misconceptions for targeted counter-example design
        recorded_misconceptions = (
            profile.get("misconceptions")
            or memory.get("misconceptions")
            or []
        )
        mastered_concepts = profile.get("masteredConcepts") or memory.get("masteredConcepts") or []
        if profile:
            if profile.get("studentLevel"):
                parts.append(f"学生水平：{profile['studentLevel']}")
            if profile.get("learningPreference"):
                parts.append(f"讲解偏好：{profile['learningPreference']}")
            if profile.get("cognitiveStyle"):
                parts.append(f"认知风格：{profile['cognitiveStyle']}")
            preferred_resource_types = profile.get("preferredResourceTypes") or []
            if preferred_resource_types:
                parts.append(f"偏好资源类型：{', '.join(preferred_resource_types[:3])}")
        if topic_focus:
            parts.append(f"对话主题：{', '.join(topic_focus) if isinstance(topic_focus, list) else topic_focus}")
        if learner_goal:
            parts.append(f"学习目标：{learner_goal}")
        if known_gaps:
            parts.append(f"已知薄弱点：{', '.join(known_gaps)}")
        if unresolved:
            parts.append(f"未解决问题：{', '.join(unresolved)}")
        if recorded_misconceptions:
            parts.append("‼️ 已记录的错误概念（必须用反例瓦解，勿直接纠正）：")
            for mc in recorded_misconceptions[:5]:
                concept = mc.get("concept", "") if isinstance(mc, dict) else ""
                belief = mc.get("wrongBelief", "") if isinstance(mc, dict) else ""
                status = mc.get("status", "") if isinstance(mc, dict) else ""
                if concept and belief:
                    parts.append(f"  - [{concept}] {belief} (状态: {status or 'active'})")
        if mastered_concepts:
            concepts_str = ", ".join(
                mc.get("concept", "") if isinstance(mc, dict) else str(mc)
                for mc in mastered_concepts[:8]
            )
            if concepts_str:
                parts.append(f"已掌握概念（可用于交叉练习混入）：{concepts_str}")
        documents = evidence.get("documents", []) if isinstance(evidence.get("documents"), list) else []
        if documents:
            parts.append("检索到的知识来源：")
            for i, doc in enumerate(documents[:5], 1):
                title = str(doc.get("title") or "")
                snippet = str(doc.get("evidence") or doc.get("snippet") or "")[:200]
                parts.append(f"  {i}. {title}: {snippet}")
        parts.append(f"用户问题：{user_query}")
        parts.append(
            "请按 Sigma 教学流程处理："
            "1) 先用问题诊断学生的当前理解（不直接解释）；"
            "2) 根据回答决定下一步（见系统提示词中的映射表）；"
            "3) 如果涉及已记录的错误概念，设计反例让学生自己发现矛盾；"
            "4) 每 3-4 轮问答穿插一个需要用到已掌握概念的交叉练习；"
            "5) 以一个问题结尾，引导学生继续思考。"
        )
        return "\n\n".join(parts)

    async def _run_with_agent_core_loop(
        self,
        *,
        system_prompt: str,
        user_query: str,
        params: dict[str, Any],
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

    def _tool_read_profile_context(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        profile = params.get("profile", {})
        if not isinstance(profile, dict):
            return {}
        return {
            "studentLevel": profile.get("studentLevel") or profile.get("knowledgeFoundation"),
            "learningPreference": profile.get("learningPreference") or profile.get("preferredStyle"),
            "cognitiveStyle": profile.get("cognitiveStyle"),
            "preferredResourceTypes": profile.get("preferredResourceTypes", []),
        }
