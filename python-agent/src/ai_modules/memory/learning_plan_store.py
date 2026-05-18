"""学习路径及其快照的持久化层。"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any, Protocol
from uuid import uuid4

from src.ai_modules.config import get_settings
from src.ai_modules.models import LearningPlanPayload


def _adapt_json_payload(payload: dict[str, Any]) -> Any:
    try:
        from psycopg2.extras import Json

        return Json(payload)
    except ModuleNotFoundError:
        return json.dumps(payload, ensure_ascii=False)


class LearningPlanStore(Protocol):
    """学习路径当前状态和快照的持久化契约。"""

    async def save_plan(
        self,
        *,
        user_id: str,
        plan: LearningPlanPayload,
        trigger_source: str,
        course_id: str | None = None,
    ) -> dict[str, Any]: ...


class InMemoryLearningPlanStore:
    """用于测试和本地回退的内存存储。"""

    def __init__(self) -> None:
        self.active_plans_by_user: dict[str, dict[str, Any]] = {}
        self.snapshots_by_plan: dict[str, list[dict[str, Any]]] = {}

    async def save_plan(
        self,
        *,
        user_id: str,
        plan: LearningPlanPayload,
        trigger_source: str,
        course_id: str | None = None,
    ) -> dict[str, Any]:
        current_record = self.active_plans_by_user.get(user_id)
        plan_id = str(current_record["planId"]) if current_record else str(uuid4())
        version = 1 if current_record is None else int(current_record["version"]) + 1
        snapshot_id = str(uuid4())
        metadata = {
            "planId": plan_id,
            "snapshotId": snapshot_id,
            "userId": user_id,
            "courseId": course_id,
            "version": version,
            "triggerSource": trigger_source,
        }
        stored_record = {
            **metadata,
            "learningPath": plan.model_dump(by_alias=True),
            "summaryText": plan.summary_text,
        }
        self.active_plans_by_user[user_id] = stored_record
        self.snapshots_by_plan.setdefault(plan_id, []).append(stored_record)
        return metadata


class PostgresLearningPlanStore:
    """基于 PostgreSQL 的学习路径当前状态和快照存储。"""

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

    def _save_plan_sync(
        self,
        *,
        user_id: str,
        plan: LearningPlanPayload,
        trigger_source: str,
        course_id: str | None = None,
    ) -> dict[str, Any]:
        plan_payload = plan.model_dump(by_alias=True)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id
                    FROM app.learning_plan
                    WHERE user_id = %s::uuid
                      AND status = 'ACTIVE'
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                if row is None:
                    cur.execute(
                        """
                        INSERT INTO app.learning_plan(user_id, course_id, plan_json, status)
                        VALUES (%s::uuid, %s::uuid, %s, %s)
                        RETURNING id
                        """,
                        (
                            user_id,
                            course_id,
                            _adapt_json_payload(plan_payload),
                            "ACTIVE",
                        ),
                    )
                    plan_id = str(cur.fetchone()[0])
                    version = 1
                else:
                    plan_id = str(row[0])
                    cur.execute(
                        """
                        UPDATE app.learning_plan
                        SET course_id = %s::uuid,
                            plan_json = %s,
                            status = %s,
                            updated_at = now()
                        WHERE id = %s
                        """,
                        (
                            course_id,
                            _adapt_json_payload(plan_payload),
                            "ACTIVE",
                            plan_id,
                        ),
                    )
                    cur.execute(
                        """
                        SELECT COALESCE(MAX(version), 0) + 1
                        FROM app.learning_plan_snapshot
                        WHERE plan_id = %s
                        """,
                        (plan_id,),
                    )
                    version = int(cur.fetchone()[0])

                cur.execute(
                    """
                    INSERT INTO app.learning_plan_snapshot(
                        plan_id, user_id, course_id, version, trigger_source, plan_json, summary_text
                    )
                    VALUES (%s, %s::uuid, %s::uuid, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        plan_id,
                        user_id,
                        course_id,
                        version,
                        trigger_source,
                        _adapt_json_payload(plan_payload),
                        plan.summary_text,
                    ),
                )
                snapshot_id = str(cur.fetchone()[0])
            conn.commit()
        return {
            "planId": plan_id,
            "snapshotId": snapshot_id,
            "userId": user_id,
            "courseId": course_id,
            "version": version,
            "triggerSource": trigger_source,
        }

    async def save_plan(
        self,
        *,
        user_id: str,
        plan: LearningPlanPayload,
        trigger_source: str,
        course_id: str | None = None,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self._save_plan_sync,
            user_id=user_id,
            plan=plan,
            trigger_source=trigger_source,
            course_id=course_id,
        )
