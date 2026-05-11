"""Hybrid retrieval agent implementation."""

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
    """Run hybrid retrieval and attach source evidence to params."""

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

        retrieval_response, summary_text = await self._run_agent_core_loop(
            query=query,
            rewritten_query=rewritten_query,
            keywords=keywords,
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
        params: dict[str, Any],
        system_prompt: str,
    ):
        try:
            # Step 1: Get raw retrieval results (1 DB query, with recovery)
            raw_result = await self._safe_get_raw_result(
                rewritten_query=rewritten_query, keywords=keywords,
            )
            params["retrievalRawResult"] = raw_result

            # Step 2: Channel results (deterministic, parallel)
            grep_task = asyncio.to_thread(self.service.channel_results, raw_result, "grep")
            vector_task = asyncio.to_thread(self.service.channel_results, raw_result, "vector")
            graph_task = asyncio.to_thread(self.service.channel_results, raw_result, "graph")
            grep_result, vector_result, graph_result = await asyncio.gather(
                grep_task, vector_task, graph_task,
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

            # Step 3: RRF merge (deterministic)
            retrieval_response = self.service.build_response(
                query=query, rewritten_query=rewritten_query, keywords=keywords, raw_result=raw_result,
            )
            params["mergedRetrievalResult"] = retrieval_response

            # Step 4: Summarize sources (1 LLM call)
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
    ) -> dict[str, Any]:
        async def operation() -> dict[str, Any]:
            return await asyncio.to_thread(self.service.retrieve_raw, rewritten_query)

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
