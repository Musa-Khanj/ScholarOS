from __future__ import annotations

import logging
from pathlib import Path

from scholaros.logging.handlers import console_handler
from scholaros.logging.handlers import file_handler


class LogManager:
    def __init__(self, log_dir: Path = Path("logs")) -> None:
        self._logger = logging.getLogger("ScholarOS")
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:
            self._logger.addHandler(console_handler())
            self._logger.addHandler(file_handler(log_dir))

    @property
    def logger(self) -> logging.Logger:
        return self._logger