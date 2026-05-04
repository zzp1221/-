"""Async Spark OpenAI-compatible client helpers."""

from __future__ import annotations

from src.ai_modules.config import get_settings
from src.ai_modules.llms.bailian_compatible import (
    BailianCompatibleClient,
    BailianCompatibleToolCallingLLM,
)


class SparkCompatibleClient(BailianCompatibleClient):
    """Small async client for Spark OpenAI-compatible chat completions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        settings = get_settings()
        super().__init__(
            api_key=api_key or settings.spark_api_key,
            base_url=base_url or settings.spark_base_url,
            model_name=model_name or settings.spark_model_name,
            timeout_seconds=timeout_seconds,
        )
        self.provider_name = "spark"


class SparkCompatibleToolCallingLLM(BailianCompatibleToolCallingLLM):
    """Tool-calling adapter over Spark OpenAI-compatible chat completions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.client = SparkCompatibleClient(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
        )
        self.temperature = temperature
