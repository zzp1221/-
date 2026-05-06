"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.ai_modules.models import ModelRoutingConfig, ProviderEndpointConfig

PYTHON_AGENT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = PYTHON_AGENT_ROOT.parent


class LLMComponentOverride(BaseModel):
    """Optional provider/model override for a single LLM-backed component."""

    provider: str = ""
    model: str = ""

    model_config = ConfigDict(extra="ignore")


class Settings(BaseSettings):
    """Runtime settings for the Python agent service."""

    model_config = SettingsConfigDict(
        env_file=(
            str(PROJECT_ROOT / ".env"),
            str(PYTHON_AGENT_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = Field(default="zhixue-python-agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    model_provider: str = Field(default="openai_compatible", alias="MODEL_PROVIDER")
    active_provider: str = Field(default="", alias="ACTIVE_PROVIDER")
    fallback_provider: str = Field(default="", alias="FALLBACK_PROVIDER")
    model_routing_config_path: str = Field(default="", alias="MODEL_ROUTING_CONFIG_PATH")
    model_name: str = Field(default="qwen3.6-plus", alias="MODEL_NAME")
    fast_model_name: str = Field(default="qwen3.6-flash", alias="FAST_MODEL_NAME")
    reasoning_model_name: str = Field(default="qwen3.6-max-preview", alias="REASONING_MODEL_NAME")
    code_model_name: str = Field(default="qwen3-coder-plus", alias="CODE_MODEL_NAME")
    code_fast_model_name: str = Field(default="qwen3-coder-next", alias="CODE_FAST_MODEL_NAME")
    omni_model_name: str = Field(default="qwen3.5-omni-plus", alias="OMNI_MODEL_NAME")
    omni_realtime_model_name: str = Field(
        default="qwen3.5-omni-plus-realtime",
        alias="OMNI_REALTIME_MODEL_NAME",
    )
    embedding_model_name: str = Field(default="text-embedding-v4", alias="EMBEDDING_MODEL_NAME")
    rerank_model_name: str = Field(default="qwen3-rerank", alias="RERANK_MODEL_NAME")
    safety_model_name: str = Field(default="qwen3.6-flash", alias="SAFETY_MODEL_NAME")
    openai_compatible_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_COMPATIBLE_API_KEY", "BAILIAN_API_KEY"),
    )
    openai_compatible_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        validation_alias=AliasChoices("OPENAI_COMPATIBLE_BASE_URL", "BAILIAN_BASE_URL"),
    )
    spark_api_key: str = Field(default="", alias="SPARK_API_KEY")
    spark_app_id: str = Field(default="", alias="SPARK_APP_ID")
    spark_api_secret: str = Field(default="", alias="SPARK_API_SECRET")
    spark_base_url: str = Field(
        default="https://spark-api-open.xf-yun.com/v1",
        alias="SPARK_BASE_URL",
    )
    spark_model_name: str = Field(default="4.0Ultra", alias="SPARK_MODEL_NAME")
    spark_fast_model_name: str = Field(
        default="generalv3.5",
        alias="SPARK_FAST_MODEL_NAME",
    )
    spark_reasoning_model_name: str = Field(default="Spark X2", alias="SPARK_REASONING_MODEL_NAME")
    spark_code_model_name: str = Field(default="Spark X2-Flash", alias="SPARK_CODE_MODEL_NAME")
    spark_code_fast_model_name: str = Field(
        default="Spark X2-Flash",
        alias="SPARK_CODE_FAST_MODEL_NAME",
    )
    spark_omni_model_name: str = Field(default="Spark Ultra", alias="SPARK_OMNI_MODEL_NAME")
    spark_omni_realtime_model_name: str = Field(
        default="Spark X2-Flash",
        alias="SPARK_OMNI_REALTIME_MODEL_NAME",
    )
    spark_embedding_model_name: str = Field(
        default="spark-embedding",
        alias="SPARK_EMBEDDING_MODEL_NAME",
    )
    spark_rerank_model_name: str = Field(default="spark-rerank", alias="SPARK_RERANK_MODEL_NAME")
    spark_safety_model_name: str = Field(
        default="Spark X2-Flash",
        alias="SPARK_SAFETY_MODEL_NAME",
    )
    tts_provider: str = Field(default="edge_tts", alias="TTS_PROVIDER")
    avatar_provider: str = Field(default="sadtalker", alias="AVATAR_PROVIDER")
    llm_tool_content_max_string_chars: int = Field(
        default=600,
        alias="LLM_TOOL_CONTENT_MAX_STRING_CHARS",
    )
    llm_tool_content_max_list_items: int = Field(
        default=4,
        alias="LLM_TOOL_CONTENT_MAX_LIST_ITEMS",
    )
    llm_tool_content_max_dict_items: int = Field(
        default=12,
        alias="LLM_TOOL_CONTENT_MAX_DICT_ITEMS",
    )
    query_rewrite_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="QUERY_REWRITE_LLM",
    )
    retrieval_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="RETRIEVAL_LLM",
    )
    generation_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="GENERATION_LLM",
    )
    practice_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="PRACTICE_LLM",
    )
    judge_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="JUDGE_LLM",
    )
    profile_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="PROFILE_LLM",
    )
    tutor_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="TUTOR_LLM",
    )
    planning_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="PLANNING_LLM",
    )
    review_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="REVIEW_LLM",
    )
    safety_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="SAFETY_LLM",
    )
    evaluation_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="EVALUATION_LLM",
    )
    path_planning_llm: LLMComponentOverride = Field(
        default_factory=LLMComponentOverride,
        alias="PATH_PLANNING_LLM",
    )
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="zhixue", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="", alias="POSTGRES_PASSWORD")
    mongo_uri: str = Field(default="mongodb://localhost:27017/zhixue", alias="MONGO_URI")
    mongo_db: str = Field(default="zhixue", alias="MONGO_DB")
    retrieval_domain: str = Field(
        default="COMPUTER_SCIENCE",
        alias="RETRIEVAL_DOMAIN",
    )
    knowledge_embedding_model_name: str = Field(
        default="qwen3-vl-embedding",
        alias="KNOWLEDGE_EMBEDDING_MODEL_NAME",
    )
    knowledge_embedding_dimension: int = Field(
        default=1024,
        alias="KNOWLEDGE_EMBEDDING_DIMENSION",
    )
    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin123", alias="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")
    minio_bucket: str = Field(default="zhixue-resources", alias="MINIO_BUCKET")
    sandbox_root: str = Field(default="sandbox-temp", alias="SANDBOX_ROOT")

    otel_exporter_otlp_endpoint: str = Field(
        default="",
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
    )
    otel_service_name: str = Field(
        default="zhixue-python-agent",
        alias="OTEL_SERVICE_NAME",
    )

    @staticmethod
    def normalize_provider_name(provider_name: str | None) -> str:
        normalized = (provider_name or "").strip().lower()
        if normalized == "bailian":
            return "openai_compatible"
        return normalized

    @property
    def bailian_api_key(self) -> str:
        return self.openai_compatible_api_key

    @property
    def bailian_base_url(self) -> str:
        return self.openai_compatible_base_url

    def selected_provider_name(self) -> str:
        """Return the active provider with compatibility fallback to MODEL_PROVIDER."""

        return self.normalize_provider_name(self.active_provider or self.model_provider or "openai_compatible")

    def selected_fallback_provider_name(self) -> str | None:
        fallback = self.normalize_provider_name(self.fallback_provider)
        return fallback or None

    def any_provider_ready(self) -> bool:
        """Return whether any configured provider has usable credentials."""

        return any(
            self.provider_ready(provider_name)
            for provider_name in self.model_routing_config().providers
        )

    def runtime_provider_name(self) -> str:
        """Return the provider that should actually be used at runtime."""

        selected = self.selected_provider_name()
        fallback = self.selected_fallback_provider_name()

        if self.provider_ready(selected):
            return selected
        if fallback and self.provider_ready(fallback):
            return fallback

        for provider_name in self.model_routing_config().providers:
            if self.provider_ready(provider_name):
                return provider_name
        return selected

    def build_default_model_routing_config(self) -> ModelRoutingConfig:
        """Build the default logical-model routing config from env values."""

        return ModelRoutingConfig(
            activeProvider=self.selected_provider_name(),
            fallbackProvider=self.selected_fallback_provider_name(),
            ttsProvider=self.tts_provider,
            avatarProvider=self.avatar_provider,
            providers={
                "openai_compatible": ProviderEndpointConfig(
                    name="openai_compatible",
                    protocol="openai_compatible",
                    baseUrl=self.openai_compatible_base_url,
                    apiKeyEnv="OPENAI_COMPATIBLE_API_KEY",
                    timeoutMs=60000,
                    models={
                        "main_chat_model": self.model_name,
                        "fast_model": self.fast_model_name,
                        "reasoning_model": self.reasoning_model_name,
                        "code_model": self.code_model_name,
                        "code_fast_model": self.code_fast_model_name,
                        "omni_model": self.omni_model_name,
                        "omni_realtime_model": self.omni_realtime_model_name,
                        "embedding_model": self.embedding_model_name,
                        "rerank_model": self.rerank_model_name,
                        "safety_model": self.safety_model_name,
                    },
                ),
                "spark": ProviderEndpointConfig(
                    name="spark",
                    protocol="spark_compatible",
                    baseUrl=self.spark_base_url,
                    apiKeyEnv="SPARK_API_KEY",
                    appIdEnv="SPARK_APP_ID",
                    apiSecretEnv="SPARK_API_SECRET",
                    timeoutMs=60000,
                    models={
                        "main_chat_model": self.spark_model_name,
                        "fast_model": self.spark_fast_model_name,
                        "reasoning_model": self.spark_reasoning_model_name,
                        "code_model": self.spark_code_model_name,
                        "code_fast_model": self.spark_code_fast_model_name,
                        "omni_model": self.spark_omni_model_name,
                        "omni_realtime_model": self.spark_omni_realtime_model_name,
                        "embedding_model": self.spark_embedding_model_name,
                        "rerank_model": self.spark_rerank_model_name,
                        "safety_model": self.spark_safety_model_name,
                    },
                ),
            },
        )

    def model_routing_config(self) -> ModelRoutingConfig:
        """Load provider routing config from YAML when available, else use defaults."""

        config_path = self.model_routing_config_path.strip()
        if not config_path:
            return self.build_default_model_routing_config()

        path = Path(config_path)
        if not path.exists():
            return self.build_default_model_routing_config()

        try:
            import yaml
        except ModuleNotFoundError:
            return self.build_default_model_routing_config()

        raw_payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return ModelRoutingConfig.model_validate(self._normalize_model_routing_payload(raw_payload))

    def _normalize_model_routing_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized_payload = dict(payload)
        normalized_payload["activeProvider"] = self.normalize_provider_name(normalized_payload.get("activeProvider"))
        normalized_payload["fallbackProvider"] = self.normalize_provider_name(normalized_payload.get("fallbackProvider"))

        raw_providers = normalized_payload.get("providers", {})
        if not isinstance(raw_providers, dict):
            return normalized_payload

        providers: dict[str, Any] = {}
        for raw_name, raw_config in raw_providers.items():
            normalized_name = self.normalize_provider_name(str(raw_name))
            provider_config = dict(raw_config) if isinstance(raw_config, dict) else raw_config
            if isinstance(provider_config, dict):
                provider_config["name"] = normalized_name
                if normalized_name == "openai_compatible":
                    provider_config["apiKeyEnv"] = "OPENAI_COMPATIBLE_API_KEY"
            providers[normalized_name] = provider_config
        normalized_payload["providers"] = providers
        return normalized_payload

    def resolve_logical_model(
        self,
        logical_model_name: str,
        provider_name: str | None = None,
    ) -> str:
        """Resolve a logical model name for the selected provider."""

        routing = self.model_routing_config()
        return routing.resolve_model(
            logical_model_name,
            self.normalize_provider_name(provider_name or self.runtime_provider_name()),
        )

    def provider_endpoint_config(self, provider_name: str | None = None) -> ProviderEndpointConfig:
        """Return endpoint config for the selected or specified provider."""

        routing = self.model_routing_config()
        return routing.providers[self.normalize_provider_name(provider_name or self.runtime_provider_name())]

    def provider_api_key(self, provider_name: str | None = None) -> str:
        """Return the configured API key string for a provider."""

        provider = self.normalize_provider_name(provider_name or self.runtime_provider_name())
        if provider == "spark":
            return self.spark_api_key
        return self.openai_compatible_api_key

    def provider_ready(self, provider_name: str | None = None) -> bool:
        """Check whether required credentials for a provider are present."""

        provider = self.normalize_provider_name(provider_name or self.runtime_provider_name())
        if provider == "spark":
            return bool(self.spark_api_key)
        return bool(self.openai_compatible_api_key)

    def llm_component_override(self, component_name: str) -> LLMComponentOverride:
        """Return the override block for a named LLM component."""

        override = getattr(self, component_name, None)
        if isinstance(override, LLMComponentOverride):
            return override
        return LLMComponentOverride()

    def resolve_component_provider(self, component_name: str) -> str:
        """Resolve the provider to use for a specific LLM component."""

        override = self.llm_component_override(component_name)
        requested_provider = self.normalize_provider_name(override.provider)
        if requested_provider and self.provider_ready(requested_provider):
            return requested_provider
        return self.runtime_provider_name()

    def resolve_component_model(
        self,
        component_name: str,
        *,
        default_logical_model: str,
        provider_name: str | None = None,
    ) -> str:
        """Resolve a component model override, accepting logical or literal names."""

        override = self.llm_component_override(component_name)
        resolved_provider = self.normalize_provider_name(provider_name or self.resolve_component_provider(component_name))
        configured_model = override.model.strip()
        if not configured_model:
            return self.resolve_logical_model(default_logical_model, resolved_provider)

        provider_config = self.provider_endpoint_config(resolved_provider)
        if configured_model in provider_config.models:
            return provider_config.models[configured_model]
        return configured_model

    def postgres_connect_kwargs(self) -> dict[str, Any]:
        """Return PostgreSQL connection kwargs for psycopg2."""

        return {
            "dbname": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }

    def minio_connect_kwargs(self) -> dict[str, Any]:
        """Return MinIO connection kwargs for the Minio client."""

        return {
            "endpoint": self.minio_endpoint,
            "access_key": self.minio_access_key,
            "secret_key": self.minio_secret_key,
            "secure": self.minio_secure,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


def get_sandbox_root() -> Path:
    """Return the configured sandbox directory as a Path."""

    return Path(get_settings().sandbox_root)
