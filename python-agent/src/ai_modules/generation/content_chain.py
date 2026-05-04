"""LLM-backed content generation chain with deterministic fallback."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, ClassVar, Protocol

import httpx
from opentelemetry import trace
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.ai_modules.config import get_settings
from src.ai_modules.generation.prompts import (
    build_code_system_prompt,
    build_code_user_prompt,
    build_document_system_prompt,
    build_document_user_prompt,
    build_mindmap_system_prompt,
    build_mindmap_user_prompt,
    build_reading_system_prompt,
    build_reading_user_prompt,
    build_slides_system_prompt,
    build_slides_user_prompt,
)

LOGGER = logging.getLogger(__name__)
TRACER = trace.get_tracer(__name__)


class GeneratedSection(BaseModel):
    """Structured output for a single generated section."""

    title: str
    body: str
    tips: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class GeneratedSectionBundle(BaseModel):
    """Generated bundle for a structured teaching document."""

    sections: list[GeneratedSection]


class GeneratedTextAsset(BaseModel):
    """Structured output for reading or code-style assets."""

    title: str
    summary: str
    body: str


class GeneratedSlide(BaseModel):
    """A single generated slide."""

    title: str
    bullets: list[str] = Field(default_factory=list)
    speaker_notes: str = Field(alias="speakerNotes")

    model_config = ConfigDict(populate_by_name=True)


class GeneratedSlideDeck(BaseModel):
    """Structured output for slides."""

    title: str
    summary: str
    slides: list[GeneratedSlide]

    model_config = ConfigDict(populate_by_name=True)


class GeneratedMindMapNode(BaseModel):
    """A node in the generated mind map."""

    name: str
    children: list["GeneratedMindMapNode"] = Field(default_factory=list)


class GeneratedMindMap(BaseModel):
    """Structured output for a mind map."""

    title: str
    summary: str
    root: str
    children: list[GeneratedMindMapNode]


GeneratedMindMapNode.model_rebuild()


class GeneratedCodeAsset(BaseModel):
    """Structured output for a code asset."""

    title: str
    summary: str
    code: str
    explanation: str


class SupportsStructuredGenerator(Protocol):
    """Protocol for primary structured-content generators."""

    def generate_document_sections(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        section_plans: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> GeneratedSectionBundle: ...

    def generate_reading_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedTextAsset: ...

    def generate_slides_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedSlideDeck: ...

    def generate_mindmap_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedMindMap: ...

    def generate_code_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedCodeAsset: ...


class BailianStructuredGenerator:
    """OpenAI-compatible structured generator for Bailian and Spark."""

    _shared_clients: ClassVar[dict[str, httpx.Client]] = {}

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        max_retries: int = 2,
        backoff_seconds: float = 0.5,
    ) -> None:
        settings = get_settings()
        self.provider_name = settings.model_provider.strip().lower()
        if self.provider_name == "spark":
            self.api_key = api_key or settings.spark_api_key
            self.base_url = settings.spark_base_url.rstrip("/")
            self.model_name = model_name or settings.spark_model_name
        else:
            self.provider_name = "bailian"
            self.api_key = api_key or settings.bailian_api_key
            self.base_url = settings.bailian_base_url.rstrip("/")
            self.model_name = model_name or settings.model_name
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def _get_client(self) -> httpx.Client:
        client_key = f"{self.provider_name}:{self.base_url}"
        client = self._shared_clients.get(client_key)
        if client is None or client.is_closed:
            client = httpx.Client(
                timeout=60.0,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
            self._shared_clients[client_key] = client
        return client

    def _post_chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError(f"missing {self.provider_name} api key")
        client = self._get_client()
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        response = client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        self._record_usage(data)
        return data

    def _record_usage(self, data: dict[str, Any]) -> None:
        usage = data.get("usage", {})
        if not isinstance(usage, dict):
            return
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        cached_tokens = 0
        prompt_details = usage.get("prompt_tokens_details", {})
        if isinstance(prompt_details, dict):
            cached_tokens = int(prompt_details.get("cached_tokens", 0) or 0)
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attribute("llm.provider", self.provider_name)
            current_span.set_attribute("llm.model_name", self.model_name)
            current_span.set_attribute("llm.prompt_tokens", prompt_tokens)
            current_span.set_attribute("llm.completion_tokens", completion_tokens)
            current_span.set_attribute("llm.cached_prompt_tokens", cached_tokens)
        if cached_tokens > 0:
            LOGGER.info(
                "%s structured generation cache hit: %d/%d prompt tokens reused",
                self.provider_name,
                cached_tokens,
                prompt_tokens,
            )

    def generate_document_sections(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        section_plans: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> GeneratedSectionBundle:
        return GeneratedSectionBundle.model_validate(
            self._call_and_parse_json(
                span_name=f"{self.provider_name}.generate_document_sections",
                system_prompt=build_document_system_prompt(),
                user_prompt=build_document_user_prompt(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    section_plans=section_plans,
                    sources=sources,
                ),
                max_tokens=2200,
            )
        )

    def generate_reading_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedTextAsset:
        return GeneratedTextAsset.model_validate(
            self._call_and_parse_json(
                span_name=f"{self.provider_name}.generate_reading_asset",
                system_prompt=build_reading_system_prompt(),
                user_prompt=build_reading_user_prompt(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                ),
                max_tokens=1600,
            )
        )

    def generate_slides_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedSlideDeck:
        return GeneratedSlideDeck.model_validate(
            self._call_and_parse_json(
                span_name=f"{self.provider_name}.generate_slides_asset",
                system_prompt=build_slides_system_prompt(),
                user_prompt=build_slides_user_prompt(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                ),
                max_tokens=1800,
            )
        )

    def generate_mindmap_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedMindMap:
        return GeneratedMindMap.model_validate(
            self._call_and_parse_json(
                span_name=f"{self.provider_name}.generate_mindmap_asset",
                system_prompt=build_mindmap_system_prompt(),
                user_prompt=build_mindmap_user_prompt(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                ),
                max_tokens=1600,
            )
        )

    def generate_code_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> GeneratedCodeAsset:
        return GeneratedCodeAsset.model_validate(
            self._call_and_parse_json(
                span_name=f"{self.provider_name}.generate_code_asset",
                system_prompt=build_code_system_prompt(),
                user_prompt=build_code_user_prompt(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                ),
                max_tokens=2200,
            )
        )

    def _call_and_parse_json(
        self,
        *,
        span_name: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with TRACER.start_as_current_span(span_name):
                    response = self._post_chat_completion(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.3,
                        max_tokens=max_tokens,
                    )
                payload = self._extract_message_content(response)
                return self._extract_json(payload)
            except (ValidationError, ValueError, RuntimeError, KeyError, TypeError, httpx.HTTPError) as exc:
                last_error = exc
                LOGGER.warning(
                    "%s structured generation attempt %s failed: %s",
                    self.provider_name,
                    attempt + 1,
                    exc,
                )
                if attempt >= self.max_retries:
                    break
                time.sleep(self.backoff_seconds * (2**attempt))

        raise RuntimeError(f"{self.provider_name} structured generation failed: {last_error}")

    def _extract_message_content(self, response: Any) -> str:
        if not isinstance(response, dict):
            raise RuntimeError(f"unsupported {self.provider_name} response format")
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"missing choices from {self.provider_name} response")
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise RuntimeError(f"missing choice payload from {self.provider_name} response")
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"missing message in {self.provider_name} response")
        content = message.get("content")
        if isinstance(content, list):
            return "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        if isinstance(content, str):
            return content
        raise RuntimeError(f"unsupported {self.provider_name} content format")

    def _extract_json(self, content: str) -> dict[str, Any]:
        fenced_match = re.search(r"```json\s*(\{[\s\S]*\})\s*```", content)
        raw_json = fenced_match.group(1) if fenced_match else content.strip()
        start = raw_json.find("{")
        end = raw_json.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"no json object found in {self.provider_name} output")
        return json.loads(raw_json[start : end + 1])


class ContentGenerationChain:
    """Structured document-content chain with Bailian primary and fallback output."""

    def __init__(
        self,
        primary_generator: SupportsStructuredGenerator | None = None,
    ) -> None:
        self.primary_generator = primary_generator or BailianStructuredGenerator()

    def generate_document_sections(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        section_plans: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedSectionBundle:
        with TRACER.start_as_current_span("content_chain.generate_document_sections"):
            try:
                return self.primary_generator.generate_document_sections(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    section_plans=section_plans,
                    sources=sources,
                )
            except Exception as exc:
                LOGGER.warning("Falling back to deterministic document generation: %s", exc)
                return self._build_fallback_sections(
                    topic=topic,
                    snapshot=snapshot,
                    section_plans=section_plans,
                    fallback_builder=fallback_builder,
                )

    def _build_fallback_sections(
        self,
        *,
        topic: str,
        snapshot: dict[str, Any],
        section_plans: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedSectionBundle:
        sections: list[GeneratedSection] = []
        for index, plan in enumerate(section_plans, start=1):
            sections.append(
                GeneratedSection(
                    title=str(plan.get("title", "")),
                    body=fallback_builder.render_section_paragraph(
                        topic=topic,
                        snapshot=snapshot,
                        section_index=index,
                        plan=plan,
                    ),
                    tips=fallback_builder.render_section_tips(
                        snapshot=snapshot,
                        section_index=index,
                        plan=plan,
                    ),
                    citations=fallback_builder.render_section_citations(plan=plan),
                )
            )
        return GeneratedSectionBundle(sections=sections)

    def generate_reading_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedTextAsset:
        with TRACER.start_as_current_span("content_chain.generate_reading_asset"):
            try:
                return self.primary_generator.generate_reading_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )
            except Exception as exc:
                LOGGER.warning("Falling back to deterministic reading generation: %s", exc)
                return fallback_builder.build_fallback_reading_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )

    def generate_slides_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedSlideDeck:
        with TRACER.start_as_current_span("content_chain.generate_slides_asset"):
            try:
                return self.primary_generator.generate_slides_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )
            except Exception as exc:
                LOGGER.warning("Falling back to deterministic slide generation: %s", exc)
                return fallback_builder.build_fallback_slides_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )

    def generate_mindmap_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedMindMap:
        with TRACER.start_as_current_span("content_chain.generate_mindmap_asset"):
            try:
                return self.primary_generator.generate_mindmap_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )
            except Exception as exc:
                LOGGER.warning("Falling back to deterministic mindmap generation: %s", exc)
                return fallback_builder.build_fallback_mindmap_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )

    def generate_code_asset(
        self,
        *,
        title: str,
        topic: str,
        snapshot: dict[str, Any],
        sources: list[dict[str, Any]],
        fallback_builder: Any,
    ) -> GeneratedCodeAsset:
        with TRACER.start_as_current_span("content_chain.generate_code_asset"):
            try:
                return self.primary_generator.generate_code_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )
            except Exception as exc:
                LOGGER.warning("Falling back to deterministic code generation: %s", exc)
                return fallback_builder.build_fallback_code_asset(
                    title=title,
                    topic=topic,
                    snapshot=snapshot,
                    sources=sources,
                )
