"""Resource push agent that selects existing resources and returns delivery links."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.config import get_settings
from src.ai_modules.models import (
    ProgressPayload,
    ProgressSSEEvent,
    ResourceFilePayload,
    ResourceFileSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PushResourceCandidate:
    title: str
    resource_type: str
    summary_text: str
    file_name: str
    mime_type: str | None
    bucket_name: str | None
    object_key: str | None
    access_mode: str | None
    storage_url: str | None
    score: int
    matched_terms: list[str]
    download_url: str | None = None


class ResourcePushAgent(PlaceholderAgent):
    """Select existing resources from object storage instead of regenerating them."""

    def __init__(self) -> None:
        super().__init__("Resource Push Agent", "resource_push")
        self.settings = get_settings()

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot,
        system_prompt: str,
    ) -> asyncio.AsyncIterator[SSEEvent]:
        del service_type, snapshot, system_prompt

        query = self._build_query(params)
        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=25,
                message=f"正在根据推送参数筛选资源：{query}",
            ),
        )

        candidates = await asyncio.to_thread(self._select_candidates, params)
        if not candidates:
            params["pushedResources"] = []
            yield ResultChunkSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=seq + 1,
                payload=ResultChunkPayload(
                    text=(
                        f"未找到与“{query}”匹配的现成资源。"
                        "请尝试调整关键词、课程范围或资源类型后重试。"
                    )
                ),
            )
            return

        params["pushedResources"] = [
            {
                "title": item.title,
                "resourceType": item.resource_type,
                "fileName": item.file_name,
                "downloadUrl": item.download_url,
                "summaryText": item.summary_text,
                "matchedTerms": item.matched_terms,
            }
            for item in candidates
        ]

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=65,
                message=f"已筛选出 {len(candidates)} 个可推送资源",
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 2,
            payload=ResultChunkPayload(
                text=self._build_summary_text(query, candidates),
            ),
        )

        next_seq = seq + 3
        for item in candidates:
            yield ResourceFileSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=next_seq,
                payload=ResourceFilePayload(
                    assetType=item.resource_type,
                    title=item.title,
                    summary=item.summary_text,
                    displayMode="download",
                    fileName=item.file_name,
                    localPath=None,
                    mimeType=item.mime_type,
                    downloadUrl=item.download_url,
                ),
            )
            next_seq += 1

    def _build_query(self, params: dict[str, Any]) -> str:
        parts = [
            self._normalize_text(params.get("keyword")),
            self._normalize_text(params.get("courseScope")),
            self._normalize_text(params.get("resourceType")),
        ]
        return " / ".join(part for part in parts if part) or "未指定推送条件"

    def _select_candidates(self, params: dict[str, Any]) -> list[PushResourceCandidate]:
        preferred_type = self._normalize_text(params.get("resourceType"))
        keyword = self._normalize_text(params.get("keyword"))
        course_scope = self._normalize_text(params.get("courseScope"))
        terms = self._build_terms(keyword, course_scope, preferred_type)

        sql = """
            SELECT
                lr.title,
                lr.resource_type::text AS resource_type,
                COALESCE(lr.summary_text, '') AS summary_text,
                ro.file_name,
                ro.mime_type,
                ro.bucket_name,
                ro.object_key,
                ro.access_mode,
                ro.storage_url,
                COALESCE(lr.tags::text, '') AS tags_text,
                COALESCE(lr.metadata_json::text, '') AS metadata_text
            FROM app.learning_resource lr
            JOIN storage.resource_object ro ON ro.id = lr.storage_object_id
            WHERE lr.status = 'ACTIVE'
              AND lr.storage_object_id IS NOT NULL
              AND (%(preferred_type)s = '' OR lr.resource_type::text = %(preferred_type)s)
            ORDER BY lr.updated_at DESC
            LIMIT 80
        """

        with psycopg2.connect(**self.settings.postgres_connect_kwargs()) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, {"preferred_type": preferred_type})
                rows = cursor.fetchall()

        ranked: list[PushResourceCandidate] = []
        for row in rows:
            if not self._is_pushable_resource(row):
                continue
            searchable_text = " ".join(
                [
                    self._normalize_text(row.get("title")),
                    self._normalize_text(row.get("summary_text")),
                    self._normalize_text(row.get("tags_text")),
                    self._normalize_text(row.get("metadata_text")),
                    self._normalize_text(row.get("resource_type")),
                    self._normalize_text(row.get("file_name")),
                ]
            ).lower()
            matched_terms = [term for term in terms if term.lower() in searchable_text]
            score = len(matched_terms) * 10
            if keyword and keyword.lower() in searchable_text:
                score += 20
            if course_scope and course_scope.lower() in searchable_text:
                score += 20
            if preferred_type and preferred_type.lower() == self._normalize_text(row.get("resource_type")).lower():
                score += 15
            if terms and score == 0:
                continue

            candidate = PushResourceCandidate(
                title=self._normalize_text(row.get("title")) or "未命名资源",
                resource_type=self._normalize_text(row.get("resource_type")) or "DOCUMENT",
                summary_text=self._normalize_text(row.get("summary_text")) or "已命中现成资源，可直接推送。",
                file_name=self._normalize_text(row.get("file_name")) or "resource.dat",
                mime_type=self._normalize_text(row.get("mime_type")) or None,
                bucket_name=self._normalize_text(row.get("bucket_name")) or None,
                object_key=self._normalize_text(row.get("object_key")) or None,
                access_mode=self._normalize_text(row.get("access_mode")) or None,
                storage_url=self._normalize_text(row.get("storage_url")) or None,
                score=score,
                matched_terms=matched_terms[:4],
            )
            candidate.download_url = self._resolve_download_url(candidate)
            if candidate.download_url:
                ranked.append(candidate)

        ranked.sort(key=lambda item: (-item.score, item.title))
        return ranked[:3]

    def _is_pushable_resource(self, row: dict[str, Any]) -> bool:
        file_name = self._normalize_text(row.get("file_name")).lower()
        mime_type = self._normalize_text(row.get("mime_type")).lower()
        object_key = self._normalize_text(row.get("object_key")).lower()
        storage_url = self._normalize_text(row.get("storage_url")).lower()

        if mime_type == "application/json":
            return False
        if any(path.endswith(".json") for path in (file_name, object_key, storage_url) if path):
            return False
        return bool(file_name or object_key or storage_url)

    def _resolve_download_url(self, item: PushResourceCandidate) -> str | None:
        if item.storage_url and item.access_mode in {"DIRECT", "PRESIGNED"}:
            return item.storage_url
        if not item.object_key:
            return item.storage_url
        bucket_name = item.bucket_name or self.settings.minio_bucket
        try:
            from minio import Minio

            client = Minio(**self.settings.minio_connect_kwargs())
            return client.presigned_get_object(
                bucket_name,
                item.object_key,
                expires=timedelta(hours=2),
            )
        except Exception:
            LOGGER.warning(
                "Failed to create presigned url for resource push bucket=%s object=%s",
                bucket_name,
                item.object_key,
                exc_info=True,
            )
            return item.storage_url

    def _build_terms(self, keyword: str, course_scope: str, preferred_type: str) -> list[str]:
        terms: list[str] = []
        for raw in (keyword, course_scope):
            if not raw:
                continue
            for token in raw.replace("/", " ").replace(">", " ").split():
                cleaned = token.strip()
                if cleaned and cleaned not in terms:
                    terms.append(cleaned)
        if preferred_type:
            terms.append(preferred_type)
        return terms

    def _build_summary_text(self, query: str, candidates: list[PushResourceCandidate]) -> str:
        titles = "，".join(item.title for item in candidates[:3])
        return (
            f"已按“{query}”筛选到 {len(candidates)} 个现成资源，并生成可直接推送的下载链接。"
            f"优先资源：{titles}。"
        )

    @staticmethod
    def _normalize_text(value: Any) -> str:
        return str(value).strip() if isinstance(value, str) else ""
