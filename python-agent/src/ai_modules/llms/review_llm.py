"""LLM adapters used by critic and safety review agents."""

from __future__ import annotations

import json
from typing import Any

from src.ai_modules.config import get_settings
from src.ai_modules.llms.agent_models import BailianJSONGenerator, create_tool_calling_llm
from src.ai_modules.llms.bailian_compatible import BailianCompatibleToolCallingLLM
from src.ai_modules.models import CriticReviewPayload, SafetyReviewPayload
from src.ai_modules.runtime import AssistantTurn, ToolCall


class RuleBasedReviewLLM:
    """Deterministic fallback LLM that preserves review tool sequencing."""

    _TOOL_SEQUENCE = (
        "check_fact_consistency",
        "check_difficulty_match",
        "review_source_coverage",
        "classify_content",
        "detect_boundary_risk",
        "filter_academic_misconduct",
        "synthesize_review",
    )

    async def complete(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> AssistantTurn:
        del system_prompt
        available_tools = {
            str(tool.get("function", {}).get("name"))
            for tool in tools
            if isinstance(tool, dict)
        }
        executed_tools = [
            str(message.get("name"))
            for message in messages
            if message.get("role") == "tool"
        ]

        for tool_name in self._TOOL_SEQUENCE:
            if tool_name in available_tools and tool_name not in executed_tools:
                return AssistantTurn(
                    content=f"调用 {tool_name} 完成复核步骤。",
                    tool_calls=[
                        ToolCall(
                            id=f"call_{tool_name}",
                            name=tool_name,
                            input=self._build_tool_input(tool_name=tool_name, messages=messages),
                        )
                    ],
                )

        latest_tool_content = self._latest_tool_content(messages)
        if isinstance(latest_tool_content, dict) and latest_tool_content.get("summaryText"):
            return AssistantTurn(content=str(latest_tool_content["summaryText"]))
        return AssistantTurn(content="复核完成。")

    def _build_tool_input(
        self,
        *,
        tool_name: str,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if tool_name == "synthesize_review":
            latest_tool_content = self._latest_tool_content(messages)
            return latest_tool_content if isinstance(latest_tool_content, dict) else {}
        return {}

    def _latest_tool_content(self, messages: list[dict[str, Any]]) -> Any:
        for message in reversed(messages):
            if message.get("role") == "tool":
                return message.get("content")
        return {}


class BailianCriticReviewer:
    """Generate the final structured critic review with the active provider."""

    def __init__(self) -> None:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("review_llm")
        model_name = settings.resolve_component_model(
            "review_llm",
            default_logical_model="main_chat_model",
            provider_name=provider_name,
        )
        self.generator = BailianJSONGenerator(
            model_name=model_name,
            provider_name=provider_name,
            temperature=0.1,
        )

    async def review(
        self,
        *,
        system_prompt: str,
        context_payload: dict[str, Any],
    ) -> CriticReviewPayload:
        payload = await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=(
                "请根据以下教学资源复核证据生成 Critic 审核结论，并只返回 JSON。\n"
                f"{json.dumps(context_payload, ensure_ascii=False)}"
            ),
            max_tokens=1200,
        )
        return CriticReviewPayload.model_validate(payload)


class BailianSafetyReviewer:
    """Generate the final structured safety review with the active provider."""

    def __init__(self) -> None:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("safety_llm")
        model_name = settings.resolve_component_model(
            "safety_llm",
            default_logical_model="safety_model",
            provider_name=provider_name,
        )
        self.generator = BailianJSONGenerator(
            model_name=model_name,
            provider_name=provider_name,
            temperature=0.1,
        )

    async def review(
        self,
        *,
        system_prompt: str,
        context_payload: dict[str, Any],
    ) -> SafetyReviewPayload:
        payload = await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=(
                "请根据以下教学资源安全证据生成 Safety 审核结论，并只返回 JSON。\n"
                f"{json.dumps(context_payload, ensure_ascii=False)}"
            ),
            max_tokens=1200,
        )
        return SafetyReviewPayload.model_validate(payload)


class ReviewLLMClientFactory:
    """Create the review LLM client with Bailian primary and rule fallback."""

    @staticmethod
    def create() -> Any:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("review_llm")
        if settings.provider_ready(provider_name):
            model_name = settings.resolve_component_model(
                "review_llm",
                default_logical_model="reasoning_model",
                provider_name=provider_name,
            )
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedReviewLLM()


CriticReviewer = BailianCriticReviewer
SafetyReviewer = BailianSafetyReviewer
