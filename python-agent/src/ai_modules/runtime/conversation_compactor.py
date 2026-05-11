"""Conversation compaction utilities for tutoring flows."""

from __future__ import annotations

from dataclasses import dataclass
import re
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


@dataclass(slots=True)
class TopicCandidate:
    """A scored topic candidate extracted from a user message."""

    text: str
    source: str
    recency_rank: int
    order: int


class ConversationCompactor:
    """Compress long conversations while keeping recent tutoring context."""

    def __init__(
        self,
        token_budget: int = 1200,
        keep_recent_turns: int = 4,
        summary_max_chars: int = 500,
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

    def compact(
        self,
        messages: list[dict[str, Any]],
        previous_summary: StructuredConversationSummary | None = None,
    ) -> CompactionResult:
        """Compact earlier turns into a short tutoring summary if over budget."""

        estimated_before = self.estimate_tokens(messages)
        structured_summary = self._extract_structured_summary(messages)
        if previous_summary is not None:
            structured_summary = self._merge_summaries(
                new_summary=structured_summary,
                previous_summary=previous_summary,
            )
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
        if previous_summary is not None:
            structured_summary = self._merge_summaries(
                new_summary=structured_summary,
                previous_summary=previous_summary,
            )
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
            None,
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
        candidates: list[TopicCandidate] = []
        order = 0
        for recency_rank, message in enumerate(reversed(user_messages)):
            for candidate_text, source in self._extract_topic_candidates(message):
                candidates.append(
                    TopicCandidate(
                        text=candidate_text,
                        source=source,
                        recency_rank=recency_rank,
                        order=order,
                    )
                )
                order += 1
        if not candidates:
            return []

        scored_candidates = sorted(
            candidates,
            key=lambda candidate: (
                -self._score_topic_candidate(candidate),
                candidate.recency_rank,
                candidate.order,
            ),
        )
        focus_terms: list[str] = []
        for candidate in scored_candidates:
            if candidate.text in focus_terms:
                continue
            focus_terms.append(candidate.text)
            if len(focus_terms) >= 6:
                break
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

    def _merge_summaries(
        self,
        *,
        new_summary: StructuredConversationSummary,
        previous_summary: StructuredConversationSummary,
    ) -> StructuredConversationSummary:
        topic_focus = self._merge_unique(previous_summary.topic_focus, new_summary.topic_focus, limit=6)
        known_gaps = self._merge_unique(previous_summary.known_gaps, new_summary.known_gaps, limit=5)
        unresolved_questions = self._merge_unique(
            previous_summary.unresolved_questions,
            new_summary.unresolved_questions,
            limit=5,
        )
        recent_progress = self._merge_unique(
            previous_summary.recent_progress,
            new_summary.recent_progress,
            limit=4,
        )
        learner_goal = new_summary.learner_goal or previous_summary.learner_goal
        preferred_help_style = (
            new_summary.preferred_help_style or previous_summary.preferred_help_style
        )
        last_user_message = new_summary.last_user_message or previous_summary.last_user_message
        return StructuredConversationSummary(
            topicFocus=topic_focus,
            learnerGoal=learner_goal,
            knownGaps=known_gaps,
            unresolvedQuestions=unresolved_questions,
            preferredHelpStyle=preferred_help_style,
            lastUserMessage=last_user_message,
            recentProgress=recent_progress,
            summaryText=self._build_summary_text(
                topic_focus=topic_focus,
                learner_goal=learner_goal,
                unresolved_questions=unresolved_questions,
                known_gaps=known_gaps,
            ),
        )

    def _merge_unique(self, older: list[str], newer: list[str], *, limit: int) -> list[str]:
        merged: list[str] = []
        for item in [*older, *newer]:
            normalized = str(item).strip()
            if not normalized or normalized in merged:
                continue
            merged.append(normalized)
            if len(merged) >= limit:
                break
        return merged

    def _extract_topic_candidates(self, message: str) -> list[tuple[str, str]]:
        candidates: list[tuple[str, str]] = []
        for topic in self._extract_by_patterns(message):
            if topic not in [item[0] for item in candidates]:
                candidates.append((topic, "pattern"))
        for topic in self._extract_identifiers(message):
            if topic not in [item[0] for item in candidates]:
                candidates.append((topic, "identifier"))
        if candidates:
            return candidates
        for topic in self._extract_fallback_topics(message):
            if topic not in [item[0] for item in candidates]:
                candidates.append((topic, "fallback"))
        return candidates

    def _extract_by_patterns(self, message: str) -> list[str]:
        patterns: list[tuple[re.Pattern[str], tuple[str, ...]]] = [
            (re.compile(r"什么是(?P<a>[^，。！？；:：]+)"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)是什么"), ("a",)),
            (re.compile(r"(?:请解释|解释一下)(?P<a>[^，。！？；:：]+)"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)具体怎么用"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)怎么用"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)如何用"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)怎么写"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)是怎么产生的"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)怎么产生的"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)怎么避免"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)怎么解决"), ("a",)),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)的核心参数有哪些"), ("a", "__core_params__")),
            (re.compile(r"(?P<a>[^，。！？；:：]+?)有哪些"), ("a",)),
            (re.compile(r"(?:回到|继续说|继续讲|总结一下今天学到的|总结一下)(?P<a>[^，。！？；:：]+)"), ("a",)),
            (
                re.compile(
                    r"(?P<a>[^，。！？；:：]+?)\s*(?:和|与)\s*(?P<b>[^，。！？；:：]+?)\s*(?:有什么区别|有什么不同|区别|不同)"
                ),
                ("a", "b"),
            ),
        ]
        extracted: list[str] = []
        for pattern, fields in patterns:
            match = pattern.search(message)
            if match is None:
                continue
            for field in fields:
                if field == "__core_params__":
                    base = self._normalize_topic_chunk(match.group("a"))
                    if base:
                        extracted.extend(self._dedupe_topics([f"{base}核心参数", base]))
                    continue
                normalized = self._normalize_topic_chunk(match.group(field))
                if normalized:
                    extracted.append(normalized)
        return self._dedupe_topics(extracted)

    def _extract_identifiers(self, message: str) -> list[str]:
        identifiers: list[str] = []
        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9_]{1,31}\b", message):
            normalized = self._normalize_topic_chunk(token)
            if normalized:
                identifiers.append(normalized)
        return self._dedupe_topics(identifiers)

    def _extract_fallback_topics(self, message: str) -> list[str]:
        normalized_message = self._normalize_topic_chunk(message)
        if not normalized_message:
            return []
        topics: list[str] = []
        if any(connector in normalized_message for connector in ("和", "与", "及", "以及")):
            for piece in re.split(r"(?:和|与|及|以及)", normalized_message):
                normalized_piece = self._normalize_topic_chunk(piece)
                if normalized_piece:
                    topics.append(normalized_piece)
        topics.append(normalized_message)
        return self._dedupe_topics(topics)

    def _score_topic_candidate(self, candidate: TopicCandidate) -> int:
        score_map = {"pattern": 4, "identifier": 3, "fallback": 1}
        score = score_map.get(candidate.source, 0)
        if candidate.recency_rank < 2:
            score += 1
        if self._looks_like_technical_topic(candidate.text):
            score += 2
        if self._is_generic_topic(candidate.text):
            score -= 2
        if self._looks_like_full_question(candidate.text):
            score -= 2
        if len(candidate.text) > 16 and not self._is_identifier(candidate.text):
            score -= 1
        return score

    def _looks_like_technical_topic(self, text: str) -> bool:
        technical_markers = (
            "线程",
            "锁",
            "并发",
            "同步",
            "参数",
            "关键字",
            "线程池",
            "可见性",
            "原子",
            "死锁",
            "volatile",
            "synchronized",
        )
        return any(marker.lower() in text.lower() for marker in technical_markers)

    def _is_generic_topic(self, text: str) -> bool:
        generic_terms = {"这个", "那个", "问题", "东西", "内容", "情况", "知识点"}
        return text in generic_terms

    def _looks_like_full_question(self, text: str) -> bool:
        question_markers = ("什么", "怎么", "如何", "为什么", "哪些", "哪个", "能否", "可否", "吗")
        return any(marker in text for marker in question_markers) or "?" in text or "？" in text

    def _is_identifier(self, text: str) -> bool:
        return re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{1,31}", text) is not None

    def _dedupe_topics(self, topics: list[str]) -> list[str]:
        deduped: list[str] = []
        for topic in topics:
            if topic and topic not in deduped:
                deduped.append(topic)
        return deduped

    def _normalize_topic_chunk(self, chunk: str) -> str:
        normalized = str(chunk).strip()
        if not normalized:
            return ""
        normalized = re.sub(
            r"^(那我前面问的|回到|总结一下今天学到的|总结一下|继续上次的话题|继续说|继续讲|请问|请解释|解释一下|什么是)",
            "",
            normalized,
        )
        normalized = re.sub(
            r"(的核心参数有哪些|核心参数有哪些|具体怎么用|如何用|怎么写|是怎么产生的|怎么产生的|怎么避免|怎么解决|怎么用|有什么区别|有什么不同|区别|不同|有哪些|是什么|能再举个例子吗|能再举个例子|举个例子吗|举个例子|还有别的解决办法吗|还有别的解决办法)$",
            "",
            normalized,
        )
        normalized = re.sub(r"^(的|了|呢|吗|呀|啊)+|(?:的|了|呢|吗|呀|啊|问题)+$", "", normalized)
        normalized = normalized.strip(" ,，。？?:：;；|")
        if not normalized:
            return ""
        if self._is_identifier(normalized):
            return normalized
        normalized = re.sub(r"\s+", "", normalized)
        if len(normalized) < 2 or len(normalized) > 16:
            return ""
        if self._is_generic_topic(normalized):
            return ""
        return normalized
