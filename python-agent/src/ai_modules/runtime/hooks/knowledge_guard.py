"""Knowledge-first hook for generation tools."""

from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from src.ai_modules.runtime.hook_chain import HookResult


RetrievalProvider = Callable[[dict[str, Any]], Any] | Callable[[dict[str, Any]], Awaitable[Any]]


class KnowledgeGuardHook:
    """Inject retrieved evidence before generation tools are allowed to run."""

    def __init__(self, retrieval_provider: RetrievalProvider) -> None:
        self.retrieval_provider = retrieval_provider

    async def pre_tool_use(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> HookResult:
        if not tool_name.startswith("generate_"):
            return HookResult(updatedInput=tool_input)

        retrieval_result = self.retrieval_provider(tool_input)
        if inspect.isawaitable(retrieval_result):
            retrieval_result = await retrieval_result

        if not retrieval_result:
            return HookResult(
                denied=True,
                reason="无相关知识依据",
                updatedInput=tool_input,
            )

        updated_input = dict(tool_input)
        updated_input["retrieved_context"] = retrieval_result
        return HookResult(updatedInput=updated_input)

    async def post_tool_use(
        self,
        tool_name: str,
        tool_output: Any,
    ) -> HookResult:
        del tool_name, tool_output
        return HookResult()
