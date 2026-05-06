"""Async + sync MiMo platform client — TTS + Omni multimodal via api-key auth."""

from __future__ import annotations

import base64
import json
import logging
import re
from typing import Any, ClassVar

import httpx
from opentelemetry import trace

from src.ai_modules.config import get_settings

LOGGER = logging.getLogger(__name__)
TRACER = trace.get_tracer(__name__)

MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"


class MiMoClient:
    """Async HTTP client for Xiaomi MiMo platform (api-key auth)."""

    _shared: ClassVar[dict[str, httpx.AsyncClient]] = {}
    _sync_client: ClassVar[httpx.Client | None] = None

    def __init__(self, *, api_key: str | None = None, timeout_seconds: float = 60.0) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.mimo_api_key
        self.base_url = MIMO_BASE_URL
        self.timeout_seconds = timeout_seconds

    async def _get_client(self) -> httpx.AsyncClient:
        key = f"mimo:{self.timeout_seconds}"
        client = self._shared.get(key)
        if client is None or client.is_closed:
            client = httpx.AsyncClient(
                timeout=self.timeout_seconds,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
            self._shared[key] = client
        return client

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None or self._sync_client.is_closed:
            self._sync_client = httpx.Client(timeout=self.timeout_seconds)
        return self._sync_client

    def _headers(self) -> dict[str, str]:
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    # ── TTS ──────────────────────────────────────────────────────

    async def synthesize_speech(
        self,
        *,
        text: str,
        style_description: str = "用清晰自然的语速播报，声音沉稳专业",
        voice: str = "mimo_default",
        audio_format: str = "mp3",
    ) -> bytes:
        """Call MiMo-V2.5-TTS and return raw audio bytes."""
        if not self.api_key:
            raise RuntimeError("missing mimo api key for tts")

        payload: dict[str, Any] = {
            "model": "mimo-v2.5-tts",
            "messages": [
                {"role": "user", "content": style_description},
                {"role": "assistant", "content": text},
            ],
            "audio": {"format": audio_format, "voice": voice},
        }

        with TRACER.start_as_current_span("mimo.tts.synthesize"):
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("mimo tts response missing choices")
        audio_b64 = choices[0].get("message", {}).get("audio", {}).get("data", "")
        if not audio_b64:
            raise RuntimeError("mimo tts response missing audio.data")
        return base64.b64decode(audio_b64)

    # ── Omni Chat (async) ───────────────────────────────────────

    async def omni_chat(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 8192,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call MiMo-V2-Omni for multimodal generation."""
        if not self.api_key:
            raise RuntimeError("missing mimo api key for omni")

        payload: dict[str, Any] = {
            "model": "mimo-v2-omni",
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if response_format:
            payload["response_format"] = response_format

        with TRACER.start_as_current_span("mimo.omni.chat"):
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("mimo omni response missing choices")
        return data

    # ── Omni Chat (sync) ────────────────────────────────────────

    def omni_chat_sync(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict[str, Any]:
        """Synchronous wrapper for omni_chat using httpx.Client."""
        if not self.api_key:
            raise RuntimeError("missing mimo api key for omni")

        payload: dict[str, Any] = {
            "model": "mimo-v2-omni",
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        with TRACER.start_as_current_span("mimo.omni.chat_sync"):
            client = self._get_sync_client()
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("mimo omni response missing choices")
        return data

    def extract_content(self, response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices", [])
        if not choices:
            raise RuntimeError("missing choices")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content)

    def extract_json(self, response_json: dict[str, Any]) -> dict[str, Any]:
        content = self.extract_content(response_json)
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if match:
            return json.loads(match.group(1))
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            return json.loads(content[start : end + 1])
        raise ValueError(f"no json found in omni response: {content[:200]}")
