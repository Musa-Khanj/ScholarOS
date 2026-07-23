from __future__ import annotations

from scholaros.scheduler.queue import TaskQueue
from scholaros.scheduler.task import Task
from scholaros.scheduler.worker import Worker


class Scheduler:

    def __init__(self):
        self.queue = TaskQueue()
        self.worker = Worker(self.queue)

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.stop()

    def submit(self, task: Task):
        self.queue.put(task)