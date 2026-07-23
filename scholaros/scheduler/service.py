from __future__ import annotations

from scholaros.kernel.service import Service
from scholaros.scheduler.scheduler import Scheduler


class SchedulerService(Service):

    def __init__(self):
        super().__init__()
        self.scheduler = Scheduler()

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.stop()