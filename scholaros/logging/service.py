from __future__ import annotations

from scholaros.kernel.service import Service
from scholaros.logging.manager import LogManager


class LoggingService(Service):
    def __init__(self) -> None:
        super().__init__()
        self.manager = LogManager()

    def start(self) -> None:
        self.manager.logger.info("Logging service started.")

    def stop(self) -> None:
        self.manager.logger.info("Logging service stopped.")