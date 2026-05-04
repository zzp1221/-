"""Conversation compaction utilities for tutoring flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StructuredConversationSummary(BaseModel):
    """Structured information extracted from historical dialogue."""

    topic_focus: list[str] = Field(default_factory=list, alias="topicFocus")
    learner_goal: str | None = Field(default=None, alias="learnerGoal")
    known_gaps: list[str] = Field(default_factory=list, alias="knownGaps")
    unresolved_questions: list[str] = Field(default_factory=list, alias="unresolvedQuestions")
    preferred_help_style: str | None = Field(default=None, alias="preferredHelpStyle")
    last_user_message: str | None = Field(default=None, alias="lastUserMessage")
    recent_progress: list[str] = Field(default_factory=list, alias="recentProgress")
    summary_text: str = Field(default="", alias="summaryText")

    model_config = ConfigDict(populate_by_name=True)


@dataclass(slots=True)
class CompactionResult:
    """Result of a compaction pass over conversation messages."""

    compacted_messages: list[dict[str, Any]]
    summary: str
    structured_summary: StructuredConversationSummary
    was_compacted: bool
    estimated_tokens_before: int
    estimated_tokens_after: int


class ConversationCompactor:
    """Compress long conversations while keeping recent tutoring context."""

    def __init__(
        self,
        token_budget: int = 1200,
        keep_recent_turns: int = 4,
        summary_max_chars: int = 280,
    ) -> None:
        self.token_budget = token_budget
        self.keep_recent_turns = keep_recent_turns
        self.summary_max_chars = summary_max_chars

    def estimate_tokens(self, messages: list[dict[str, Any]]) -> int:
        """Rough token estimate based on character count."""

        total_chars = 0
        for message in messages:
            total_chars += len(str(message.get("role", "")))
            total_chars += len(str(message.get("content", "")))
        return max(1, total_chars // 2)

    def compact(self, messages: list[dict[str, Any]]) -> CompactionResult:
        """Compact earlier turns into a short tutoring summary if over budget."""

        estimated_before = self.estimate_tokens(messages)
        structured_summary = self._extract_structured_summary(messages)
        if estimated_before <= self.token_budget or len(messages) <= self.keep_recent_turns:
            return CompactionResult(
                compacted_messages=[dict(message) for message in messages],
                summary=structured_summary.summary_text,
                structured_summary=structured_summary,
                was_compacted=False,
                estimated_tokens_before=estimated_before,
                estimated_tokens_after=estimated_before,
            )

        recent_messages = [dict(message) for message in messages[-self.keep_recent_turns :]]
        historical_messages = messages[: -self.keep_recent_turns]
        structured_summary = self._extract_structured_summary(historical_messages)
        summary = structured_summary.summary_text
        compacted_messages = [
            {
                "role": "system",
                "content": f"历史对话摘要: {summary}",
            },
            *recent_messages,
        ]
        estimated_after = self.estimate_tokens(compacted_messages)
        return CompactionResult(
            compacted_messages=compacted_messages,
            summary=summary,
            structured_summary=structured_summary,
            was_compacted=True,
            estimated_tokens_before=estimated_before,
            estimated_tokens_after=estimated_after,
        )

    def _extract_structured_summary(
        self,
        messages: list[dict[str, Any]],
    ) -> StructuredConversationSummary:
        """Extract structured tutoring signals from historical dialogue."""

        user_messages = [
            str(message.get("content", "")).replace("\n", " ").strip()
            for message in messages
            if str(message.get("role", "")).lower() == "user"
        ]
        assistant_messages = [
            str(message.get("content", "")).replace("\n", " ").strip()
            for message in messages
            if str(message.get("role", "")).lower() == "assistant"
        ]

        topic_focus = self._extract_topic_focus(user_messages)
        learner_goal = next(
            (
                message
                for message in user_messages
                if any(keyword in message for keyword in ("想", "希望", "需要", "目标", "复习", "掌握"))
            ),
            user_messages[-1] if user_messages else None,
        )
        unresolved_questions = [
            message
            for message in user_messages[-3:]
            if "?" in message or "？" in message or any(keyword in message for keyword in ("不懂", "不会", "为什么", "怎么"))
        ]
        known_gaps = [
            message[:18]
            for message in user_messages[-3:]
            if any(keyword in message for keyword in ("不会", "不懂", "总错", "易错", "分不清"))
        ]
        preferred_help_style = self._detect_help_style(user_messages)
        last_user_message = user_messages[-1] if user_messages else None
        recent_progress = [
            message[:24]
            for message in assistant_messages[-2:]
            if message
        ]

        summary_text = self._build_summary_text(
            topic_focus=topic_focus,
            learner_goal=learner_goal,
            unresolved_questions=unresolved_questions,
            known_gaps=known_gaps,
        )
        return StructuredConversationSummary(
            topicFocus=topic_focus,
            learnerGoal=learner_goal,
            knownGaps=known_gaps,
            unresolvedQuestions=unresolved_questions,
            preferredHelpStyle=preferred_help_style,
            lastUserMessage=last_user_message,
            recentProgress=recent_progress,
            summaryText=summary_text,
        )

    def _extract_topic_focus(self, user_messages: list[str]) -> list[str]:
        focus_terms: list[str] = []
        for message in reversed(user_messages):
            terms = [
                fragment
                for fragment in message.replace("，", " ").replace("。", " ").split()
                if len(fragment) >= 2
            ]
            for term in terms:
                if term not in focus_terms:
                    focus_terms.append(term)
                if len(focus_terms) >= 4:
                    return focus_terms
        return focus_terms

    def _detect_help_style(self, user_messages: list[str]) -> str | None:
        joined = " ".join(user_messages)
        if any(keyword in joined for keyword in ("例子", "举例", "案例")):
            return "example_first"
        if any(keyword in joined for keyword in ("一步步", "详细", "慢一点")):
            return "step_by_step"
        if user_messages:
            return "concept_then_question"
        return None

    def _build_summary_text(
        self,
        *,
        topic_focus: list[str],
        learner_goal: str | None,
        unresolved_questions: list[str],
        known_gaps: list[str],
    ) -> str:
        summary_parts = [
            f"主题: {', '.join(topic_focus) or '暂无'}",
            f"目标: {learner_goal or '暂无明确目标'}",
            f"薄弱点: {', '.join(known_gaps) or '暂无'}",
            f"未解决问题: {' | '.join(unresolved_questions) or '暂无'}",
        ]
        summary = " ; ".join(summary_parts)
        if len(summary) > self.summary_max_chars:
            return f"{summary[: self.summary_max_chars - 3]}..."
        return summary
