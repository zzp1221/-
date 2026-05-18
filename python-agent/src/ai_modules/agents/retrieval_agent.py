"""混合检索 Agent 实现。"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
import logging
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import (
    RetrievalToolLLMClientFactory,
    RetrievalSummaryGenerator,
)
from src.ai_modules.models import ProgressPayload, ProgressSSEEvent, ResultChunkPayload, ResultChunkSSEEvent, SSEEvent
from src.ai_modules.prompts import build_retrieval_summary_prompt
from src.ai_modules.retrieval import HybridRetrievalService
from src.ai_modules.runtime import (
    RecoveryEngine,
    RecoveryFailureType,
    SystemSnapshot,
)

LOGGER = logging.getLogger(__name__)


class RetrievalAgent(PlaceholderAgent):
    """运行混合检索并将来源证据附加到参数中。"""

    def __init__(
        self,
        service: HybridRetrievalService | None = None,
        llm_client: Any | None = None,
        summary_generator: Any | None = None,
    ) -> None:
        super().__init__("Hybrid Retrieval Agent", "retrieving")
        self.service = service or HybridRetrievalService()
        self.llm_client = llm_client or RetrievalToolLLMClientFactory.create()
        self.summary_generator = summary_generator
        self.recovery_engine = RecoveryEngine()

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_retrieval_summary_prompt(snapshot)

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
        query = str(params.get("query") or params.get("rewrittenQuery") or "未提供查询")
        rewritten_query = str(params.get("rewrittenQuery") or query)
        keywords = list(params.get("keywords", []))
        web_search_enabled = self._web_search_enabled(params)

        retrieval_response, summary_text = await self._run_agent_core_loop(
            query=query,
            rewritten_query=rewritten_query,
            keywords=keywords,
            web_search_enabled=web_search_enabled,
            params=params,
            system_prompt=system_prompt,
        )
        params["retrievalResult"] = retrieval_response.model_dump(by_alias=True)

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=45,
                message=f"检索完成，命中 {len(retrieval_response.documents)} 个候选来源",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResultChunkPayload(
                text=(
                    f"检索查询: {retrieval_response.rewritten_query}；"
                    f"来源摘要: {summary_text}"
                )
            ),
        )

    async def _run_agent_core_loop(
        self,
        *,
        query: str,
        rewritten_query: str,
        keywords: list[str],
        web_search_enabled: bool,
        params: dict[str, Any],
        system_prompt: str,
    ):
        try:
            # 步骤 1: 获取原始检索结果（1 次数据库查询，带恢复机制）
            raw_result = await self._safe_get_raw_result(
                rewritten_query=rewritten_query,
                keywords=keywords,
                web_search_enabled=web_search_enabled,
            )
            params["retrievalRawResult"] = raw_result

            # 步骤 2: 分渠道结果（确定性操作，并行执行）
            grep_task = asyncio.to_thread(self.service.channel_results, raw_result, "grep")
            vector_task = asyncio.to_thread(self.service.channel_results, raw_result, "vector")
            graph_task = asyncio.to_thread(self.service.channel_results, raw_result, "graph")
            web_task = asyncio.to_thread(self.service.channel_results, raw_result, "web")
            grep_result, vector_result, graph_result, web_result = await asyncio.gather(
                grep_task, vector_task, graph_task, web_task,
            )
            params["grepRetrievalResult"] = {
                "priority": grep_result.get("priority", []) if isinstance(grep_result, dict) else [],
                "query": rewritten_query,
            }
            params["vectorRetrievalResult"] = {
                "results": list(vector_result) if not isinstance(vector_result, dict) else vector_result.get("results", []),
                "query": rewritten_query,
            }
            params["graphRetrievalResult"] = {
                "results": list(graph_result) if not isinstance(graph_result, dict) else graph_result.get("results", []),
                "query": rewritten_query,
            }
            params["webRetrievalResult"] = {
                "enabled": web_search_enabled,
                "results": list(web_result) if not isinstance(web_result, dict) else web_result.get("results", []),
                "query": rewritten_query,
            }

            # 步骤 3: RRF 融合（确定性操作）
            retrieval_response = self.service.build_response(
                query=query, rewritten_query=rewritten_query, keywords=keywords, raw_result=raw_result,
            )
            params["mergedRetrievalResult"] = retrieval_response

            # 步骤 4: 摘要来源（1 次 LLM 调用）
            summary_text = await self._safe_summarize(
                retrieval_response=retrieval_response, system_prompt=system_prompt,
            )
            params["retrievalSummaryText"] = summary_text
            return retrieval_response, summary_text

        except Exception:
            LOGGER.warning("Direct retrieval failed, falling back to service retrieval.", exc_info=True)

        retrieval_response = await asyncio.to_thread(
            self.service.retrieve,
            query=query,
            rewritten_query=rewritten_query,
            keywords=keywords,
            web_search_enabled=web_search_enabled,
        )
        summary_text = await self._safe_summarize(
            retrieval_response=retrieval_response, system_prompt=system_prompt,
        )
        return retrieval_response, summary_text

    async def _tool_grep_search(
        self,
        *,
        tool_input: dict[str, Any],
        rewritten_query: str,
        keywords: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        raw_result = await self._safe_get_raw_result(
            rewritten_query=rewritten_query,
            keywords=keywords,
        )
        params["retrievalRawResult"] = raw_result
        grep_result = self.service.channel_results(raw_result, "grep")
        payload = {
            "priority": grep_result.get("priority", []) if isinstance(grep_result, dict) else [],
            "query": rewritten_query,
        }
        params["grepRetrievalResult"] = payload
        return payload

    async def _tool_vector_search(
        self,
        *,
        tool_input: dict[str, Any],
        rewritten_query: str,
        keywords: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        raw_result = params.get("retrievalRawResult") or await self._safe_get_raw_result(
            rewritten_query=rewritten_query,
            keywords=keywords,
        )

        async def operation() -> dict[str, Any]:
            if params.get("forceVectorTimeout"):
                raise TimeoutError("vector db timeout")
            return {
                "results": list(self.service.channel_results(raw_result, "vector")),
                "query": rewritten_query,
            }

        async def fallback_operation() -> dict[str, Any]:
            payload = {"results": [], "query": rewritten_query, "degraded": True}
            await self.recovery_engine.recover_vector_db_timeout(query=rewritten_query)
            return payload

        payload = await self.recovery_engine.call_with_recovery(
            failure_type=RecoveryFailureType.VECTOR_DB_TIMEOUT,
            operation=operation,
            fallback_operation=fallback_operation,
        )
        params["vectorRetrievalResult"] = payload
        return payload

    async def _tool_graph_expand(
        self,
        *,
        tool_input: dict[str, Any],
        rewritten_query: str,
        keywords: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        raw_result = params.get("retrievalRawResult") or await self._safe_get_raw_result(
            rewritten_query=rewritten_query,
            keywords=keywords,
        )
        payload = {
            "results": list(self.service.channel_results(raw_result, "graph")),
            "query": rewritten_query,
        }
        params["graphRetrievalResult"] = payload
        return payload

    def _tool_rrf_merge(
        self,
        *,
        tool_input: dict[str, Any],
        query: str,
        rewritten_query: str,
        keywords: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        raw_result = params.get("retrievalRawResult") or self.service.fallback_raw_result(
            rewritten_query=rewritten_query,
            keywords=keywords,
        )
        retrieval_response = self.service.build_response(
            query=query,
            rewritten_query=rewritten_query,
            keywords=keywords,
            raw_result=raw_result,
        )
        params["mergedRetrievalResult"] = retrieval_response
        return retrieval_response.model_dump(by_alias=True)

    async def _tool_summarize_sources(
        self,
        *,
        tool_input: dict[str, Any],
        system_prompt: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        from src.ai_modules.models import RetrievalResponse

        retrieval_response = params.get("mergedRetrievalResult") or RetrievalResponse.model_validate(
            tool_input
        )
        summary = await self._safe_summarize(
            retrieval_response=retrieval_response,
            system_prompt=system_prompt,
        )
        payload = {
            "summaryText": summary,
            "retrievalResult": retrieval_response.model_dump(by_alias=True),
        }
        params["retrievalSummaryText"] = summary
        return payload

    async def _safe_get_raw_result(
        self,
        *,
        rewritten_query: str,
        keywords: list[str],
        web_search_enabled: bool = False,
    ) -> dict[str, Any]:
        async def operation() -> dict[str, Any]:
            return await asyncio.to_thread(
                self.service.retrieve_raw,
                rewritten_query,
                web_search_enabled=web_search_enabled,
            )

        async def fallback_operation() -> dict[str, Any]:
            fallback_payload = self.service.fallback_raw_result(
                rewritten_query=rewritten_query,
                keywords=keywords,
            )
            await self.recovery_engine.recover_retrieval_unavailable(
                query=rewritten_query,
                fallback_payload=fallback_payload,
            )
            return fallback_payload

        return await self.recovery_engine.call_with_recovery(
            failure_type=RecoveryFailureType.RETRIEVAL_UNAVAILABLE,
            operation=operation,
            fallback_operation=fallback_operation,
        )

    def _web_search_enabled(self, params: dict[str, Any]) -> bool:
        return bool(
            params.get("webSearchEnabled") is True
            or params.get("enableWebSearch") is True
            or params.get("tavilySearchEnabled") is True
        )

    async def _safe_summarize(
        self,
        *,
        retrieval_response,
        system_prompt: str,
    ) -> str:
        try:
            generator = self.summary_generator or RetrievalSummaryGenerator()
            summary = await generator.summarize(
                system_prompt=system_prompt,
                retrieval_response=retrieval_response,
            )
            if summary:
                return summary
        except Exception:
            LOGGER.warning(
                "Retrieval summary generation failed, falling back to source summary.",
                exc_info=True,
            )
        return retrieval_response.sources_summary
