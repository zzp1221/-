"""Query rewrite and hybrid retrieval services."""

from __future__ import annotations

import re
from typing import Any, Protocol

from src.ai_modules.config import get_settings
from src.ai_modules.models import (
    QueryRewriteResult,
    RetrievalDocument,
    RetrievalResponse,
)
from src.ai_modules.runtime.ttl_cache import InMemoryTTLCache, stable_cache_key


_RETRIEVAL_RESULT_CACHE = InMemoryTTLCache()


class SupportsHybridRetrieve(Protocol):
    def retrieve(self, query: str) -> dict[str, Any]: ...


class LegacyHybridRetrieverAdapter:
    """Adapter around the legacy retrieval implementation in `python-agent/retrieval`."""

    def __init__(self) -> None:
        settings = get_settings()
        self.domain = settings.retrieval_domain
        self._db_config = {
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "dbname": settings.postgres_db,
            "user": settings.postgres_user,
            "password": settings.postgres_password,
        }

        from retrieval.hybrid_retriever import HybridRetriever

        self._retriever = HybridRetriever(
            db_config=self._db_config,
            domain=self.domain,
        )

    def retrieve(self, query: str) -> dict[str, Any]:
        import psycopg2

        with psycopg2.connect(**self._db_config) as conn:
            with conn.cursor() as cur:
                return self._retriever.retrieve(cur, query)


