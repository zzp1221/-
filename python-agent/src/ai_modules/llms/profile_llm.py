"""Rule-based LLM adapter for Profile Agent tool orchestration."""

from __future__ import annotations

from typing import Any

from src.ai_modules.runtime import AssistantTurn, ToolCall


class RuleBasedProfileLLM:
    """Deterministic orchestrator that exercises the Profile Agent tool chain."""

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        del system_prompt, tools
        if not self._has_tool_result(messages, "read_profile"):
            user_message = self._last_user_message(messages)
            return AssistantTurn(
                content="先读取现有画像。",
                tool_calls=[
                    ToolCall(
                        id="call_read_profile",
                        name="read_profile",
                        input={"userId": user_message or "unknown-user"},
                    )
                ],
            )

        if not self._has_tool_result(messages, "analyze_dialogue"):
            return AssistantTurn(
                content="继续分析对话，抽取画像维度。",
                tool_calls=[
                    ToolCall(
                        id="call_analyze_dialogue",
                        name="analyze_dialogue",
                        input={},
                    )
                ],
            )

        if not self._has_tool_result(messages, "update_profile"):
            analyze_output = self._tool_output(messages, "analyze_dialogue")
            return AssistantTurn(
                content="将画像维度写回存储。",
                tool_calls=[
                    ToolCall(
                        id="call_update_profile",
                        name="update_profile",
                        input=analyze_output,
                    )
                ],
            )

        update_output = self._tool_output(messages, "update_profile")
        summary = update_output.get("summaryText", "画像更新完成。")
        version = update_output.get("version")
        return AssistantTurn(
            content=f"{summary} 当前画像版本: {version}。"
        )

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

    def _last_user_message(self, messages: list[dict[str, Any]]) -> str | None:
        for message in reversed(messages):
            if message.get("role") == "user":
                return str(message.get("content", ""))
        return None
