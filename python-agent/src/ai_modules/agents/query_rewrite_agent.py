"""查询改写 Agent 实现。"""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import (
    QueryRewriteToolLLMClientFactory,
    QueryRewriteGenerator,
)
from src.ai_modules.models import (
    ProgressPayload,
    ProgressSSEEvent,
    QueryRewriteResult,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_query_rewrite_prompt
from src.ai_modules.retrieval import QueryRewriteService
from src.ai_modules.runtime import (
    SystemSnapshot,
)

LOGGER = logging.getLogger(__name__)


class QueryRewriteAgent(PlaceholderAgent):
    """在混合检索器运行前改写检索查询。"""

    def __init__(
        self,
        service: QueryRewriteService | None = None,
        llm_client: Any | None = None,
        llm_generator: Any | None = None,
    ) -> None:
        super().__init__("Query Rewrite Agent", "query_rewrite")
        self.service = service or QueryRewriteService()
        self.llm_client = llm_client or QueryRewriteToolLLMClientFactory.create()
        self.llm_generator = llm_generator

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_query_rewrite_prompt(snapshot)

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
        rewrite_result = await self._run_agent_core_loop(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
        )
        params["query"] = rewrite_result.original_query
        params["rewrittenQuery"] = rewrite_result.rewritten_query
        params["keywords"] = rewrite_result.keywords

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=20,
                message="查询改写完成",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(
                text=(
                    f"原始查询: {rewrite_result.original_query}；"
                    f"改写后: {rewrite_result.rewritten_query}；"
                    f"关键词: {', '.join(rewrite_result.keywords)}"
                )
            ),
        )

    async def _run_agent_core_loop(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ):
        # 步骤 1: 提取查询上下文（确定性操作）
        context = self._tool_extract_query_context(tool_input={}, params=params)
        original_query = context["originalQuery"]

        # 步骤 2: 通过 LLM 改写查询（1 次 LLM 调用）
        try:
            rewritten_payload = await self._tool_rewrite_query(
                tool_input={}, params=params, snapshot=snapshot, system_prompt=system_prompt,
            )
        except Exception:
            LOGGER.warning("LLM query rewrite failed, falling back to direct rewrite.", exc_info=True)
            return self.service.rewrite(params)

        # 步骤 3: 验证结果（确定性操作）
        try:
            return self._tool_finalize_rewrite(rewritten_payload)
        except Exception:
            LOGGER.warning("Query rewrite validation failed, falling back.", exc_info=True)
            return self.service.rewrite(params)

    def _tool_extract_query_context(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        learning_context = params.get("learningContext", {})
        original_query = self.service.extract_query(params)
        context = {
            "originalQuery": original_query,
            "learningContext": learning_context,
            "course": learning_context.get("course"),
            "chapter": learning_context.get("chapter"),
        }
        params["queryRewriteContext"] = context
        return context

    async def _tool_rewrite_query(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        del snapshot
        context = params.get("queryRewriteContext") or tool_input
        original_query = str(context.get("originalQuery") or self.service.extract_query(params))
        try:
            generator = self.llm_generator or QueryRewriteGenerator()
            rewritten = await generator.rewrite(
                system_prompt=system_prompt,
                original_query=original_query,
                learning_context=params.get("learningContext", {}),
            )
            payload = rewritten.model_dump(by_alias=True)
        except Exception:
            payload = self.service.rewrite(params).model_dump(by_alias=True)
        params["rewrittenQueryPayload"] = payload
        return payload

    def _tool_finalize_rewrite(self, tool_input: dict[str, Any]) -> QueryRewriteResult:
        return QueryRewriteResult.model_validate(tool_input)
