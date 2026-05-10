"""Small asyncio helpers shared by long-running agent tasks."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import TypeVar

_T = TypeVar("_T")


async def cancel_and_await(task: asyncio.Task[_T]) -> None:
    """Cancel a task and swallow the expected cancellation error."""

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
