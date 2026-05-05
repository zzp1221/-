"""Rule-based tool orchestration for routing and generation workflows."""

from __future__ import annotations

from typing import Any

from src.ai_modules.config import get_settings
from src.ai_modules.llms.agent_models import create_tool_calling_llm
from src.ai_modules.runtime import AssistantTurn, ToolCall


class _BaseSequenceLLM:
    """Drive AgentCoreLoop by executing tools in a deterministic sequence."""

    tool_sequence: tuple[str, ...] = ()

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        del system_prompt
        available_tools = {
            str(tool.get("function", {}).get("name"))
            for tool in tools
            if isinstance(tool, dict)
        }
        for tool_name in self.tool_sequence:
            if tool_name not in available_tools or self._has_tool_result(messages, tool_name):
                continue
            return AssistantTurn(
                content=f"调用 {tool_name} 完成当前步骤。",
                tool_calls=[
                    ToolCall(
                        id=f"call_{tool_name}",
                        name=tool_name,
                        input=self._build_tool_input(tool_name=tool_name, messages=messages),
                    )
                ],
            )

        latest = self._latest_tool_output(messages)
        if isinstance(latest, dict):
            summary_text = latest.get("summaryText") or latest.get("summary")
            if summary_text:
                return AssistantTurn(content=str(summary_text))
        return AssistantTurn(content="流程完成。")

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        del tool_name, messages
        return {}

    def _has_tool_result(self, messages: list[dict[str, Any]], tool_name: str) -> bool:
        return any(
            message.get("role") == "tool" and message.get("name") == tool_name
            for message in messages
        )

    def _tool_output(self, messages: list[dict[str, Any]], tool_name: str) -> dict[str, Any]:
        for message in reversed(messages):
            if message.get("role") == "tool" and message.get("name") == tool_name:
                content = message.get("content", {})
                return content if isinstance(content, dict) else {"raw": content}
        return {}

    def _latest_tool_output(self, messages: list[dict[str, Any]]) -> Any:
        for message in reversed(messages):
            if message.get("role") == "tool":
                return message.get("content")
        return {}


class RuleBasedQueryRewriteLLM(_BaseSequenceLLM):
    tool_sequence = ("extract_query_context", "rewrite_query", "finalize_rewrite")

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if tool_name in {"rewrite_query", "finalize_rewrite"}:
            return self._latest_tool_output(messages) or {}
        return {}


class RuleBasedRetrievalLLM(_BaseSequenceLLM):
    tool_sequence = (
        "grep_search",
        "vector_search",
        "graph_expand",
        "rrf_merge",
        "summarize_sources",
    )

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if tool_name == "rrf_merge":
            return {
                "grep": self._tool_output(messages, "grep_search"),
                "vector": self._tool_output(messages, "vector_search"),
                "graph": self._tool_output(messages, "graph_expand"),
            }
        if tool_name == "summarize_sources":
            return self._tool_output(messages, "rrf_merge")
        return {}


class RuleBasedGenerationLLM(_BaseSequenceLLM):
    tool_sequence = (
        "generate_outline",
        "expand_content",
        "review_content",
        "format_output",
    )

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if tool_name in {"expand_content", "review_content", "format_output"}:
            return self._latest_tool_output(messages) or {}
        return {}


class QueryRewriteToolLLMClientFactory:
    @staticmethod
    def create() -> Any:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("query_rewrite_llm")
        if settings.provider_ready(provider_name):
            model_name = settings.resolve_component_model(
                "query_rewrite_llm",
                default_logical_model="fast_model",
                provider_name=provider_name,
            )
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedQueryRewriteLLM()


class RetrievalToolLLMClientFactory:
    @staticmethod
    def create() -> Any:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("retrieval_llm")
        if settings.provider_ready(provider_name):
            model_name = settings.resolve_component_model(
                "retrieval_llm",
                default_logical_model="fast_model",
                provider_name=provider_name,
            )
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedRetrievalLLM()


class GenerationToolLLMClientFactory:
    @staticmethod
    def create() -> Any:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("generation_llm")
        if settings.provider_ready(provider_name):
            model_name = settings.resolve_component_model(
                "generation_llm",
                default_logical_model="main_chat_model",
                provider_name=provider_name,
            )
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedGenerationLLM()
