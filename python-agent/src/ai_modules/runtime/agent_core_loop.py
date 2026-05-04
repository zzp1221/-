"""Generic multi-step agent execution loop."""

from __future__ import annotations

import json
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.config import get_settings
from src.ai_modules.runtime.recovery_engine import (
    LLMRateLimitError,
    RecoveryFailureType,
)
from src.ai_modules.runtime.tool_registry import ToolRegistry


class ToolCall(BaseModel):
    """A tool invocation requested by the model."""

    id: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)


class AssistantTurn(BaseModel):
    """Structured model turn returned by the LLM adapter."""

    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    def as_message(self) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": self.content,
            "tool_calls": [call.model_dump() for call in self.tool_calls],
        }


class ToolExecutionResult(BaseModel):
    """Normalized tool output stored in the conversation state."""

    tool_call_id: str = Field(alias="toolCallId")
    tool_name: str = Field(alias="toolName")
    output: Any
    is_error: bool = Field(default=False, alias="isError")

    model_config = ConfigDict(populate_by_name=True)

    def as_message(self) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "name": self.tool_name,
            "content": self.output,
            "is_error": self.is_error,
        }


class AgentLoopResult(BaseModel):
    """Final result of a completed agent loop."""

    final_text: str = Field(alias="finalText")
    iterations: int
    messages: list[dict[str, Any]]
    tool_results: list[ToolExecutionResult] = Field(alias="toolResults")

    model_config = ConfigDict(populate_by_name=True)


class SupportsToolCallingLLM(Protocol):
    """LLM protocol expected by AgentCoreLoop."""

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn: ...


class MaxIterationsExceededError(RuntimeError):
    """Raised when the agent loop exceeds the configured iteration limit."""


