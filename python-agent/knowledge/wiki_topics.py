"""JSON-backed topic definitions for wiki expansion."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

TopicSection = tuple[str, str]
TopicDefinition = tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    list[str],
    list[str],
    str,
    list[TopicSection],
]

TOPICS_JSON_PATH = Path(__file__).with_suffix(".json")


def _expect_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Invalid topic field `{field}` in {TOPICS_JSON_PATH}")
    return value


def _expect_string_list(entry: dict[str, Any], field: str) -> list[str]:
    value = entry.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Invalid topic list field `{field}` in {TOPICS_JSON_PATH}")
    return list(value)


def _expect_sections(entry: dict[str, Any]) -> list[TopicSection]:
    sections = entry.get("sections")
    if not isinstance(sections, list):
        raise ValueError(f"Invalid topic field `sections` in {TOPICS_JSON_PATH}")

    normalized_sections: list[TopicSection] = []
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError(f"Invalid section entry in {TOPICS_JSON_PATH}")
        heading = section.get("heading")
        content = section.get("content")
        if not isinstance(heading, str) or not isinstance(content, str):
            raise ValueError(f"Invalid section payload in {TOPICS_JSON_PATH}")
        normalized_sections.append((heading, content))
    return normalized_sections


@lru_cache(maxsize=1)
def load_topics() -> list[TopicDefinition]:
    raw_payload = json.loads(TOPICS_JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw_payload, list):
        raise ValueError(f"Expected a list payload in {TOPICS_JSON_PATH}")

    topics: list[TopicDefinition] = []
    for entry in raw_payload:
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid topic entry in {TOPICS_JSON_PATH}")
        topics.append(
            (
                _expect_string(entry, "dir_name"),
                _expect_string(entry, "file_stem"),
                _expect_string(entry, "title"),
                _expect_string(entry, "course"),
                _expect_string(entry, "chapter"),
                _expect_string(entry, "difficulty"),
                _expect_string_list(entry, "tags"),
                _expect_string_list(entry, "aliases"),
                _expect_string(entry, "source"),
                _expect_sections(entry),
            )
        )
    return topics


TOPICS = load_topics()
