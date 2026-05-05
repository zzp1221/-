"""Provider-aware structured helpers and model-selection factories."""

from __future__ import annotations

import json
from typing import Any

from src.ai_modules.config import get_settings
from src.ai_modules.llms.openai_compatible import OpenAICompatibleClient
from src.ai_modules.llms.spark_compatible import (
    SparkCompatibleClient,
    SparkCompatibleToolCallingLLM,
)
from src.ai_modules.llms.practice_llm import RuleBasedJudgeLLM, RuleBasedPracticeLLM
from src.ai_modules.llms.profile_llm import RuleBasedProfileLLM
from src.ai_modules.llms.tutor_llm import OpenAICompatibleTutorLLM, RuleBasedTutorLLM
from src.ai_modules.models import (
    EvaluationPayload,
    JudgeItemResult,
    LearningPlanPayload,
    LearnerProfileDimensions,
    PracticeQuestion,
    QueryRewriteResult,
    QuestionBatchPayload,
    RetrievalResponse,
)


def _provider_name() -> str:
    return get_settings().runtime_provider_name()


def _primary_model_name() -> str:
    return get_settings().resolve_logical_model("main_chat_model")


def _fast_model_name() -> str:
    return get_settings().resolve_logical_model("fast_model")


def _has_provider_api_key() -> bool:
    return get_settings().provider_ready()


def _resolve_component_binding(
    component_name: str,
    *,
    default_logical_model: str,
) -> tuple[str, str]:
    settings = get_settings()
    provider_name = settings.resolve_component_provider(component_name)
    model_name = settings.resolve_component_model(
        component_name,
        default_logical_model=default_logical_model,
        provider_name=provider_name,
    )
    return provider_name, model_name


def _component_provider_ready(component_name: str) -> bool:
    settings = get_settings()
    return settings.provider_ready(settings.resolve_component_provider(component_name))


def create_compatible_client(
    *,
    model_name: str | None = None,
    provider_name: str | None = None,
) -> Any:
    """Build the currently configured OpenAI-compatible client."""

    resolved_provider = (provider_name or _provider_name()).strip().lower()
    if resolved_provider == "spark":
        return SparkCompatibleClient(model_name=model_name or _primary_model_name())
    return OpenAICompatibleClient(model_name=model_name or _primary_model_name())


def create_tool_calling_llm(
    *,
    model_name: str | None = None,
    provider_name: str | None = None,
) -> Any:
    """Build the currently configured tool-calling LLM adapter."""

    resolved_provider = (provider_name or _provider_name()).strip().lower()
    if resolved_provider == "spark":
        return SparkCompatibleToolCallingLLM(model_name=model_name or _primary_model_name())
    return OpenAICompatibleTutorLLM(model_name=model_name or _primary_model_name())


class OpenAICompatibleJSONGenerator:
    """Generate structured JSON with the active OpenAI-compatible provider."""

    def __init__(
        self,
        *,
        model_name: str | None = None,
        provider_name: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.client = create_compatible_client(model_name=model_name, provider_name=provider_name)
        self.temperature = temperature

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model_name: str | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        response = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model_name=model_name,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        message = self.client.extract_message(response)
        return self.client.parse_json_text(self.client.extract_content(message))


class OpenAICompatibleQueryRewriteGenerator:
    """Use a lightweight OpenAI-compatible model to rewrite retrieval queries."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("query_rewrite_llm", default_logical_model="fast_model")
        self.generator = OpenAICompatibleJSONGenerator(
            model_name=model_name,
            provider_name=provider_name,
            temperature=0.1,
        )

    async def rewrite(
        self,
        *,
        system_prompt: str,
        original_query: str,
        learning_context: dict[str, Any],
    ) -> QueryRewriteResult:
        payload = await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt="\n".join(
                [
                    f"原始问题: {original_query}",
                    f"学习上下文: {json.dumps(learning_context, ensure_ascii=False)}",
                    "请返回 JSON。",
                ]
            ),
            max_tokens=400,
        )
        return QueryRewriteResult.model_validate(payload)


class OpenAICompatibleRetrievalSummaryGenerator:
    """Use a lightweight OpenAI-compatible model to summarize retrieval evidence."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("retrieval_llm", default_logical_model="fast_model")
        self.client = create_compatible_client(model_name=model_name, provider_name=provider_name)

    async def summarize(
        self,
        *,
        system_prompt: str,
        retrieval_response: RetrievalResponse,
    ) -> str:
        response = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": "\n".join(
                        [
                            f"查询: {retrieval_response.rewritten_query}",
                            f"候选文档: {json.dumps(retrieval_response.model_dump(by_alias=True), ensure_ascii=False)}",
                            "请输出 1-2 句中文摘要，不要返回 JSON。",
                        ]
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=220,
        )
        return self.client.extract_content(self.client.extract_message(response)).strip()


