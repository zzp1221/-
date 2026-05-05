"""FastAPI entrypoint for the zhixue Python agent runtime."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from opentelemetry import trace
from pydantic import BaseModel, ConfigDict, Field

from src.ai_modules.config import get_settings
from src.ai_modules.memory import ConversationMessageDocument, MongoConversationMessageStore
from src.ai_modules.models import DonePayload, DoneSSEEvent, EngineStreamRequest, ErrorPayload, ErrorSSEEvent
from src.ai_modules.observability import configure_observability
from src.ai_modules.supervisor import PythonAgentSupervisor

LOGGER = logging.getLogger(__name__)
SETTINGS = get_settings()
TRACER = trace.get_tracer(__name__)
SUPERVISOR = PythonAgentSupervisor()
MESSAGE_STORE = MongoConversationMessageStore()
CANCELLED_TASKS: set[str] = set()


class InternalConversationMessageRequest(BaseModel):
    """Append a single transcript message for a conversation."""

    role: str
    content: str
    user_id: str | None = Field(default=None, alias="userId")

    model_config = ConfigDict(populate_by_name=True)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle hooks."""

    logging.basicConfig(level=logging.INFO)
    configure_observability(SETTINGS)
    LOGGER.info(
        "Starting %s with provider=%s runtime_provider=%s model=%s",
        SETTINGS.app_name,
        SETTINGS.model_provider,
        SETTINGS.runtime_provider_name(),
        SETTINGS.model_name,
    )

    cleanup_task = asyncio.create_task(_sandbox_cleanup_loop())

    yield

    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


async def _sandbox_cleanup_loop() -> None:
    """Periodically remove sandbox files older than 2 hours."""
    import shutil
    from pathlib import Path

    sandbox_root = Path(SETTINGS.sandbox_root)
    max_age_seconds = 2 * 60 * 60  # 2 hours
    interval_seconds = 30 * 60  # 30 minutes

    while True:
        await asyncio.sleep(interval_seconds)
        try:
            if not sandbox_root.exists():
                continue
            import time
            now = time.time()
            for entry in sandbox_root.iterdir():
                try:
                    age = now - entry.stat().st_mtime
                    if age > max_age_seconds:
                        if entry.is_dir():
                            shutil.rmtree(entry)
                        else:
                            entry.unlink()
                        LOGGER.info("Sandbox cleanup: removed %s (age %.0fs)", entry.name, age)
                except Exception:
                    pass
        except Exception:
            LOGGER.exception("Sandbox cleanup iteration failed")


app = FastAPI(title=SETTINGS.app_name, lifespan=lifespan)


async def _supervisor_event_stream(engine_request: EngineStreamRequest) -> AsyncIterator[str]:
    """Yield SSE events produced by the placeholder supervisor."""

    with TRACER.start_as_current_span("internal.smart_engine.stream"):
        seq = 1
        try:
            async for event in SUPERVISOR.stream(engine_request, cancelled=CANCELLED_TASKS):
                seq = event.seq + 1
                yield event.to_sse()
        except Exception as exc:
            LOGGER.exception(
                "Supervisor stream failed for task_id=%s trace_id=%s",
                engine_request.task_id,
                engine_request.trace_id,
            )
            yield ErrorSSEEvent(
                taskId=engine_request.task_id,
                traceId=engine_request.trace_id,
                seq=seq,
                payload=ErrorPayload(
                    code="PYTHON_AGENT_ERROR",
                    message=str(exc) or "Python Agent 执行失败",
                ),
            ).to_sse()
            yield DoneSSEEvent(
                taskId=engine_request.task_id,
                traceId=engine_request.trace_id,
                seq=seq + 1,
                payload=DonePayload(
                    status="FAILED",
                    summary="Supervisor 执行失败，任务已终止",
                ),
            ).to_sse()
        finally:
            CANCELLED_TASKS.discard(engine_request.task_id)


@app.get("/health")
async def health() -> JSONResponse:
    """Simple health probe for Docker and local development."""

    payload = {
        "status": "ok",
        "service": SETTINGS.app_name,
        "provider": SETTINGS.model_provider,
        "runtimeProvider": SETTINGS.runtime_provider_name(),
        "model": SETTINGS.model_name,
        "resolvedMainModel": SETTINGS.resolve_logical_model("main_chat_model"),
        "resolvedFastModel": SETTINGS.resolve_logical_model("fast_model"),
    }
    return JSONResponse(payload)


@app.post("/internal/smart-engine/stream")
async def smart_engine_stream(
    engine_request: EngineStreamRequest,
) -> StreamingResponse:
    """Internal streaming endpoint used by the Java BFF."""

    LOGGER.info(
        "Received task_id=%s trace_id=%s service_type=%s",
        engine_request.task_id,
        engine_request.trace_id,
        engine_request.service_type,
    )
    try:
        SUPERVISOR.resolve_route(engine_request.service_type, engine_request.params)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(
        _supervisor_event_stream(engine_request),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/internal/smart-engine/{task_id}/cancel")
async def cancel_smart_engine_task(task_id: str) -> JSONResponse:
    """Cancel a running smart-engine task by its id."""
    CANCELLED_TASKS.add(task_id)
    LOGGER.info("Task cancellation requested: task_id=%s", task_id)
    return JSONResponse({"status": "cancelled", "taskId": task_id})


@app.post("/internal/conversations/{conversation_id}/messages")
async def append_conversation_message(
    conversation_id: str,
    request: InternalConversationMessageRequest,
) -> JSONResponse:
    """Persist a single conversation transcript message."""

    document = ConversationMessageDocument(
        conversationId=conversation_id,
        userId=request.user_id,
        role=request.role,
        content=request.content,
    )
    await MESSAGE_STORE.append_message(document)
    return JSONResponse({"messageId": document.message_id})


@app.get("/internal/conversations/{conversation_id}/messages")
async def list_conversation_messages(
    conversation_id: str,
    user_id: str | None = Query(default=None, alias="userId"),
) -> JSONResponse:
    """Return the persisted transcript for a conversation."""

    documents = await MESSAGE_STORE.list_messages(
        conversation_id=conversation_id,
        user_id=user_id,
    )
    return JSONResponse(
        [
            document.model_dump(by_alias=True, mode="json")
            for document in documents
        ]
    )
