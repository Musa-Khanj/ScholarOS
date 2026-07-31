from __future__ import annotations

import logging
from pathlib import Path

from scholaros.logging.formatter import ScholarFormatter


def console_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(ScholarFormatter())
    return handler


def file_handler(log_dir: Path) -> logging.Handler:
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_dir / "scholaros.log", encoding="utf-8")
    handler.setFormatter(ScholarFormatter())
    return handler