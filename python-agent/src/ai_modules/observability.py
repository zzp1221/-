"""Minimal observability bootstrap with optional OpenTelemetry export."""

from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.ai_modules.config import Settings

LOGGER = logging.getLogger(__name__)


def configure_observability(settings: Settings) -> None:
    """Configure tracing if an OTLP endpoint is available."""

    provider = TracerProvider(
        resource=Resource.create({"service.name": settings.otel_service_name})
    )

    if settings.otel_exporter_otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter = OTLPSpanExporter(
                endpoint=settings.otel_exporter_otlp_endpoint
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception as exc:  # pragma: no cover - defensive fallback
            LOGGER.warning("Failed to configure OTLP exporter: %s", exc)

    trace.set_tracer_provider(provider)