class OpenAICompatibleEvaluationGenerator:
    """Generate structured learner evaluation with the primary provider model."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("evaluation_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(model_name=model_name, provider_name=provider_name)

    async def evaluate(
        self,
        *,
        system_prompt: str,
        context_payload: dict[str, Any],
    ) -> EvaluationPayload:
        payload = await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=(
                "请结合以下上下文评估学生当前水平，并只返回 JSON。\n"
                f"{json.dumps(context_payload, ensure_ascii=False)}"
            ),
            max_tokens=1200,
        )
        return EvaluationPayload.model_validate(payload)


class OpenAICompatibleLearningPathGenerator:
    """Generate structured learning path with the primary provider model."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("path_planning_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(model_name=model_name, provider_name=provider_name)

    async def plan(
        self,
        *,
        system_prompt: str,
        context_payload: dict[str, Any],
    ) -> LearningPlanPayload:
        payload = await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=(
                "请根据以下上下文制定学习路径，并只返回 JSON。\n"
                f"{json.dumps(context_payload, ensure_ascii=False)}"
            ),
            max_tokens=1400,
        )
        return LearningPlanPayload.model_validate(payload)


class OpenAICompatiblePracticeQuestionGenerator:
    """Generate a structured practice batch with the primary provider model."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("practice_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(model_name=model_name, provider_name=provider_name)

    async def generate_batch(
        self,
        *,
        topic: str,
        difficulty: str,
        count: int,
        learning_context: dict[str, Any],
    ) -> QuestionBatchPayload:
        payload = await self.generator.generate(
            system_prompt=(
                "你是教学系统中的 Practice Agent。"
                "请围绕指定主题生成高质量中文练习题。"
                "输出必须是 JSON，结构为 "
                '{"title":"...","topic":"...","difficulty":"...","questions":'
                '[{"questionId":"q1","questionType":"SINGLE_CHOICE或SHORT_ANSWER","stem":"...",'
                '"options":["..."],"answer":"...","knowledgeTags":["..."],'
                '"difficultyLevel":"...","explanation":"..."}]}.'
            ),
            user_prompt="\n".join(
                [
                    f"主题: {topic}",
                    f"难度: {difficulty}",
                    f"题量: {count}",
                    f"学习上下文: {json.dumps(learning_context, ensure_ascii=False)}",
                    "要求同时覆盖概念、条件判断、易错点和自测/迁移。",
                ]
            ),
            max_tokens=1800,
        )
        batch = QuestionBatchPayload.model_validate(payload)
        normalized_questions = []
        for index, question in enumerate(batch.questions[:count], start=1):
            normalized_question = question.model_copy(update={"question_id": f"q{index}"})
            normalized_questions.append(normalized_question)
        return batch.model_copy(update={"questions": normalized_questions})


class OpenAICompatibleObjectiveJudgeGenerator:
    """Use the active provider to judge objective questions and return structured results."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("judge_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(
            model_name=model_name,
            provider_name=provider_name,
            temperature=0.1,
        )

    async def judge(
        self,
        *,
        questions: list[PracticeQuestion],
        answers: dict[str, str],
    ) -> dict[str, Any]:
        payload = await self.generator.generate(
            system_prompt=(
                "你是教学系统中的 Judge Agent。"
                "请对客观题判题，并只返回 JSON。"
                '结构为 {"items":[{"questionId":"...","questionType":"...","learnerAnswer":"...",'
                '"correctAnswer":"...","isCorrect":true,"score":20.0,"knowledgeTags":["..."],'
                '"reason":"...","feedback":"...","profileDelta":{"confidenceLevel":"LOW或MEDIUM","weakPoints":["..."]}}],'
                '"pendingSubjective":[{PracticeQuestion原样对象}]}.'
                "SHORT_ANSWER 题不要判分，原样放入 pendingSubjective。"
            ),
            user_prompt=json.dumps(
                {
                    "questions": [question.model_dump(by_alias=True) for question in questions],
                    "answers": answers,
                },
                ensure_ascii=False,
            ),
            max_tokens=2200,
        )
        payload["items"] = [
            JudgeItemResult.model_validate(item).model_dump(by_alias=True)
            for item in payload.get("items", [])
        ]
        payload["pendingSubjective"] = [
            PracticeQuestion.model_validate(item).model_dump(by_alias=True)
            for item in payload.get("pendingSubjective", [])
        ]
        return payload


