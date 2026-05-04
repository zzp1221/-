"""Persistence layer for practice question batches and judging results."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Protocol
from uuid import uuid4

from src.ai_modules.config import get_settings
from src.ai_modules.models import JudgeItemResult, JudgeResultPayload, PracticeQuestion, QuestionBatchPayload


def _adapt_json_payload(payload: dict[str, Any] | list[Any]) -> Any:
    try:
        from psycopg2.extras import Json

        return Json(payload)
    except ModuleNotFoundError:
        return json.dumps(payload, ensure_ascii=False)


class PracticeStore(Protocol):
    """Persistence contract for practice generation and judging."""

    async def save_question_batch(
        self,
        *,
        user_id: str,
        batch: QuestionBatchPayload,
        task_id: str | None = None,
    ) -> dict[str, Any]: ...

    async def save_judge_result(
        self,
        *,
        user_id: str,
        answers: dict[str, str],
        judge_result: JudgeResultPayload,
        persistence_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]: ...


class InMemoryPracticeStore:
    """In-memory store for tests and local fallback."""

    def __init__(self) -> None:
        self.question_batches: dict[str, dict[str, Any]] = {}
        self.judge_results: dict[str, dict[str, Any]] = {}

    async def save_question_batch(
        self,
        *,
        user_id: str,
        batch: QuestionBatchPayload,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        practice_set_id = str(uuid4())
        item_mappings: list[dict[str, Any]] = []
        for item_no, question in enumerate(batch.questions, start=1):
            item_mappings.append(
                {
                    "questionId": question.question_id,
                    "practiceItemId": str(uuid4()),
                    "itemNo": item_no,
                }
            )
        metadata = {
            "practiceSetId": practice_set_id,
            "userId": user_id,
            "taskId": task_id,
            "itemMappings": item_mappings,
        }
        self.question_batches[practice_set_id] = {
            "batch": batch.model_dump(by_alias=True),
            "metadata": metadata,
        }
        return metadata

    async def save_judge_result(
        self,
        *,
        user_id: str,
        answers: dict[str, str],
        judge_result: JudgeResultPayload,
        persistence_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        practice_set_id = str(
            (persistence_metadata or {}).get("practiceSetId") or uuid4()
        )
        item_mappings = {
            str(item.get("questionId")): item
            for item in (persistence_metadata or {}).get("itemMappings", [])
            if isinstance(item, dict)
        }
        submission_ids: list[dict[str, str]] = []
        for item in judge_result.items:
            submission_id = str(uuid4())
            submission_ids.append(
                {
                    "questionId": item.question_id,
                    "practiceItemId": str(
                        item_mappings.get(item.question_id, {}).get("practiceItemId") or uuid4()
                    ),
                    "practiceSubmissionId": submission_id,
                }
            )
        metadata = {
            "practiceSetId": practice_set_id,
            "userId": user_id,
            "answers": answers,
            "submissionMappings": submission_ids,
        }
        self.judge_results[practice_set_id] = {
            "judgeResult": judge_result.model_dump(by_alias=True),
            "metadata": metadata,
        }
        return metadata


class PostgresPracticeStore:
    """PostgreSQL-backed store for practice sets, items, and submissions."""

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

    async def save_question_batch(
        self,
        *,
        user_id: str,
        batch: QuestionBatchPayload,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        difficulty = self._normalize_difficulty(batch.difficulty)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO app.practice_set(
                        task_id, user_id, course_id, source_resource_id, difficulty_level, question_count, set_status, metadata_json
                    )
                    VALUES (%s, %s::uuid, %s, %s, %s::app.difficulty_level, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        task_id,
                        user_id,
                        None,
                        None,
                        difficulty,
                        len(batch.questions),
                        "OPEN",
                        _adapt_json_payload(
                            {
                                "title": batch.title,
                                "topic": batch.topic,
                            }
                        ),
                    ),
                )
                practice_set_id = str(cur.fetchone()[0])
                item_mappings: list[dict[str, Any]] = []
                for item_no, question in enumerate(batch.questions, start=1):
                    cur.execute(
                        """
                        INSERT INTO app.practice_item(
                            practice_set_id, item_no, question_type, stem, options_json, standard_answer, rubric_json, knowledge_tags, difficulty_level
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::app.difficulty_level)
                        RETURNING id
                        """,
                        (
                            practice_set_id,
                            item_no,
                            question.question_type,
                            question.stem,
                            _adapt_json_payload(question.options),
                            _adapt_json_payload({"answer": question.answer, "explanation": question.explanation}),
                            _adapt_json_payload({"explanation": question.explanation}),
                            _adapt_json_payload(question.knowledge_tags),
                            self._normalize_difficulty(question.difficulty_level),
                        ),
                    )
                    practice_item_id = str(cur.fetchone()[0])
                    item_mappings.append(
                        {
                            "questionId": question.question_id,
                            "practiceItemId": practice_item_id,
                            "itemNo": item_no,
                        }
                    )
            conn.commit()
        return {
            "practiceSetId": practice_set_id,
            "userId": user_id,
            "itemMappings": item_mappings,
        }

    async def save_judge_result(
        self,
        *,
        user_id: str,
        answers: dict[str, str],
        judge_result: JudgeResultPayload,
        persistence_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        practice_set_id = (persistence_metadata or {}).get("practiceSetId")
        if not practice_set_id:
            raise ValueError("missing practice set id")
        item_mappings = {
            str(item.get("questionId")): item
            for item in (persistence_metadata or {}).get("itemMappings", [])
            if isinstance(item, dict)
        }
        submission_mappings: list[dict[str, str]] = []
        with self._connect() as conn:
            with conn.cursor() as cur:
                for item in judge_result.items:
                    mapping = item_mappings.get(item.question_id)
                    if mapping is None:
                        continue
                    cur.execute(
                        """
                        INSERT INTO app.practice_submission(
                            practice_set_id, practice_item_id, user_id, answer_json, score, is_correct, judge_mode, judge_result_json, profile_delta_json
                        )
                        VALUES (%s, %s, %s::uuid, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (practice_item_id, user_id) DO UPDATE
                        SET answer_json = EXCLUDED.answer_json,
                            score = EXCLUDED.score,
                            is_correct = EXCLUDED.is_correct,
                            judge_mode = EXCLUDED.judge_mode,
                            judge_result_json = EXCLUDED.judge_result_json,
                            profile_delta_json = EXCLUDED.profile_delta_json,
                            submitted_at = now()
                        RETURNING id
                        """,
                        (
                            practice_set_id,
                            mapping["practiceItemId"],
                            user_id,
                            _adapt_json_payload({"answer": answers.get(item.question_id, "")}),
                            item.score,
                            item.is_correct,
                            "HYBRID",
                            _adapt_json_payload(item.model_dump(by_alias=True)),
                            _adapt_json_payload(item.profile_delta),
                        ),
                    )
                    practice_submission_id = str(cur.fetchone()[0])
                    submission_mappings.append(
                        {
                            "questionId": item.question_id,
                            "practiceItemId": str(mapping["practiceItemId"]),
                            "practiceSubmissionId": practice_submission_id,
                        }
                    )
                cur.execute(
                    """
                    UPDATE app.practice_set
                    SET set_status = %s,
                        metadata_json = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (
                        "JUDGED",
                        _adapt_json_payload(
                            {
                                "title": judge_result.title,
                                "summary": judge_result.summary,
                                "accuracy": judge_result.accuracy,
                            }
                        ),
                        practice_set_id,
                    ),
                )
            conn.commit()
        return {
            "practiceSetId": str(practice_set_id),
            "userId": user_id,
            "submissionMappings": submission_mappings,
        }

    def _normalize_difficulty(self, difficulty: str) -> str:
        normalized = str(difficulty or "MIXED").upper()
        if normalized not in {"BASIC", "INTERMEDIATE", "ADVANCED", "MIXED"}:
            return "MIXED"
        return normalized
