"""Shared runtime configuration helpers for knowledge scripts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_modules.config import get_settings


class PostgresRuntimeConfig(BaseModel):
    """Validated PostgreSQL connection settings."""

    dbname: str
    user: str
    password: str
    host: str
    port: int


class MinioRuntimeConfig(BaseModel):
    """Validated MinIO connection settings."""

    endpoint: str
    access_key: str
    secret_key: str
    secure: bool
    bucket: str


class KnowledgeRuntimeConfig(BaseModel):
    """Validated runtime configuration for knowledge scripts."""

    dashscope_api_key: str = Field(min_length=1)
    embedding_model_name: str = Field(min_length=1)
    embedding_dimension: int = Field(gt=0)
    retrieval_domain: str = Field(min_length=1)
    postgres: PostgresRuntimeConfig
    minio: MinioRuntimeConfig


def load_knowledge_runtime_config() -> KnowledgeRuntimeConfig:
    """Build a validated runtime config from shared Settings."""

    settings = get_settings()
    return KnowledgeRuntimeConfig(
        dashscope_api_key=settings.bailian_api_key,
        embedding_model_name=settings.knowledge_embedding_model_name,
        embedding_dimension=settings.knowledge_embedding_dimension,
        retrieval_domain=settings.retrieval_domain,
        postgres=PostgresRuntimeConfig.model_validate(settings.postgres_connect_kwargs()),
        minio=MinioRuntimeConfig(
            **settings.minio_connect_kwargs(),
            bucket=settings.minio_bucket,
        ),
    )


def configure_dashscope_api_key() -> KnowledgeRuntimeConfig:
    """Load config and export the DashScope key for SDK-based callers."""

    config = load_knowledge_runtime_config()
    os.environ["DASHSCOPE_API_KEY"] = config.dashscope_api_key
    return config