class OpenAICompatibleJudgeFeedbackGenerator:
    """Generate the final judging summary with the primary provider model."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("judge_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(
            model_name=model_name,
            provider_name=provider_name,
            temperature=0.2,
        )

    async def summarize(
        self,
        *,
        items: list[JudgeItemResult],
        topic: str,
    ) -> dict[str, Any]:
        payload = await self.generator.generate(
            system_prompt=(
                "你是教学系统中的 Judge Agent。"
                "请基于逐题判题结果汇总整体反馈，只返回 JSON。"
                '结构为 {"summary":"...","totalScore":0.0,"accuracy":0.0,"items":[...],"weakKnowledgeTags":["..."]}。'
                "accuracy 取值 0 到 1。summary 要用中文完整表述。"
            ),
            user_prompt=json.dumps(
                {
                    "topic": topic,
                    "items": [item.model_dump(by_alias=True) for item in items],
                },
                ensure_ascii=False,
            ),
            max_tokens=1400,
        )
        payload["items"] = [
            JudgeItemResult.model_validate(item).model_dump(by_alias=True)
            for item in payload.get("items", [])
        ]
        return payload


class OpenAICompatibleProfileAnalyzer:
    """Extract learner profile dimensions with the primary provider model."""

    def __init__(self) -> None:
        provider_name, model_name = _resolve_component_binding("profile_llm", default_logical_model="main_chat_model")
        self.generator = OpenAICompatibleJSONGenerator(model_name=model_name, provider_name=provider_name)

    async def analyze(
        self,
        *,
        context_payload: dict[str, Any],
    ) -> LearnerProfileDimensions:
        payload = await self.generator.generate(
            system_prompt=(
                "你是教学系统中的 Profile Agent。"
                "请根据对话、结构化摘要、练习与判题信息抽取学生画像。"
                "输出必须是 JSON，字段为 "
                '{"knowledgeFoundation":"...","learningGoal":"...","professionalBackground":"...",'
                '"learningPreference":"...","cognitiveStyle":"...","weakPoints":["..."],'
                '"learningPace":"...","confidenceLevel":"...","source":"...","summaryText":"..."}。'
            ),
            user_prompt=json.dumps(context_payload, ensure_ascii=False),
            max_tokens=1400,
        )
        return LearnerProfileDimensions.model_validate(payload)


# Provider-neutral aliases used by current agents.
StructuredJSONGenerator = OpenAICompatibleJSONGenerator
QueryRewriteGenerator = OpenAICompatibleQueryRewriteGenerator
RetrievalSummaryGenerator = OpenAICompatibleRetrievalSummaryGenerator
EvaluationGenerator = OpenAICompatibleEvaluationGenerator
LearningPathGenerator = OpenAICompatibleLearningPathGenerator
PracticeQuestionGenerator = OpenAICompatiblePracticeQuestionGenerator
ObjectiveJudgeGenerator = OpenAICompatibleObjectiveJudgeGenerator
JudgeFeedbackGenerator = OpenAICompatibleJudgeFeedbackGenerator
ProfileAnalyzer = OpenAICompatibleProfileAnalyzer

BailianJSONGenerator = OpenAICompatibleJSONGenerator
BailianQueryRewriteGenerator = OpenAICompatibleQueryRewriteGenerator
BailianRetrievalSummaryGenerator = OpenAICompatibleRetrievalSummaryGenerator
BailianEvaluationGenerator = OpenAICompatibleEvaluationGenerator
BailianLearningPathGenerator = OpenAICompatibleLearningPathGenerator
BailianPracticeQuestionGenerator = OpenAICompatiblePracticeQuestionGenerator
BailianObjectiveJudgeGenerator = OpenAICompatibleObjectiveJudgeGenerator
BailianJudgeFeedbackGenerator = OpenAICompatibleJudgeFeedbackGenerator
BailianProfileAnalyzer = OpenAICompatibleProfileAnalyzer


class PracticeLLMClientFactory:
    """Create the Practice Agent LLM with provider routing and rule fallback."""

    @staticmethod
    def create() -> Any:
        if _component_provider_ready("practice_llm"):
            provider_name, model_name = _resolve_component_binding("practice_llm", default_logical_model="main_chat_model")
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedPracticeLLM()


class JudgeLLMClientFactory:
    """Create the Judge Agent LLM with provider routing and rule fallback."""

    @staticmethod
    def create() -> Any:
        if _component_provider_ready("judge_llm"):
            provider_name, model_name = _resolve_component_binding("judge_llm", default_logical_model="main_chat_model")
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedJudgeLLM()


class ProfileLLMClientFactory:
    """Create the Profile Agent LLM with provider routing and rule fallback."""

    @staticmethod
    def create() -> Any:
        if _component_provider_ready("profile_llm"):
            provider_name, model_name = _resolve_component_binding("profile_llm", default_logical_model="main_chat_model")
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedProfileLLM()


class TutorToolLLMClientFactory:
    """Create the Tutor Agent LLM with provider routing and rule fallback."""

    @staticmethod
    def create() -> Any:
        if _component_provider_ready("tutor_llm"):
            provider_name, model_name = _resolve_component_binding("tutor_llm", default_logical_model="main_chat_model")
            return create_tool_calling_llm(model_name=model_name, provider_name=provider_name)
        return RuleBasedTutorLLM()
