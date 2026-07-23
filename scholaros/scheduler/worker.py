from __future__ import annotations

import threading

from scholaros.scheduler.queue import TaskQueue


class Worker(threading.Thread):

    def __init__(self, queue: TaskQueue):
        super().__init__(daemon=True)
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            task = self.queue.get()
            task.func(*task.args, **task.kwargs)

    def stop(self):
        self.running = False