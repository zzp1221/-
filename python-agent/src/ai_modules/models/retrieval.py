"""Models for query rewriting and hybrid retrieval."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class QueryRewriteResult(BaseModel):
    """Normalized query rewrite output."""

    original_query: str = Field(alias="originalQuery")
    rewritten_query: str = Field(alias="rewrittenQuery")
    keywords: list[str]

    model_config = ConfigDict(populate_by_name=True)


class RetrievalDocument(BaseModel):
    """A single retrieved knowledge document."""

    slug: str
    title: str
    score: float
    channel: str
    match_type: str = Field(default="ranked", alias="matchType")
    evidence: str | None = None
    snippet: str | None = None
    url: str | None = None
    source_title: str | None = Field(default=None, alias="sourceTitle")
    published_date: str | None = Field(default=None, alias="publishedDate")

    model_config = ConfigDict(populate_by_name=True)


class RetrievalResponse(BaseModel):
    """Structured hybrid retrieval result."""

    query: str
    rewritten_query: str = Field(alias="rewrittenQuery")
    keywords: list[str]
    documents: list[RetrievalDocument]
    sources_summary: str = Field(alias="sourcesSummary")

    model_config = ConfigDict(populate_by_name=True)
