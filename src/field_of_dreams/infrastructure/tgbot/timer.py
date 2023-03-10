import asyncio
import logging
from typing import Callable, Awaitable

logger = logging.getLogger()


class Timer:
    def __init__(self):
        self._tasks_ref: set[asyncio.Task] = set()  # type: ignore

    def run(self, func: Callable[..., Awaitable]) -> asyncio.Task:
        task = asyncio.create_task(func())  # type: ignore
        self._tasks_ref.add(task)
        task.add_done_callback(self._tasks_ref.discard)
        return task

    def del_all(self):
        for task in set(self._tasks_ref):
            task.cancel()
            self._tasks_ref.discard(task)

    def has_timers(self) -> bool:
        return len(self._tasks_ref) > 0

    def all_done(self):
        return len(self._tasks_ref) == 0
