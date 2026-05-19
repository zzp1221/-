"""结构化对话摘要的持久化层。"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.config import get_settings


class ConversationSummaryDocument(BaseModel):
    """对话的结构化持久化摘要。"""

    conversation_id: str = Field(alias="conversationId")
    user_id: str | None = Field(default=None, alias="userId")
    task_id: str | None = Field(default=None, alias="taskId")
    topic_focus: list[str] = Field(default_factory=list, alias="topicFocus")
    canonical_topic_keys: list[str] = Field(default_factory=list, alias="canonicalTopicKeys")
    topic_aliases: dict[str, list[str]] = Field(default_factory=dict, alias="aliases")
    learner_goal: str | None = Field(default=None, alias="learnerGoal")
    known_gaps: list[str] = Field(default_factory=list, alias="knownGaps")
    unresolved_questions: list[str] = Field(default_factory=list, alias="unresolvedQuestions")
    preferred_help_style: str | None = Field(default=None, alias="preferredHelpStyle")
    last_user_message: str | None = Field(default=None, alias="lastUserMessage")
    recent_progress: list[str] = Field(default_factory=list, alias="recentProgress")
    confidence: float = 0.55
    summary_text: str = Field(alias="summaryText")
    source: str = "COMPACTION"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class ConversationSummaryStore(Protocol):
    """结构化摘要的持久化契约。"""

    async def save_summary(self, document: ConversationSummaryDocument) -> None: ...

    async def upsert_summary(self, document: ConversationSummaryDocument) -> None: ...

    async def get_latest_summary(
        self,
        *,
        conversation_id: str,
        user_id: str | None,
    ) -> ConversationSummaryDocument | None: ...


class InMemoryConversationSummaryStore:
    """测试和本地回退模式使用的内存摘要存储。"""

    def __init__(self) -> None:
        self.documents: list[ConversationSummaryDocument] = []

    async def save_summary(self, document: ConversationSummaryDocument) -> None:
        await self.upsert_summary(document)

    async def upsert_summary(self, document: ConversationSummaryDocument) -> None:
        for index, existing in enumerate(self.documents):
            if self._same_summary_key(existing, document):
                self.documents[index] = document
                return
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

    def _same_summary_key(
        self,
        existing: ConversationSummaryDocument,
        incoming: ConversationSummaryDocument,
    ) -> bool:
        return (
            existing.conversation_id == incoming.conversation_id
            and existing.user_id == incoming.user_id
        )


class MongoConversationSummaryStore:
    """基于 MongoDB 的对话摘要存储。"""

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

            client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
            )
            self._collection = client[self.database_name][self.collection_name]
        return self._collection

    async def save_summary(self, document: ConversationSummaryDocument) -> None:
        await self.upsert_summary(document)

    async def upsert_summary(self, document: ConversationSummaryDocument) -> None:
        criteria: dict[str, Any] = {
            "conversationId": document.conversation_id,
            "userId": document.user_id,
        }
        await asyncio.to_thread(
            self.collection.update_one,
            criteria,
            {"$set": document.model_dump(by_alias=True)},
            True,
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
