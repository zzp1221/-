"""Base placeholder agent implementations for early integration steps."""

from __future__ import annotations

from collections.abc import AsyncIterator

from src.ai_modules.models import ProgressPayload, ProgressSSEEvent, ResultChunkPayload, ResultChunkSSEEvent, SSEEvent
from src.ai_modules.runtime import SnapshotBuilder, SystemSnapshot


class PlaceholderAgent:
    """Minimal agent skeleton used before real business logic is connected."""

    def __init__(
        self,
        agent_name: str,
        stage_name: str,
        emits_result_chunk: bool = False,
    ) -> None:
        self.agent_name = agent_name
        self.stage_name = stage_name
        self.emits_result_chunk = emits_result_chunk

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        context = SnapshotBuilder.render_prompt_context(snapshot)
        return "\n".join(
            [
                f"你是 {self.agent_name}，当前处于骨架联调阶段。",
                context,
            ]
        )

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> AsyncIterator[SSEEvent]:
        if self.emits_result_chunk:
            del params
            yield ResultChunkSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=seq,
                payload=ResultChunkPayload(
                    text=(
                        f"{self.agent_name} 已完成占位执行，服务类型为 {service_type}。"
                        f" 当前课程: {snapshot.current_course}。"
                    )
                ),
            )
            return

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=min(seq * 20, 95),
                message=(
                    f"{self.agent_name} 占位执行完成；"
                    f" 已注入上下文 prompt，课程={snapshot.current_course}"
                ),
            ),
        )