class QueryRewriteService:
    """Low-cost deterministic query rewrite for the retrieval stage."""

    def extract_query(self, params: dict[str, Any]) -> str:
        explicit_query = self._first_non_empty(
            params.get("query"),
            params.get("userInput"),
            params.get("message"),
            params.get("topic"),
            params.get("prompt"),
            params.get("question"),
            params.get("resourceTopic"),
        )
        if explicit_query:
            return explicit_query

        keyword = params.get("keyword")
        course_scope = params.get("courseScope")
        resource_type = params.get("resourceType")
        if any(isinstance(item, str) and item.strip() for item in (keyword, course_scope)):
            parts = [
                keyword.strip() if isinstance(keyword, str) else "",
                course_scope.strip() if isinstance(course_scope, str) else "",
                resource_type.strip() if isinstance(resource_type, str) else "",
            ]
            composed = " ".join(part for part in parts if part)
            if composed:
                return composed

        learning_context = params.get("learningContext", {})
        if not isinstance(learning_context, dict):
            learning_context = {}
        resource_query = self._compose_resource_query(params, learning_context)
        if resource_query:
            return resource_query

        candidates = [
            params.get("query"),
            params.get("userInput"),
            params.get("message"),
            params.get("topic"),
            params.get("prompt"),
            params.get("question"),
            params.get("resourceTopic"),
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()

        if isinstance(resource_type, str) and resource_type.strip():
            return resource_type.strip()
        return "未提供查询"

    def _compose_resource_query(
        self,
        params: dict[str, Any],
        learning_context: dict[str, Any],
    ) -> str:
        query = self._first_non_empty(
            params.get("topic"),
            params.get("keyPoints"),
            params.get("course"),
            learning_context.get("chapter"),
            learning_context.get("course"),
        )
        if not query:
            return ""

        parts = [
            self._clean_query_term(params.get("course")),
            self._clean_query_term(params.get("keyPoints")),
            self._clean_query_term(params.get("difficulty")),
            self._clean_query_term(learning_context.get("course")),
            self._clean_query_term(learning_context.get("chapter")),
        ]
        composed_parts: list[str] = []
        seen: set[str] = set()
        for part in parts:
            if not part:
                continue
            normalized = re.sub(r"\s+", " ", part).strip().lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            composed_parts.append(part)
        return " ".join(composed_parts)

    def _first_non_empty(self, *values: Any) -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _clean_query_term(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        text = value.strip()
        if not text:
            return ""
        normalized = text.upper()
        if normalized in {"DOCUMENT", "VIDEO", "MINDMAP", "READING", "SLIDES", "CODE"}:
            return ""
        return text

    def rewrite(self, params: dict[str, Any]) -> QueryRewriteResult:
        original_query = self.extract_query(params)
        learning_context = params.get("learningContext", {})
        prefixes = [
            learning_context.get("course", ""),
            learning_context.get("chapter", ""),
        ]
        rewritten_query = original_query
        for prefix in prefixes:
            if prefix and prefix not in rewritten_query:
                rewritten_query = f"{prefix} {rewritten_query}".strip()

        keywords = self._extract_keywords(rewritten_query)
        return QueryRewriteResult(
            originalQuery=original_query,
            rewrittenQuery=rewritten_query,
            keywords=keywords,
        )

    def _extract_keywords(self, text: str) -> list[str]:
        raw_terms = re.findall(r"[A-Za-z0-9+\-#_.]{2,}|[\u4e00-\u9fff]{2,}", text)
        seen: set[str] = set()
        keywords: list[str] = []
        for term in raw_terms:
            normalized = term.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            keywords.append(normalized)
            if len(keywords) >= 6:
                break
        return keywords or [text]


class HybridRetrievalService:
    """Hybrid retrieval with legacy-adapter and deterministic fallback."""

    def __init__(
        self,
        retriever: SupportsHybridRetrieve | None = None,
    ) -> None:
        self.domain = get_settings().retrieval_domain
        self.retriever = retriever

    def retrieve(
        self,
        *,
        query: str,
        rewritten_query: str,
        keywords: list[str],
    ) -> RetrievalResponse:
        raw_result = self.retrieve_raw(rewritten_query)
        return self.build_response(
            query=query,
            rewritten_query=rewritten_query,
            keywords=keywords,
            raw_result=raw_result,
        )

    def retrieve_raw(self, rewritten_query: str) -> dict[str, Any]:
        cache_key = self._build_raw_result_cache_key(rewritten_query)
        if cache_key:
            cached_result = _RETRIEVAL_RESULT_CACHE.get(cache_key)
            if isinstance(cached_result, dict):
                return cached_result

        raw_result = self._retrieve_raw(rewritten_query)
        if cache_key and self._is_cacheable_raw_result(raw_result):
            _RETRIEVAL_RESULT_CACHE.set(
                cache_key,
                raw_result,
                ttl_seconds=self._raw_result_cache_ttl_seconds(),
            )
        return raw_result

    def build_response(
        self,
        *,
        query: str,
        rewritten_query: str,
        keywords: list[str],
        raw_result: dict[str, Any],
    ) -> RetrievalResponse:
        documents = self._normalize_documents(raw_result, keywords)
        sources_summary = "；".join(
            f"{document.title}({document.channel}:{document.score})"
            for document in documents[:3]
        ) or "无命中来源"
        return RetrievalResponse(
            query=query,
            rewrittenQuery=rewritten_query,
            keywords=keywords,
            documents=documents,
            sourcesSummary=sources_summary,
        )

    def fallback_raw_result(
        self,
        *,
        rewritten_query: str,
        keywords: list[str],
    ) -> dict[str, Any]:
        keyword = keywords[0] if keywords else rewritten_query
        return {
            "query": rewritten_query,
            "channels": {
                "grep": {
                    "priority": [(f"fallback-{keyword}", f"候选知识: {keyword}", 0.4, [keyword])]
                },
                "vector": [],
                "graph": [],
            },
            "top": [(f"fallback-{keyword}", f"候选知识: {keyword}", 0.4)],
        }

    def channel_results(self, raw_result: dict[str, Any], channel_name: str) -> Any:
        channels = raw_result.get("channels", {}) if isinstance(raw_result, dict) else {}
        return channels.get(channel_name, {} if channel_name == "grep" else [])

    def _retrieve_raw(self, rewritten_query: str) -> dict[str, Any]:
        if self.retriever is not None:
            return self.retriever.retrieve(rewritten_query)

        try:
            adapter = LegacyHybridRetrieverAdapter()
            return adapter.retrieve(rewritten_query)
        except Exception:
            return {
                "query": rewritten_query,
                "channels": {},
                "top": [],
            }

    def _raw_result_cache_ttl_seconds(self) -> int:
        settings = get_settings()
        ttl_seconds = max(0, settings.retrieval_result_cache_ttl_seconds)
        _RETRIEVAL_RESULT_CACHE.max_entries = max(1, settings.runtime_cache_max_entries)
        return ttl_seconds

    def _build_raw_result_cache_key(self, rewritten_query: str) -> str:
        ttl_seconds = self._raw_result_cache_ttl_seconds()
        if ttl_seconds <= 0:
            return ""
        return stable_cache_key(
            "retrieval-raw",
            {
                "scope": self._raw_result_cache_scope(),
                "domain": self.domain,
                "query": rewritten_query,
            },
        )

    def _raw_result_cache_scope(self) -> str:
        if self.retriever is None:
            return "legacy-hybrid-retriever"
        return f"custom:{type(self.retriever).__module__}.{type(self.retriever).__qualname__}:{id(self.retriever)}"

    def _is_cacheable_raw_result(self, raw_result: dict[str, Any]) -> bool:
        if not isinstance(raw_result, dict):
            return False
        top_results = raw_result.get("top")
        channels = raw_result.get("channels")
        return bool(top_results or channels)

    def _normalize_documents(
        self,
        raw_result: dict[str, Any],
        keywords: list[str],
    ) -> list[RetrievalDocument]:
        if isinstance(raw_result, dict):
            documents = self._build_ranked_documents(raw_result, keywords)
            if documents:
                return documents

        return [
            RetrievalDocument(
                slug=f"fallback-{index + 1}",
                title=f"候选知识: {keyword}",
                score=round(1.0 - index * 0.1, 2),
                channel="fallback",
                matchType="fallback",
                evidence=f"由关键词 `{keyword}` 生成的回退候选。",
            )
            for index, keyword in enumerate(keywords[:3])
        ]

    def _build_ranked_documents(
        self,
        raw_result: dict[str, Any],
        keywords: list[str],
    ) -> list[RetrievalDocument]:
        top_results = raw_result.get("top", [])
        channels = raw_result.get("channels", {})
        grep_priority = channels.get("grep", {}).get("priority", [])
        vector_results = channels.get("vector", [])
        graph_results = channels.get("graph", [])

        priority_slugs = {str(item[0]) for item in grep_priority}
        vector_slugs = {str(item[0]) for item in vector_results}
        graph_slugs = {str(item[0]) for item in graph_results}

        scored_documents: list[tuple[float, RetrievalDocument]] = []
        phrase_anchor = self._phrase_anchor(keywords)
        for item in top_results[:8]:
            slug = str(item[0])
            title = str(item[1])
            base_score = float(item[2])
            snippet = self._extract_snippet(item)
            phrase_score, match_type = self._score_phrase_precision(
                title=title,
                phrase_anchor=phrase_anchor,
                keywords=keywords,
                is_priority=slug in priority_slugs,
            )
            channel = "hybrid"
            if slug in priority_slugs:
                channel = "phrase"
            elif slug in vector_slugs:
                channel = "vector"
            elif slug in graph_slugs:
                channel = "graph"

            scored_documents.append(
                (
                    phrase_score + base_score,
                    RetrievalDocument(
                        slug=slug,
                        title=title,
                        score=round(base_score, 4),
                        channel=channel,
                        matchType=match_type,
                        evidence=(
                            f"短语锚点 `{phrase_anchor}` 命中，关键词覆盖: "
                            f"{', '.join(self._matched_keywords(title, keywords)) or '无'}"
                        ),
                        snippet=snippet,
                    ),
                )
            )

        ranked = self._dedupe_ranked_documents(scored_documents)
        return [document for _, document in ranked[:5]]

    def _dedupe_ranked_documents(
        self,
        scored_documents: list[tuple[float, RetrievalDocument]],
    ) -> list[tuple[float, RetrievalDocument]]:
        deduped: dict[str, tuple[float, RetrievalDocument]] = {}
        for score, document in scored_documents:
            dedupe_key = self._document_dedupe_key(document)
            existing = deduped.get(dedupe_key)
            if existing is None or score > existing[0]:
                deduped[dedupe_key] = (score, document)
        return sorted(deduped.values(), key=lambda item: item[0], reverse=True)

    def _document_dedupe_key(self, document: RetrievalDocument) -> str:
        title_key = self._normalize_similarity_text(document.title)
        if title_key:
            return f"title:{title_key}"
        snippet_key = self._normalize_similarity_text(document.snippet or "")
        if snippet_key:
            return f"snippet:{snippet_key[:120]}"
        return f"slug:{document.slug}"

    def _normalize_similarity_text(self, value: str) -> str:
        return re.sub(r"\s+", "", (value or "").strip().lower())

    def _phrase_anchor(self, keywords: list[str]) -> str:
        return keywords[-1] if keywords else ""

    def _extract_snippet(self, item: Any) -> str | None:
        if isinstance(item, dict):
            for key in ("snippet", "content", "text", "summary"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()[:400]
            return None
        if isinstance(item, (list, tuple)):
            for extra in item[3:]:
                if isinstance(extra, str) and extra.strip():
                    return extra.strip()[:400]
                if isinstance(extra, dict):
                    for key in ("snippet", "content", "text", "summary"):
                        value = extra.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()[:400]
        return None

    def _score_phrase_precision(
        self,
        *,
        title: str,
        phrase_anchor: str,
        keywords: list[str],
        is_priority: bool,
    ) -> tuple[float, str]:
        normalized_title = self._normalize_text(title)
        normalized_anchor = self._normalize_text(phrase_anchor)
        matched_keywords = self._matched_keywords(title, keywords)

        if normalized_anchor and normalized_title == normalized_anchor:
            return (100.0, "title_exact")
        if normalized_anchor and normalized_title.startswith(normalized_anchor):
            return (90.0, "title_prefix")
        if normalized_anchor and normalized_anchor in normalized_title:
            return (80.0, "title_contains")
        if is_priority:
            return (70.0, "phrase_priority")
        if matched_keywords:
            return (50.0 + len(matched_keywords) * 5, "keyword_cover")
        return (10.0, "rank_only")

    def _matched_keywords(self, title: str, keywords: list[str]) -> list[str]:
        normalized_title = self._normalize_text(title)
        return [
            keyword
            for keyword in keywords
            if self._normalize_text(keyword) in normalized_title
        ]

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[\s_\-]+", "", text.lower())
