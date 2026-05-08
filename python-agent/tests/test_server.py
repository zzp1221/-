import json

import pytest

import server
from src.ai_modules.config import Settings
from src.ai_modules.models import EngineStreamRequest
from src.ai_modules.models.events import ProgressPayload, ProgressSSEEvent


def test_health_endpoint(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["provider"] == "openai_compatible"
    assert response.json()["runtimeProvider"] == "openai_compatible"


def test_sse_event_serialization() -> None:
    event = ProgressSSEEvent(
        taskId="task_001",
        traceId="trace_001",
        seq=1,
        payload=ProgressPayload(stage="accepted", percent=10, message="ok"),
    )

    serialized = event.to_sse()

    assert serialized.startswith("event: progress\n")
    assert '"taskId": "task_001"' in serialized


def test_stream_endpoint_returns_expected_event_order(client) -> None:
    payload = {
        "serviceType": "RESOURCE_GENERATION",
        "params": {"resourceType": "DOCUMENT"},
        "userId": "user-001",
        "taskId": "task-001",
        "traceId": "trace-001",
        "conversationId": "conv-001",
    }

    with client.stream(
        "POST",
        "/internal/smart-engine/stream",
        json=payload,
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        lines = [line for line in response.iter_lines() if line]

    event_names = [line.removeprefix("event: ") for line in lines[::2]]
    data_payloads = [
        json.loads(line.removeprefix("data: "))
        for line in lines[1::2]
    ]

    assert event_names == [
        "progress",
        "result_chunk",
        "progress",
        "result_chunk",
        "result_chunk",
        "resource_file",
        "done",
    ]
    assert data_payloads[-1]["payload"]["status"] == "SUCCESS"


def test_stream_endpoint_supports_video_generation_events(client) -> None:
    payload = {
        "serviceType": "RESOURCE_GENERATION",
        "params": {
            "resourceType": "VIDEO",
            "query": "联合索引",
            "topic": "联合索引",
            "style": "hybrid",
            "duration": 60,
        },
        "userId": "user-001",
        "taskId": "task-video",
        "traceId": "trace-video",
    }

    with client.stream(
        "POST",
        "/internal/smart-engine/stream",
        json=payload,
    ) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    event_names = [line.removeprefix("event: ") for line in lines[::2]]
    data_payloads = [json.loads(line.removeprefix("data: ")) for line in lines[1::2]]

    assert event_names.count("progress") >= 4
    resource_file_payload = next(item["payload"] for item in data_payloads if item["event"] == "resource_file")
    assert resource_file_payload["assetType"] == "VIDEO"
    assert resource_file_payload["thumbnailPath"].endswith(".svg")
    speech_payload = next(item["payload"] for item in data_payloads if item["event"] == "video_gen:speech")
    assert speech_payload["audioBase64"]
    assert speech_payload["avatarDataUrl"] == "/dh_live/assets/combined_data.json.gz"
    completion_payload = next(item["payload"] for item in data_payloads if item["event"] == "result_chunk" and "视频生成完成" in item["payload"].get("text", ""))
    assert "视频生成完成" in completion_payload["text"]


def test_stream_endpoint_rejects_unknown_service_type(client) -> None:
    payload = {
        "serviceType": "UNKNOWN",
        "params": {},
        "taskId": "task-unknown",
        "traceId": "trace-unknown",
    }

    response = client.post("/internal/smart-engine/stream", json=payload)

    assert response.status_code == 400


def test_engine_stream_request_normalizes_legacy_java_payload() -> None:
    request = EngineStreamRequest.model_validate(
        {
            "serviceType": "LEARNING_EVALUATION",
            "taskId": 12345,
            "traceId": 67890,
            "userId": 111,
            "requestPayload": {
                "params": {
                    "params": {
                        "message": "请评估我的掌握情况",
                        "knowledgePoint": "数据结构",
                    }
                }
            },
        }
    )

    assert request.service_type == "EVALUATION"
    assert request.task_id == "12345"
    assert request.trace_id == "67890"
    assert request.user_id == "111"
    assert request.params["message"] == "请评估我的掌握情况"
    assert request.params["knowledgePoint"] == "数据结构"


def test_stream_endpoint_accepts_legacy_java_wrapped_payload(client) -> None:
    payload = {
        "serviceType": "LEARNING_EVALUATION",
        "taskId": 12345,
        "traceId": 67890,
        "userId": 111,
        "requestPayload": {
            "params": {
                "params": {
                    "message": "请评估我的掌握情况",
                    "knowledgePoint": "数据结构",
                }
            }
        },
    }

    with client.stream(
        "POST",
        "/internal/smart-engine/stream",
        json=payload,
    ) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    event_names = [line.removeprefix("event: ") for line in lines[::2]]
    assert event_names[-1] == "done"


def test_stream_endpoint_emits_error_and_failed_done_when_supervisor_raises(client, monkeypatch) -> None:
    class BrokenSupervisor:
        def resolve_route(self, service_type, params):
            del service_type, params
            return None

        async def stream(self, request):
            del request
            raise RuntimeError("boom")
            yield  # pragma: no cover

    monkeypatch.setattr(server, "SUPERVISOR", BrokenSupervisor())

    payload = {
        "serviceType": "RESOURCE_GENERATION",
        "params": {"resourceType": "DOCUMENT"},
        "taskId": "task-error",
        "traceId": "trace-error",
    }

    with client.stream(
        "POST",
        "/internal/smart-engine/stream",
        json=payload,
    ) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    event_names = [line.removeprefix("event: ") for line in lines[::2]]
    data_payloads = [json.loads(line.removeprefix("data: ")) for line in lines[1::2]]

    assert event_names == ["error", "done"]
    assert data_payloads[0]["payload"]["code"] == "PYTHON_AGENT_ERROR"
    assert data_payloads[0]["payload"]["message"] == "boom"
    assert data_payloads[1]["payload"]["status"] == "FAILED"


def test_settings_switch_provider_via_env() -> None:
    settings = Settings.model_validate(
        {
            "APP_NAME": "agent",
            "ACTIVE_PROVIDER": "spark",
            "FALLBACK_PROVIDER": "openai_compatible",
            "SPARK_API_KEY": "spark-key",
            "OPENAI_COMPATIBLE_API_KEY": "openai-key",
            "SPARK_MODEL_NAME": "Spark Ultra",
            "MODEL_NAME": "qwen3.6-plus",
        }
    )

    assert settings.runtime_provider_name() == "spark"
    assert settings.resolve_logical_model("main_chat_model") == "Spark Ultra"


def test_settings_fallback_to_bailian_when_active_provider_not_ready() -> None:
    settings = Settings.model_validate(
        {
            "APP_NAME": "agent",
            "ACTIVE_PROVIDER": "spark",
            "FALLBACK_PROVIDER": "openai_compatible",
            "SPARK_API_KEY": "",
            "OPENAI_COMPATIBLE_API_KEY": "openai-key",
            "SPARK_MODEL_NAME": "Spark Ultra",
            "MODEL_NAME": "qwen3.6-plus",
        }
    )

    assert settings.runtime_provider_name() == "openai_compatible"
    assert settings.resolve_logical_model("main_chat_model") == "qwen3.6-plus"
