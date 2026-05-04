from pathlib import Path

import pytest

from src.ai_modules.config import Settings
from src.ai_modules.llms import agent_models, planning_llm, review_llm, tutor_llm, workflow_llm
from src.ai_modules.llms.agent_models import (
    BailianEvaluationGenerator,
    BailianProfileAnalyzer,
    BailianQueryRewriteGenerator,
    JudgeLLMClientFactory,
    PracticeLLMClientFactory,
    ProfileLLMClientFactory,
    TutorToolLLMClientFactory,
)
from src.ai_modules.llms.bailian_compatible import BailianCompatibleToolCallingLLM
from src.ai_modules.llms.judge_subjective_evaluator import BailianSubjectiveJudgeEvaluator
from src.ai_modules.llms.planning_llm import PlanningLLMClientFactory, RuleBasedPlanningLLM
from src.ai_modules.llms.practice_llm import RuleBasedJudgeLLM, RuleBasedPracticeLLM
from src.ai_modules.llms.profile_llm import RuleBasedProfileLLM
from src.ai_modules.llms.review_llm import ReviewLLMClientFactory, RuleBasedReviewLLM
from src.ai_modules.llms.spark_compatible import SparkCompatibleToolCallingLLM
from src.ai_modules.llms.tutor_llm import RuleBasedTutorLLM, TutorLLMClientFactory
from src.ai_modules.llms.workflow_llm import (
    GenerationToolLLMClientFactory,
    QueryRewriteToolLLMClientFactory,
    RetrievalToolLLMClientFactory,
    RuleBasedGenerationLLM,
    RuleBasedQueryRewriteLLM,
    RuleBasedRetrievalLLM,
)


def test_settings_build_default_model_routing_config() -> None:
    settings = Settings(
        ACTIVE_PROVIDER="bailian",
        MODEL_NAME="qwen3.6-plus",
        FAST_MODEL_NAME="qwen3.6-flash",
        REASONING_MODEL_NAME="qwen3.6-max-preview",
        CODE_MODEL_NAME="qwen3-coder-plus",
        CODE_FAST_MODEL_NAME="qwen3-coder-next",
        OMNI_MODEL_NAME="qwen3.5-omni-plus",
        OMNI_REALTIME_MODEL_NAME="qwen3.5-omni-plus-realtime",
        EMBEDDING_MODEL_NAME="text-embedding-v4",
        RERANK_MODEL_NAME="qwen3-rerank",
        SAFETY_MODEL_NAME="qwen3.6-flash",
        SPARK_MODEL_NAME="Spark Ultra",
        SPARK_FAST_MODEL_NAME="Spark X2-Flash",
    )

    routing = settings.build_default_model_routing_config()

    assert routing.active_provider == "bailian"
    assert routing.resolve_model("main_chat_model") == "qwen3.6-plus"
    assert routing.resolve_model("fast_model", "spark") == "Spark X2-Flash"


def test_settings_loads_model_routing_config_from_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "model-provider.yaml"
    config_path.write_text(
        "\n".join(
            [
                "activeProvider: spark",
                "fallbackProvider: bailian",
                "ttsProvider: xfyun_tts",
                "avatarProvider: xfyun_avatar",
                "providers:",
                "  spark:",
                "    name: spark",
                "    protocol: spark_compatible",
                "    baseUrl: https://spark-api.xf-yun.com",
                "    apiKeyEnv: SPARK_API_KEY",
                "    models:",
                "      main_chat_model: Spark Ultra",
                "  bailian:",
                "    name: bailian",
                "    protocol: openai_compatible",
                "    baseUrl: https://dashscope.aliyuncs.com/compatible-mode/v1",
                "    apiKeyEnv: BAILIAN_API_KEY",
                "    models:",
                "      main_chat_model: qwen3.6-plus",
            ]
        ),
        encoding="utf-8",
    )
    settings = Settings(MODEL_ROUTING_CONFIG_PATH=str(config_path))

    routing = settings.model_routing_config()

    assert routing.active_provider == "spark"
    assert routing.fallback_provider == "bailian"
    assert settings.resolve_logical_model("main_chat_model") == "Spark Ultra"


def test_settings_provider_ready_for_spark_requires_api_key() -> None:
    settings = Settings(ACTIVE_PROVIDER="spark", SPARK_API_KEY="", BAILIAN_API_KEY="test")

    assert settings.selected_provider_name() == "spark"
    assert settings.provider_ready() is False


def test_settings_resolve_unknown_model_raises_key_error() -> None:
    settings = Settings()

    with pytest.raises(KeyError):
        settings.resolve_logical_model("unknown_model")


def test_settings_component_override_resolves_provider_and_model() -> None:
    settings = Settings(
        ACTIVE_PROVIDER="bailian",
        BAILIAN_API_KEY="bailian-key",
        SPARK_API_KEY="spark-key",
        query_rewrite_llm={"provider": "spark", "model": "fast_model"},
    )

    provider_name = settings.resolve_component_provider("query_rewrite_llm")
    model_name = settings.resolve_component_model(
        "query_rewrite_llm",
        default_logical_model="main_chat_model",
        provider_name=provider_name,
    )

    assert provider_name == "spark"
    assert model_name == settings.spark_fast_model_name


