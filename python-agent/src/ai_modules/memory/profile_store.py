"""Persistence layer for learner profile snapshots."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID
from collections.abc import Callable
from typing import Any, Protocol

from src.ai_modules.config import get_settings
from src.ai_modules.models import LearnerProfileDimensions, LearnerProfileSnapshot


class ProfileStore(Protocol):
    """Persistence contract for learner profiles."""

    async def read_profile(self, user_id: str) -> LearnerProfileSnapshot | None: ...

    async def update_profile(
        self,
        *,
        user_id: str,
        dimensions: LearnerProfileDimensions,
        source_session_id: str | None = None,
    ) -> LearnerProfileSnapshot: ...


def _adapt_json_payload(payload: dict[str, Any]) -> Any:
    try:
        from psycopg2.extras import Json

        return Json(payload)
    except ModuleNotFoundError:
        return json.dumps(payload, ensure_ascii=False)


class InMemoryProfileStore:
    """In-memory store for tests and local fallback."""

    def __init__(self) -> None:
        self.snapshots: dict[str, LearnerProfileSnapshot] = {}

    async def read_profile(self, user_id: str) -> LearnerProfileSnapshot | None:
        return self.snapshots.get(user_id)

    async def update_profile(
        self,
        *,
        user_id: str,
        dimensions: LearnerProfileDimensions,
        source_session_id: str | None = None,
    ) -> LearnerProfileSnapshot:
        del source_session_id
        current = self.snapshots.get(user_id)
        version = 1 if current is None else current.version + 1
        snapshot = LearnerProfileSnapshot(
            userId=user_id,
            version=version,
            profile=dimensions,
        )
        self.snapshots[user_id] = snapshot
        return snapshot


class PostgresProfileStore:
    """PostgreSQL-backed profile store with snapshot/current tables."""

    def __init__(
        self,
        db_config: dict[str, Any] | None = None,
        connect_fn: Callable[..., Any] | None = None,
    ) -> None:
        settings = get_settings()
        self.db_config = db_config or {
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "dbname": settings.postgres_db,
            "user": settings.postgres_user,
            "password": settings.postgres_password,
        }
        self._connect_fn = connect_fn

    def _connect(self) -> Any:
        if self._connect_fn is not None:
            return self._connect_fn(**self.db_config)

        import psycopg2

        return psycopg2.connect(**self.db_config)

    def _read_profile_sync(self, user_id: str) -> LearnerProfileSnapshot | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT profile_json, summary_text
                    FROM app.user_profile_current
                    WHERE user_id = %s::uuid
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                profile_json, summary_text = row
                dimensions = LearnerProfileDimensions.model_validate(
                    {
                        **profile_json,
                        "summaryText": summary_text or profile_json.get("summaryText", ""),
                    }
                )
                cur.execute(
                    """
                    SELECT COALESCE(MAX(version), 0)
                    FROM app.user_profile_snapshot
                    WHERE user_id = %s::uuid
                    """,
                    (user_id,),
                )
                version = int(cur.fetchone()[0])
                return LearnerProfileSnapshot(
                    userId=user_id,
                    version=max(version, 1),
                    profile=dimensions,
                )

    def _update_profile_sync(
        self,
        *,
        user_id: str,
        dimensions: LearnerProfileDimensions,
        source_session_id: str | None = None,
    ) -> LearnerProfileSnapshot:
        profile_payload = dimensions.model_dump(by_alias=True)
        summary_text = dimensions.summary_text
        normalized_session_id = _normalize_uuid(source_session_id)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(MAX(version), 0) + 1
                    FROM app.user_profile_snapshot
                    WHERE user_id = %s::uuid
                    """,
                    (user_id,),
                )
                version = int(cur.fetchone()[0])
                cur.execute(
                    """
                    INSERT INTO app.user_profile_snapshot(
                        user_id, source_session_id, version, profile_json, summary_text, confidence
                    )
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        user_id,
                        normalized_session_id,
                        version,
                        _adapt_json_payload(profile_payload),
                        summary_text,
                        0.82,
                    ),
                )
                snapshot_id = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO app.user_profile_current(user_id, active_snapshot_id, profile_json, summary_text)
                    VALUES (%s::uuid, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET active_snapshot_id = EXCLUDED.active_snapshot_id,
                        profile_json = EXCLUDED.profile_json,
                        summary_text = EXCLUDED.summary_text,
                        updated_at = now()
                    """,
                    (
                        user_id,
                        snapshot_id,
                        _adapt_json_payload(profile_payload),
                        summary_text,
                    ),
                )

                # Keep snapshot/current atomic, but degrade gracefully if pgvector is unavailable.
                zero_vector = "[" + ",".join(["0"] * 1024) + "]"
                cur.execute("SAVEPOINT profile_vector_insert")
                try:
                    cur.execute(
                        """
                        INSERT INTO rag.user_profile_vector(profile_snapshot_id, user_id, version, embedding, is_active)
                        VALUES (%s, %s::uuid, %s, %s::vector, TRUE)
                        ON CONFLICT (user_id, version) DO NOTHING
                        """,
                        (snapshot_id, user_id, version, zero_vector),
                    )
                except Exception:
                    cur.execute("ROLLBACK TO SAVEPOINT profile_vector_insert")
                finally:
                    cur.execute("RELEASE SAVEPOINT profile_vector_insert")
            conn.commit()

        return LearnerProfileSnapshot(
            userId=user_id,
            version=version,
            profile=dimensions,
        )

    async def read_profile(self, user_id: str) -> LearnerProfileSnapshot | None:
        return await asyncio.to_thread(self._read_profile_sync, user_id)

    async def update_profile(
        self,
        *,
        user_id: str,
        dimensions: LearnerProfileDimensions,
        source_session_id: str | None = None,
    ) -> LearnerProfileSnapshot:
        return await asyncio.to_thread(
            self._update_profile_sync,
            user_id=user_id,
            dimensions=dimensions,
            source_session_id=source_session_id,
        )


def _normalize_uuid(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError):
        return None
