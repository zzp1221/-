"""Tool-calling LLM adapters used by evaluation and path-planning agents."""

from __future__ import annotations

from typing import Any

from src.ai_modules.config import get_settings
from src.ai_modules.llms.agent_models import create_tool_calling_llm
from src.ai_modules.llms.bailian_compatible import BailianCompatibleToolCallingLLM
from src.ai_modules.runtime import AssistantTurn, ToolCall


class RuleBasedPlanningLLM:
    """Deterministic fallback LLM that preserves the planned tool sequence."""

    _TOOL_SEQUENCE = (
        "aggregate_behavior",
        "generate_report",
        "analyze_profile",
        "generate_path",
        "update_path_plan",
    )

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
        executed_tools = [
            str(message.get("name"))
            for message in messages
            if message.get("role") == "tool"
        ]

        for tool_name in self._TOOL_SEQUENCE:
            if tool_name in available_tools and tool_name not in executed_tools:
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

        return AssistantTurn(content=self._compose_final_text(messages))

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if tool_name in {"generate_report", "generate_path", "update_path_plan"}:
            latest_tool_content = self._latest_tool_content(messages)
            return latest_tool_content if isinstance(latest_tool_content, dict) else {}
        return {}

    def _latest_tool_content(self, messages: list[dict[str, Any]]) -> Any:
        for message in reversed(messages):
            if message.get("role") == "tool":
                return message.get("content")
        return {}

    def _compose_final_text(self, messages: list[dict[str, Any]]) -> str:
        latest_tool_content = self._latest_tool_content(messages)
        if isinstance(latest_tool_content, dict):
            learning_path = latest_tool_content.get("learningPath")
            if isinstance(learning_path, dict) and learning_path.get("summaryText"):
                return str(learning_path["summaryText"])
            if latest_tool_content.get("summaryText"):
                return str(latest_tool_content["summaryText"])
        return "已完成评估与路径规划。"


class PlanningLLMClientFactory:
    """Create the planning LLM client with Bailian primary and rule fallback."""

    @staticmethod
    def create() -> Any:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("planning_llm")
        if settings.provider_ready(provider_name):
            model_name = settings.resolve_component_model(
                "planning_llm",
                default_logical_model="reasoning_model",
                provider_name=provider_name,
            )
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedPlanningLLM()