def test_settings_component_override_accepts_literal_model_name() -> None:
    settings = Settings(
        ACTIVE_PROVIDER="bailian",
        BAILIAN_API_KEY="bailian-key",
        evaluation_llm={"model": "custom-eval-model"},
    )

    assert settings.resolve_component_model("evaluation_llm", default_logical_model="main_chat_model") == "custom-eval-model"


def test_tool_orchestration_factories_fallback_to_rule_based_clients_without_provider_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(workflow_llm, "get_settings", lambda: Settings(BAILIAN_API_KEY=""))
    monkeypatch.setattr(tutor_llm, "get_settings", lambda: Settings(BAILIAN_API_KEY=""))
    monkeypatch.setattr(planning_llm, "get_settings", lambda: Settings(BAILIAN_API_KEY=""))
    monkeypatch.setattr(review_llm, "get_settings", lambda: Settings(BAILIAN_API_KEY=""))
    monkeypatch.setattr(agent_models, "get_settings", lambda: Settings(BAILIAN_API_KEY=""))

    assert isinstance(QueryRewriteToolLLMClientFactory.create(), RuleBasedQueryRewriteLLM)
    assert isinstance(RetrievalToolLLMClientFactory.create(), RuleBasedRetrievalLLM)
    assert isinstance(GenerationToolLLMClientFactory.create(), RuleBasedGenerationLLM)
    assert isinstance(PracticeLLMClientFactory.create(), RuleBasedPracticeLLM)
    assert isinstance(JudgeLLMClientFactory.create(), RuleBasedJudgeLLM)
    assert isinstance(ProfileLLMClientFactory.create(), RuleBasedProfileLLM)
    assert isinstance(TutorToolLLMClientFactory.create(), RuleBasedTutorLLM)
    assert isinstance(TutorLLMClientFactory.create(), RuleBasedTutorLLM)
    assert isinstance(PlanningLLMClientFactory.create(), RuleBasedPlanningLLM)
    assert isinstance(ReviewLLMClientFactory.create(), RuleBasedReviewLLM)


def test_tool_orchestration_factories_use_provider_aware_clients_when_provider_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    ready_settings = Settings(BAILIAN_API_KEY="test-key", MODEL_NAME="qwen3.6-plus")
    monkeypatch.setattr(workflow_llm, "get_settings", lambda: ready_settings)
    monkeypatch.setattr(tutor_llm, "get_settings", lambda: ready_settings)
    monkeypatch.setattr(planning_llm, "get_settings", lambda: ready_settings)
    monkeypatch.setattr(review_llm, "get_settings", lambda: ready_settings)
    monkeypatch.setattr(agent_models, "get_settings", lambda: ready_settings)

    assert isinstance(QueryRewriteToolLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(RetrievalToolLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(GenerationToolLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(PracticeLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(JudgeLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(ProfileLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(TutorToolLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(TutorLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(PlanningLLMClientFactory.create(), BailianCompatibleToolCallingLLM)
    assert isinstance(ReviewLLMClientFactory.create(), BailianCompatibleToolCallingLLM)


def test_component_factories_support_component_level_provider_switch(monkeypatch: pytest.MonkeyPatch) -> None:
    spark_settings = Settings(
        ACTIVE_PROVIDER="bailian",
        BAILIAN_API_KEY="bailian-key",
        SPARK_API_KEY="spark-key",
        query_rewrite_llm={"provider": "spark", "model": "fast_model"},
        planning_llm={"provider": "spark", "model": "reasoning_model"},
        judge_llm={"provider": "spark", "model": "fast_model"},
    )
    monkeypatch.setattr(workflow_llm, "get_settings", lambda: spark_settings)
    monkeypatch.setattr(planning_llm, "get_settings", lambda: spark_settings)
    monkeypatch.setattr(agent_models, "get_settings", lambda: spark_settings)

    query_rewrite_llm = QueryRewriteToolLLMClientFactory.create()
    planning_client = PlanningLLMClientFactory.create()
    judge_client = JudgeLLMClientFactory.create()
    query_rewrite_generator = BailianQueryRewriteGenerator()
    evaluation_generator = BailianEvaluationGenerator()
    profile_analyzer = BailianProfileAnalyzer()
    subjective_evaluator = BailianSubjectiveJudgeEvaluator()

    assert isinstance(query_rewrite_llm, SparkCompatibleToolCallingLLM)
    assert isinstance(planning_client, SparkCompatibleToolCallingLLM)
    assert isinstance(judge_client, SparkCompatibleToolCallingLLM)
    assert query_rewrite_llm.client.model_name == spark_settings.spark_fast_model_name
    assert planning_client.client.model_name == spark_settings.spark_reasoning_model_name
    assert judge_client.client.model_name == spark_settings.spark_fast_model_name
    assert query_rewrite_generator.generator.client.provider_name == "spark"
    assert evaluation_generator.generator.client.provider_name == "bailian"
    assert profile_analyzer.generator.client.provider_name == "bailian"
    assert subjective_evaluator.provider_name == "spark"
