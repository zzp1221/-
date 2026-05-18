"""长时间运行的 Agent 任务共享的 asyncio 辅助工具。"""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TypeVar

_T = TypeVar("_T")


async def cancel_and_await(task: asyncio.Task[_T]) -> None:
    """取消任务并忽略预期的取消异常。"""

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
