"""Persistence layer for structured conversation summaries."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.config import get_settings


class ConversationSummaryDocument(BaseModel):
    """Structured summary persisted for a conversation."""

    conversation_id: str = Field(alias="conversationId")
    user_id: str | None = Field(default=None, alias="userId")
    task_id: str | None = Field(default=None, alias="taskId")
    topic_focus: list[str] = Field(default_factory=list, alias="topicFocus")
    learner_goal: str | None = Field(default=None, alias="learnerGoal")
    known_gaps: list[str] = Field(default_factory=list, alias="knownGaps")
    unresolved_questions: list[str] = Field(default_factory=list, alias="unresolvedQuestions")
    preferred_help_style: str | None = Field(default=None, alias="preferredHelpStyle")
    last_user_message: str | None = Field(default=None, alias="lastUserMessage")
    recent_progress: list[str] = Field(default_factory=list, alias="recentProgress")
    summary_text: str = Field(alias="summaryText")
    source: str = "COMPACTION"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class ConversationSummaryStore(Protocol):
    """Persistence contract for structured summaries."""

    async def save_summary(self, document: ConversationSummaryDocument) -> None: ...

    async def get_latest_summary(
        self,
        *,
        conversation_id: str,
        user_id: str | None,
    ) -> ConversationSummaryDocument | None: ...


class InMemoryConversationSummaryStore:
    """In-memory summary store used by tests and local fallback mode."""

    def __init__(self) -> None:
        self.documents: list[ConversationSummaryDocument] = []

    async def save_summary(self, document: ConversationSummaryDocument) -> None:
        self.documents.append(document)

    async def get_latest_summary(
        self,
        *,
        conversation_id: str,
        user_id: str | None,
    ) -> ConversationSummaryDocument | None:
        for document in reversed(self.documents):
            if document.conversation_id == conversation_id and document.user_id == user_id:
                return document
        return None


class MongoConversationSummaryStore:
    """Mongo-backed store for conversation summaries."""

    def __init__(
        self,
        mongo_uri: str | None = None,
        database_name: str | None = None,
        collection_name: str = "conversation_summaries",
        collection: Any | None = None,
    ) -> None:
        settings = get_settings()
        self.mongo_uri = mongo_uri or settings.mongo_uri
        self.database_name = database_name or settings.mongo_db
        self.collection_name = collection_name
        self._collection = collection

    @property
    def collection(self) -> Any:
        if self._collection is None:
            from pymongo import MongoClient

            client = MongoClient(self.mongo_uri)
            self._collection = client[self.database_name][self.collection_name]
        return self._collection

    async def save_summary(self, document: ConversationSummaryDocument) -> None:
        await asyncio.to_thread(
            self.collection.insert_one,
            document.model_dump(by_alias=True),
        )

    async def get_latest_summary(
        self,
        *,
        conversation_id: str,
        user_id: str | None,
    ) -> ConversationSummaryDocument | None:
        criteria: dict[str, Any] = {"conversationId": conversation_id}
        if user_id is not None:
            criteria["userId"] = user_id

        record = await asyncio.to_thread(
            self.collection.find_one,
            criteria,
            sort=[("createdAt", -1)],
        )
        if record is None:
            return None
        record.pop("_id", None)
        return ConversationSummaryDocument.model_validate(record)
