"""Pre/Post tool hook chain primitives."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class HookResult(BaseModel):
    """Hook execution result."""

    denied: bool = False
    reason: str | None = None
    updated_input: dict[str, Any] | None = Field(default=None, alias="updatedInput")


class Hook(Protocol):
    """Hook contract for tool execution interception."""

    async def pre_tool_use(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> HookResult: ...

    async def post_tool_use(
        self,
        tool_name: str,
        tool_output: Any,
    ) -> HookResult: ...


class HookChain:
    """Sequential hook runner around tool execution."""

    def __init__(
        self,
        pre_hooks: list[Hook] | None = None,
        post_hooks: list[Hook] | None = None,
    ) -> None:
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    async def run_pre_hooks(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> HookResult:
        current_input = dict(tool_input)

        for hook in self.pre_hooks:
            result = await hook.pre_tool_use(tool_name, current_input)
            if result.updated_input is not None:
                current_input = result.updated_input
            if result.denied:
                return HookResult(
                    denied=True,
                    reason=result.reason,
                    updatedInput=current_input,
                )

        return HookResult(updatedInput=current_input)

    async def run_post_hooks(
        self,
        tool_name: str,
        tool_output: Any,
    ) -> HookResult:
        for hook in self.post_hooks:
            result = await hook.post_tool_use(tool_name, tool_output)
            if result.denied:
                return result
        return HookResult()
