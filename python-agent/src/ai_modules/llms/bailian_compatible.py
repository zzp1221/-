"""Backward-compatible import shim for the old provider-specific module name."""

from src.ai_modules.llms.openai_compatible import (
    BailianCompatibleClient,
    BailianCompatibleToolCallingLLM,
    OpenAICompatibleClient,
    OpenAICompatibleToolCallingLLM,
)
