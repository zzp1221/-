import json

import pytest

from src.ai_modules.config import Settings
from src.ai_modules.generation import GenerationOutputInvalidError
from src.ai_modules.runtime.smart_engine_stream_worker import SmartEngineStreamWorker


class FakeRedis:
    def exists(self, key: str) -> bool:
        del key
        return False


class CapturingWorker(SmartEngineStreamWorker):
    def __init__(self, supervisor) -> None:
        super().__init__(Settings(), supervisor, lambda: "test-internal-token")
        self._sync_redis = FakeRedis()
        self.started: list[str] = []
        self.failed: list[tuple[str, str, str]] = []
        self.acked: list[str] = []
        self.retried: list[str] = []

    async def _post_started(self, task_id: str) -> None:
        self.started.append(task_id)

    async def _post_worker_failed(self, task_id: str, error_code: str, message: str) -> None:
        self.failed.append((task_id, error_code, message))

    async def _ack_and_clear_retry(self, message_id: str) -> None:
        self.acked.append(message_id)

    async def _retry_or_dlq(self, message_id: str, fields: dict[str, str], reason: str) -> None:
        del fields, reason
        self.retried.append(message_id)


class InvalidGenerationSupervisor:
    async def stream(self, request, cancelled=None):
        del request, cancelled
        raise GenerationOutputInvalidError("invalid generated asset")
        yield


class UnusedSupervisor:
    async def stream(self, request, cancelled=None):
        del request, cancelled
        yield


def valid_fields() -> dict[str, str]:
    return {
        "taskId": "task-1",
        "traceId": "trace-1",
        "serviceType": "RESOURCE_GENERATION",
        "paramsJson": json.dumps({"resourceType": "READING"}),
    }


@pytest.mark.asyncio
async def test_worker_reports_generation_output_invalid_for_execution_validation_failure() -> None:
    worker = CapturingWorker(InvalidGenerationSupervisor())

    await worker._process_message("message-1", valid_fields())

    assert worker.started == ["task-1"]
    assert worker.failed[0][0] == "task-1"
    assert worker.failed[0][1] == "GENERATION_OUTPUT_INVALID"
    assert "invalid generated asset" in worker.failed[0][2]
    assert worker.acked == ["message-1"]
    assert worker.retried == []


@pytest.mark.asyncio
async def test_worker_keeps_invalid_task_payload_for_bad_params_json() -> None:
    worker = CapturingWorker(UnusedSupervisor())
    fields = valid_fields()
    fields["paramsJson"] = "{bad-json"

    await worker._process_message("message-2", fields)

    assert worker.started == []
    assert worker.failed[0][0] == "task-1"
    assert worker.failed[0][1] == "INVALID_TASK_PAYLOAD"
    assert worker.acked == ["message-2"]
    assert worker.retried == []
