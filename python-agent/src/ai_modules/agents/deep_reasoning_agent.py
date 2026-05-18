"""用于多步辅导回答的深度推理 Agent。"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.tutor_agent import TutorAgent
from src.ai_modules.models import (
    DialogState,
    ProgressPayload,
    ProgressSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.runtime import (
    AgentCoreLoop,
    MaxIterationsExceededError,
    PermissionLevel,
    RecoveryEngine,
    StructuredConversationSummary,
    SystemSnapshot,
    ToolRegistry,
)

LOGGER = logging.getLogger(__name__)


class DeepReasoningAgent(TutorAgent):
    """运行有限的分析 -> 推理 -> 批判 -> 最终回答流水线。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent_name = "Deep Reasoning Agent"
        self.stage_name = "deep_reasoning"

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
        user_query = self._resolve_user_query(params)
        persisted_summary = await self._load_persisted_summary(
            conversation_id=self._conversation_id(params, task_id),
            user_id=params.get("userId"),
        )
        compaction_result = self.compactor.compact(
            conversation,
            previous_summary=self._build_previous_summary(persisted_summary),
        )
        params["compactedConversation"] = compaction_result.compacted_messages
        params["structuredConversationSummary"] = compaction_result.structured_summary.model_dump(
            by_alias=True
        )
        params["conversationSummary"] = compaction_result.summary
        recent_dialogue = self._build_recent_dialogue_context(
            conversation=conversation,
            user_query=user_query,
        )
        input_mode = self._classify_input_mode(
            user_query=user_query,
            recent_dialogue=recent_dialogue,
        )
        recent_dialogue["inputMode"] = input_mode
        params["recentDialogueContext"] = recent_dialogue
        params["inputMode"] = input_mode

        if compaction_result.was_compacted:
            await self._upsert_summary(
                params=params,
                task_id=task_id,
                structured_summary=compaction_result.structured_summary.model_dump(by_alias=True),
            )

        dialog_state = DialogState(
            conversationId=self._conversation_id(params, task_id),
            turnId=f"{task_id}-deep-turn",
            pedagogyStrategy="deep_reasoning_pipeline",
            nextAction="final_answer",
        )

        artifacts: dict[str, str] = {}
        current_seq = seq
        steps = [
            ("analysis", "问题分析", 35),
            ("reasoning", "分步推理", 55),
            ("critique", "自我批判", 75),
            ("final", "最终回答", 92),
        ]

        for step_key, label, percent in steps:
            yield ProgressSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=current_seq,
                payload=ProgressPayload(
                    stage="tutoring" if step_key == "final" else f"deep_{step_key}",
                    percent=percent,
                    message=f"深度思考：{label}",
                ),
                dialogState=dialog_state,
            )
            current_seq += 1
            artifacts[step_key] = await self._run_reasoning_step(
                step_key=step_key,
                label=label,
                base_system_prompt=system_prompt,
                user_query=user_query,
                params=params,
                persisted_summary=persisted_summary,
                artifacts=artifacts,
            )

        final_text = artifacts.get("final") or artifacts.get("reasoning") or "我已经完成深度思考，但暂时没有生成有效回答。"
        params["deepReasoningArtifacts"] = artifacts
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=current_seq,
            payload=ResultChunkPayload(text=final_text),
            dialogState=dialog_state,
        )

    async def _run_reasoning_step(
        self,
        *,
        step_key: str,
        label: str,
        base_system_prompt: str,
        user_query: str,
        params: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
        artifacts: dict[str, str],
    ) -> str:
        tool_registry = self._build_deep_reasoning_tools(
            params=params,
            persisted_summary=persisted_summary,
            artifacts=artifacts,
        )
        core_loop = AgentCoreLoop(
            llm_client=self.llm_client,
            tool_registry=tool_registry,
            recovery_engine=RecoveryEngine(),
            max_iterations=4,
            agent_level=PermissionLevel.READ_ONLY,
        )
        step_system_prompt = self._build_step_system_prompt(
            step_key=step_key,
            label=label,
            base_system_prompt=base_system_prompt,
        )
        step_request = self._build_step_request(
            step_key=step_key,
            user_query=user_query,
            params=params,
            persisted_summary=persisted_summary,
            artifacts=artifacts,
        )
        try:
            result = await core_loop.run(
                system_prompt=step_system_prompt,
                messages=[{"role": "user", "content": step_request}],
            )
            if result.final_text.strip():
                return result.final_text.strip()
        except MaxIterationsExceededError:
            LOGGER.warning("Deep reasoning step exceeded tool loop limit; falling back to direct completion step=%s", step_key)
            return await self._run_direct_reasoning_step(
                system_prompt=step_system_prompt,
                user_query=step_request,
                step_key=step_key,
                artifacts=artifacts,
            )
        return self._build_step_fallback(step_key=step_key, user_query=user_query, artifacts=artifacts)

    async def _run_direct_reasoning_step(
        self,
        *,
        system_prompt: str,
        user_query: str,
        step_key: str,
        artifacts: dict[str, str],
    ) -> str:
        client = getattr(self.llm_client, "client", None)
        if client is None or not hasattr(client, "chat_completion"):
            return self._build_step_fallback(
                step_key=step_key,
                user_query=user_query,
                artifacts=artifacts,
            )
        try:
            response = await client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            "工具循环已达到上限。请不要再调用工具，"
                            "直接完成当前深度思考步骤。\n\n"
                            f"{user_query}"
                        ),
                    },
                ],
                temperature=0.2,
                max_tokens=1400,
            )
            message = client.extract_message(response)
            content = client.extract_content(message).strip()
            if content:
                return content
        except Exception as exc:
            LOGGER.warning("Direct deep reasoning fallback failed step=%s: %s", step_key, exc)
        return self._build_step_fallback(step_key=step_key, user_query=user_query, artifacts=artifacts)

    def _build_step_fallback(
        self,
        *,
        step_key: str,
        user_query: str,
        artifacts: dict[str, str],
    ) -> str:
        if step_key == "analysis":
            return f"问题核心：{user_query.strip() or '当前问题'}。需要结合概念定义、对比维度和学习场景来回答。"
        if step_key == "reasoning":
            return "推理路径：先明确比较对象，再从语法生态、性能、并发、工程复杂度和适用场景逐项分析。"
        if step_key == "critique":
            return "检查结论：避免绝对化比较，需要说明不同语言优势依赖具体项目、团队和业务场景。"
        previous = artifacts.get("reasoning") or artifacts.get("analysis") or user_query
        return f"可以这样看：\n\n{previous}"

    def _build_deep_reasoning_tools(
        self,
        *,
        params: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
        artifacts: dict[str, str],
    ) -> ToolRegistry:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="load_conversation_memory",
            fn=lambda tool_input: self._tool_load_conversation_memory(
                tool_input=tool_input,
                persisted_summary=persisted_summary,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="加载最新的结构化对话摘要。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_compacted_context",
            fn=lambda tool_input: self._tool_read_compacted_context(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="读取压缩后的对话上下文。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_retrieval_evidence",
            fn=lambda tool_input: self._tool_read_retrieval_evidence(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="读取回答的检索证据。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_profile_context",
            fn=lambda tool_input: self._tool_read_profile_context(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="读取学习者画像上下文。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_image_analysis_context",
            fn=lambda tool_input: self._tool_read_image_analysis_context(
                tool_input=tool_input,
                params=params,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="读取上传图片的分析上下文。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        tool_registry.register(
            name="read_deep_reasoning_artifacts",
            fn=lambda tool_input: self._tool_read_deep_reasoning_artifacts(
                tool_input=tool_input,
                artifacts=artifacts,
            ),
            permission_level=PermissionLevel.READ_ONLY,
            description="读取之前深度推理步骤产生的输出。",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
        )
        return tool_registry

    def _build_step_system_prompt(
        self,
        *,
        step_key: str,
        label: str,
        base_system_prompt: str,
    ) -> str:
        step_prompts = {
            "analysis": "你正在执行深度思考的第一步：问题分析。识别用户真正要解决的问题、上下文、限制条件和需要补充的关键概念。",
            "reasoning": "你正在执行深度思考的第二步：分步推理。基于问题分析、检索证据、学习画像和对话上下文，形成清晰的解题或讲解路径。",
            "critique": "你正在执行深度思考的第三步：自我批判。检查前一步推理是否跳步、是否误用证据、是否遗漏用户真实意图，并给出修正意见。",
            "final": "你正在执行深度思考的最后一步：最终回答。只输出给用户看的自然中文回答，不暴露内部推理链、工具调用或自我批判过程。",
        }
        return "\n\n".join(
            [
                base_system_prompt,
                f"# Deep Reasoning Step: {label}",
                step_prompts.get(step_key, step_prompts["final"]),
                "回答要贴合学习场景；复杂问题可以分层说明，但不要输出内部 chain-of-thought。",
            ]
        )

    def _build_step_request(
        self,
        *,
        step_key: str,
        user_query: str,
        params: dict[str, Any],
        persisted_summary: dict[str, Any] | None,
        artifacts: dict[str, str],
    ) -> str:
        enriched_message = self._build_enriched_message(
            user_query=user_query,
            memory=self._tool_load_conversation_memory(
                tool_input={},
                persisted_summary=persisted_summary,
            ),
            context=self._tool_read_compacted_context(tool_input={}, params=params),
            evidence=self._tool_read_retrieval_evidence(tool_input={}, params=params),
            profile=self._tool_read_profile_context(tool_input={}, params=params),
            image_analysis=self._tool_read_image_analysis_context(tool_input={}, params=params),
            recent_dialogue=self._tool_read_recent_dialogue_context(tool_input={}, params=params),
            input_mode=self._resolve_input_mode(
                params=params,
                recent_dialogue=self._tool_read_recent_dialogue_context(tool_input={}, params=params),
            ),
        )
        return "\n\n".join(
            [
                f"用户问题：{user_query}",
                f"当前步骤：{step_key}",
                "# 运行时上下文",
                enriched_message,
                "# 已完成步骤",
                self._format_artifacts(artifacts),
            ]
        )

    def _tool_read_deep_reasoning_artifacts(
        self,
        *,
        tool_input: dict[str, Any],
        artifacts: dict[str, str],
    ) -> dict[str, str]:
        del tool_input
        return dict(artifacts)

    def _format_artifacts(self, artifacts: dict[str, str]) -> str:
        if not artifacts:
            return "暂无。"
        return "\n\n".join(
            f"## {key}\n{value}"
            for key, value in artifacts.items()
            if value
        )

    def _build_previous_summary(
        self,
        persisted_summary: dict[str, Any] | None,
    ) -> StructuredConversationSummary | None:
        return super()._build_previous_summary(persisted_summary)
