from __future__ import annotations

from queue import PriorityQueue

from scholaros.scheduler.task import Task


class TaskQueue:

    def __init__(self):
        self._queue: PriorityQueue[Task] = PriorityQueue()

    def put(self, task: Task):
        self._queue.put(task)

    def get(self, block: bool = True, timeout: float | None = None) -> Task:
        return self._queue.get(block=block, timeout=timeout)

    def empty(self) -> bool:
        return self._queue.empty()