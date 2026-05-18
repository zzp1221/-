"""批评审查和安全审查 Agent 使用的 LLM 适配器。"""

from __future__ import annotations

import json
from typing import Any

from src.ai_modules.config import get_settings
from src.ai_modules.llms.agent_models import OpenAICompatibleJSONGenerator, create_tool_calling_llm
from src.ai_modules.models import CriticReviewPayload, SafetyReviewPayload
from src.ai_modules.runtime import AssistantTurn, ToolCall


class RuleBasedReviewLLM:
    """保持审查工具调用顺序的确定性回退 LLM。"""

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


class OpenAICompatibleCriticReviewer:
    """使用活跃提供商生成最终结构化批评审查结论。"""

    def __init__(self) -> None:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("review_llm")
        if not settings.provider_ready(provider_name):
            raise RuntimeError("review_llm provider is not ready")
        model_name = settings.resolve_component_model(
            "review_llm",
            default_logical_model="main_chat_model",
            provider_name=provider_name,
        )
        self.generator = OpenAICompatibleJSONGenerator(
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
        payload = _normalize_critic_payload(payload)
        return CriticReviewPayload.model_validate(payload)


class OpenAICompatibleSafetyReviewer:
    """使用活跃提供商生成最终结构化安全审查结论。"""

    def __init__(self) -> None:
        settings = get_settings()
        provider_name = settings.resolve_component_provider("safety_llm")
        if not settings.provider_ready(provider_name):
            raise RuntimeError("safety_llm provider is not ready")
        model_name = settings.resolve_component_model(
            "safety_llm",
            default_logical_model="safety_model",
            provider_name=provider_name,
        )
        self.generator = OpenAICompatibleJSONGenerator(
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


def _normalize_critic_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for field in ("factConsistency", "difficultyMatch", "sourceCoverage"):
        value = normalized.get(field)
        if isinstance(value, dict):
            normalized[field] = _stringify_review_signal(value)
    return normalized


def _stringify_review_signal(value: dict[str, Any]) -> str:
    parts: list[str] = []
    status = value.get("status")
    if isinstance(status, str) and status.strip():
        parts.append(f"状态: {status.strip()}")
    issues = value.get("issues")
    if isinstance(issues, list):
        normalized_issues = [str(item).strip() for item in issues if str(item).strip()]
        if normalized_issues:
            parts.append(f"问题: {'；'.join(normalized_issues[:3])}")
    evidence = value.get("evidence")
    if isinstance(evidence, dict):
        evidence_parts = [f"{key}={evidence[key]}" for key in evidence if evidence[key] is not None]
        if evidence_parts:
            parts.append(f"证据: {', '.join(evidence_parts[:4])}")
    if not parts:
        return json.dumps(value, ensure_ascii=False)
    return "；".join(parts)


class ReviewLLMClientFactory:
    """创建审查 LLM 客户端，支持 OpenAI 兼容主模型和规则回退。"""

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


CriticReviewer = OpenAICompatibleCriticReviewer
SafetyReviewer = OpenAICompatibleSafetyReviewer

BailianCriticReviewer = OpenAICompatibleCriticReviewer
BailianSafetyReviewer = OpenAICompatibleSafetyReviewer
