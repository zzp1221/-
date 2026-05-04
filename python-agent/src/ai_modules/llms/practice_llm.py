"""Rule-based LLM adapters for Practice and Judge tool orchestration."""

from __future__ import annotations

from typing import Any

from src.ai_modules.runtime import AssistantTurn, ToolCall


class RuleBasedPracticeLLM:
    """Deterministic orchestrator for Practice Agent."""

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        del system_prompt, tools
        if not self._has_tool_result(messages, "generate_questions"):
            return AssistantTurn(
                content="先生成题目。",
                tool_calls=[ToolCall(id="call_generate_questions", name="generate_questions", input={})],
            )
        if not self._has_tool_result(messages, "validate_question"):
            questions = self._tool_output(messages, "generate_questions")
            return AssistantTurn(
                content="检查题目质量。",
                tool_calls=[ToolCall(id="call_validate_question", name="validate_question", input=questions)],
            )
        if not self._has_tool_result(messages, "format_question_batch"):
            validated = self._tool_output(messages, "validate_question")
            return AssistantTurn(
                content="输出标准题目批次。",
                tool_calls=[ToolCall(id="call_format_question_batch", name="format_question_batch", input=validated)],
            )
        final_output = self._tool_output(messages, "format_question_batch")
        return AssistantTurn(content=f"{final_output.get('title', '练习生成完成')} 已完成。")

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


class RuleBasedJudgeLLM:
    """Deterministic orchestrator for Judge Agent."""

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        del system_prompt, tools
        if not self._has_tool_result(messages, "grade_objective"):
            return AssistantTurn(
                content="先批改客观题。",
                tool_calls=[ToolCall(id="call_grade_objective", name="grade_objective", input={})],
            )
        if not self._has_tool_result(messages, "evaluate_subjective"):
            objective_result = self._tool_output(messages, "grade_objective")
            return AssistantTurn(
                content="继续评估主观题。",
                tool_calls=[ToolCall(id="call_evaluate_subjective", name="evaluate_subjective", input=objective_result)],
            )
        if not self._has_tool_result(messages, "generate_feedback"):
            judged = self._tool_output(messages, "evaluate_subjective")
            return AssistantTurn(
                content="生成综合反馈。",
                tool_calls=[ToolCall(id="call_generate_feedback", name="generate_feedback", input=judged)],
            )
        if not self._has_tool_result(messages, "save_practice_result"):
            feedback = self._tool_output(messages, "generate_feedback")
            return AssistantTurn(
                content="保存判题结果。",
                tool_calls=[ToolCall(id="call_save_practice_result", name="save_practice_result", input=feedback)],
            )
        saved = self._tool_output(messages, "save_practice_result")
        return AssistantTurn(content=saved.get("summary", "判题完成。"))

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