class AgentCoreLoop:
    """Run a tool-aware LLM loop until a final answer is produced."""

    def __init__(
        self,
        llm_client: SupportsToolCallingLLM,
        tool_registry: ToolRegistry,
        permission_policy: Any | None = None,
        hook_chain: Any | None = None,
        recovery_engine: Any | None = None,
        max_iterations: int = 10,
        agent_level: int = 5,
        max_tool_content_chars: int | None = None,
        max_tool_list_items: int | None = None,
        max_tool_dict_items: int | None = None,
    ) -> None:
        settings = get_settings()
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.permission_policy = permission_policy
        self.hook_chain = hook_chain
        self.recovery_engine = recovery_engine
        self.max_iterations = max_iterations
        self.agent_level = agent_level
        self.max_tool_content_chars = (
            max_tool_content_chars
            if max_tool_content_chars is not None
            else settings.llm_tool_content_max_string_chars
        )
        self.max_tool_list_items = (
            max_tool_list_items
            if max_tool_list_items is not None
            else settings.llm_tool_content_max_list_items
        )
        self.max_tool_dict_items = (
            max_tool_dict_items
            if max_tool_dict_items is not None
            else settings.llm_tool_content_max_dict_items
        )

    async def run(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
    ) -> AgentLoopResult:
        working_messages = [message.copy() for message in messages]
        tool_results: list[ToolExecutionResult] = []
        called_tool_names: set[str] = set()
        all_registered_tools = set(self.tool_registry._tools.keys())
        tool_schemas = self.tool_registry.list_tool_schemas(self.agent_level)

        for iteration in range(1, self.max_iterations + 1):
            async def llm_operation() -> AssistantTurn:
                return await self.llm_client.complete(
                    system_prompt=system_prompt,
                    messages=self._prepare_messages_for_llm(working_messages),
                    tools=tool_schemas,
                )

            if self.recovery_engine is None:
                assistant_turn = await llm_operation()
            else:
                try:
                    assistant_turn = await self.recovery_engine.call_with_recovery(
                        failure_type=RecoveryFailureType.LLM_API_TIMEOUT,
                        operation=llm_operation,
                    )
                except TimeoutError:
                    raise
                except LLMRateLimitError:
                    assistant_turn = await self.recovery_engine.call_with_recovery(
                        failure_type=RecoveryFailureType.LLM_API_RATE_LIMIT,
                        operation=llm_operation,
                    )
            working_messages.append(assistant_turn.as_message())

            if not assistant_turn.tool_calls:
                return AgentLoopResult(
                    finalText=assistant_turn.content,
                    iterations=iteration,
                    messages=working_messages,
                    toolResults=tool_results,
                )

            # Early termination: if all registered tools have been called and
            # the LLM is repeating tool calls, force stop with the last result.
            current_call_names = {tc.name for tc in assistant_turn.tool_calls}
            if len(all_registered_tools) > 1 and all_registered_tools.issubset(called_tool_names):
                if current_call_names.issubset(called_tool_names):
                    last_output = tool_results[-1].output if tool_results else assistant_turn.content
                    final_text = (
                        json.dumps(last_output, ensure_ascii=False)
                        if isinstance(last_output, dict)
                        else str(last_output)
                    )
                    return AgentLoopResult(
                        finalText=final_text,
                        iterations=iteration,
                        messages=working_messages,
                        toolResults=tool_results,
                    )

            for tool_call in assistant_turn.tool_calls:
                tool_definition = self.tool_registry.get(tool_call.name)
                effective_input = dict(tool_call.input)

                if self.hook_chain is not None:
                    hook_result = await self.hook_chain.run_pre_hooks(
                        tool_call.name,
                        effective_input,
                    )
                    if hook_result.updated_input is not None:
                        effective_input = hook_result.updated_input
                    if hook_result.denied:
                        result = ToolExecutionResult(
                            toolCallId=tool_call.id,
                            toolName=tool_call.name,
                            output=hook_result.reason or "denied by hook",
                            isError=True,
                        )
                        tool_results.append(result)
                        working_messages.append(result.as_message())
                        continue

                if self.permission_policy is not None:
                    permission_decision = self.permission_policy.authorize(
                        tool_name=tool_call.name,
                        tool_input=effective_input,
                        agent_level=self.agent_level,
                        tool_required_level=tool_definition.permission_level,
                    )
                else:
                    permission_decision = None

                if permission_decision is not None and not permission_decision.allowed:
                    result = ToolExecutionResult(
                        toolCallId=tool_call.id,
                        toolName=tool_call.name,
                        output=permission_decision.reason,
                        isError=True,
                    )
                elif tool_definition.permission_level > self.agent_level:
                    result = ToolExecutionResult(
                        toolCallId=tool_call.id,
                        toolName=tool_call.name,
                        output="denied by level",
                        isError=True,
                    )
                else:
                    try:
                        output = await self.tool_registry.execute(
                            tool_call.name,
                            effective_input,
                        )
                        if self.hook_chain is not None:
                            post_hook_result = await self.hook_chain.run_post_hooks(
                                tool_call.name,
                                output,
                            )
                            if post_hook_result.denied:
                                raise RuntimeError(
                                    post_hook_result.reason or "denied by post hook"
                                )
                        result = ToolExecutionResult(
                            toolCallId=tool_call.id,
                            toolName=tool_call.name,
                            output=output,
                            isError=False,
                        )
                    except Exception as exc:  # pragma: no cover - defensive branch
                        if self.recovery_engine is not None:
                            recovered_output = (
                                await self.recovery_engine.recover_tool_execution_error(
                                    tool_name=tool_call.name,
                                    error=exc,
                                )
                            )
                            result = ToolExecutionResult(
                                toolCallId=tool_call.id,
                                toolName=tool_call.name,
                                output=recovered_output,
                                isError=True,
                            )
                            tool_results.append(result)
                            working_messages.append(result.as_message())
                            continue
                        result = ToolExecutionResult(
                            toolCallId=tool_call.id,
                            toolName=tool_call.name,
                            output=str(exc),
                            isError=True,
                        )

                tool_results.append(result)
                working_messages.append(result.as_message())
                called_tool_names.add(tool_call.name)

        raise MaxIterationsExceededError(
            f"Agent loop exceeded {self.max_iterations} iterations"
        )

    def _prepare_messages_for_llm(
        self,
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        prepared_messages: list[dict[str, Any]] = []
        for message in messages:
            if message.get("role") != "tool":
                prepared_messages.append(message.copy())
                continue
            tool_message = message.copy()
            tool_message["content"] = self._compact_tool_content(tool_message.get("content"))
            prepared_messages.append(tool_message)
        return prepared_messages

    def _compact_tool_content(self, value: Any, *, depth: int = 0) -> Any:
        if isinstance(value, str):
            if len(value) <= self.max_tool_content_chars:
                return value
            return value[: self.max_tool_content_chars] + "...[truncated]"
        if isinstance(value, list):
            compacted = [
                self._compact_tool_content(item, depth=depth + 1)
                for item in value[: self.max_tool_list_items]
            ]
            if len(value) > self.max_tool_list_items:
                compacted.append({"_truncated_items": len(value) - self.max_tool_list_items})
            return compacted
        if isinstance(value, dict):
            compacted: dict[str, Any] = {}
            items = list(value.items())
            for key, item_value in items[: self.max_tool_dict_items]:
                compacted[str(key)] = self._compact_tool_content(item_value, depth=depth + 1)
            if len(items) > self.max_tool_dict_items:
                compacted["_truncated_keys"] = len(items) - self.max_tool_dict_items
            if depth > 2 and compacted:
                compacted["_compacted"] = True
            return compacted
        return value
