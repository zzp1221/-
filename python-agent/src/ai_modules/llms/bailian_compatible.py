"""Async Bailian compatible-mode client helpers."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, ClassVar

import httpx
from opentelemetry import trace

from src.ai_modules.config import get_settings
from src.ai_modules.runtime import AssistantTurn, ToolCall

LOGGER = logging.getLogger(__name__)
TRACER = trace.get_tracer(__name__)


class BailianCompatibleClient:
    """Small async client for Bailian OpenAI-compatible chat completions."""

    _shared_clients: ClassVar[dict[str, httpx.AsyncClient]] = {}

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.bailian_api_key
        self.base_url = (base_url or settings.bailian_base_url).rstrip("/")
        self.model_name = model_name or settings.model_name
        self.timeout_seconds = timeout_seconds
        self.provider_name = "bailian"

    async def _get_client(self) -> httpx.AsyncClient:
        client_key = f"{self.provider_name}:{self.base_url}:{self.timeout_seconds}"
        client = self._shared_clients.get(client_key)
        if client is None or client.is_closed:
            client = httpx.AsyncClient(
                timeout=self.timeout_seconds,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
            self._shared_clients[client_key] = client
        return client

    def _extract_cached_tokens(self, usage: dict[str, Any]) -> int:
        details = usage.get("prompt_tokens_details", {})
        if isinstance(details, dict):
            cached_tokens = details.get("cached_tokens", 0)
            if isinstance(cached_tokens, int):
                return cached_tokens
        return 0

    def _record_usage(self, data: dict[str, Any]) -> None:
        usage = data.get("usage", {})
        if not isinstance(usage, dict):
            return
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        cached_tokens = self._extract_cached_tokens(usage)
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attribute("llm.provider", self.provider_name)
            current_span.set_attribute("llm.model_name", self.model_name)
            current_span.set_attribute("llm.prompt_tokens", prompt_tokens)
            current_span.set_attribute("llm.completion_tokens", completion_tokens)
            current_span.set_attribute("llm.cached_prompt_tokens", cached_tokens)
        if cached_tokens > 0:
            LOGGER.info(
                "%s prompt cache hit: %d/%d prompt tokens reused",
                self.provider_name,
                cached_tokens,
                prompt_tokens,
            )

    async def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        model_name: str | None = None,
        temperature: float = 0.2,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("missing bailian api key")

        payload: dict[str, Any] = {
            "model": model_name or self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if response_format:
            payload["response_format"] = response_format
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with TRACER.start_as_current_span("bailian.compatible.chat_completion"):
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            self._record_usage(data)

        if not data.get("choices"):
            raise RuntimeError("missing choices from bailian compatible response")
        return data

    def extract_message(self, response_json: dict[str, Any]) -> dict[str, Any]:
        choices = response_json.get("choices", [])
        if not choices:
            raise RuntimeError("missing choices")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise RuntimeError("missing message")
        return message

    def extract_content(self, message: dict[str, Any]) -> str:
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content)

    def extract_tool_calls(self, message: dict[str, Any]) -> list[ToolCall]:
        raw_tool_calls = message.get("tool_calls") or []
        calls: list[ToolCall] = []
        for raw_call in raw_tool_calls:
            if not isinstance(raw_call, dict):
                continue
            function_payload = raw_call.get("function", {})
            arguments = function_payload.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"raw": arguments}
            calls.append(
                ToolCall(
                    id=str(raw_call.get("id", function_payload.get("name", "tool_call"))),
                    name=str(function_payload.get("name", "")),
                    input=arguments if isinstance(arguments, dict) else {},
                )
            )
        return calls

    def parse_json_text(self, content: str) -> dict[str, Any]:
        fenced_match = re.search(r"```json\s*(\{[\s\S]*\})\s*```", content)
        raw_json = fenced_match.group(1) if fenced_match else content.strip()
        start = raw_json.find("{")
        end = raw_json.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("no json object found")
        return json.loads(raw_json[start : end + 1])


class BailianCompatibleToolCallingLLM:
    """Tool-calling adapter over Bailian compatible-mode chat completions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.client = BailianCompatibleClient(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
        )
        self.temperature = temperature

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        payload_messages = [
            {"role": "system", "content": system_prompt},
            *self._normalize_messages(messages),
        ]
        response = await self.client.chat_completion(
            messages=payload_messages,
            tools=tools,
            temperature=self.temperature,
        )
        message = self.client.extract_message(response)
        return AssistantTurn(
            content=self.client.extract_content(message),
            tool_calls=self.client.extract_tool_calls(message),
        )

    def _normalize_messages(
        self,
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized_messages: list[dict[str, Any]] = []
        for message in messages:
            role = str(message.get("role", "user"))
            if role == "assistant":
                normalized_messages.append(self._normalize_assistant_message(message))
                continue
            if role == "tool":
                normalized_messages.append(self._normalize_tool_message(message))
                continue
            normalized_messages.append(
                {
                    "role": role,
                    "content": self._stringify_content(message.get("content", "")),
                }
            )
        return normalized_messages

    def _normalize_assistant_message(self, message: dict[str, Any]) -> dict[str, Any]:
        tool_calls = message.get("tool_calls") or []
        normalized_tool_calls: list[dict[str, Any]] = []
        for raw_call in tool_calls:
            if not isinstance(raw_call, dict):
                continue
            if "function" in raw_call:
                normalized_tool_calls.append(raw_call)
                continue
            normalized_tool_calls.append(
                {
                    "id": str(raw_call.get("id", "tool_call")),
                    "type": "function",
                    "function": {
                        "name": str(raw_call.get("name", "")),
                        "arguments": self._stringify_arguments(raw_call.get("input", {})),
                    },
                }
            )
        payload = {
            "role": "assistant",
            "content": self._stringify_content(message.get("content", "")),
        }
        if normalized_tool_calls:
            payload["tool_calls"] = normalized_tool_calls
        return payload

    def _normalize_tool_message(self, message: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "role": "tool",
            "content": self._stringify_content(message.get("content", "")),
            "tool_call_id": str(message.get("tool_call_id", "")),
        }
        if message.get("name"):
            payload["name"] = str(message["name"])
        return payload

    def _stringify_arguments(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _stringify_content(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)
