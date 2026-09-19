from __future__ import annotations

import logging
from pathlib import Path

from scholaros.logging.formatter import ScholarFormatter
from scholaros.observability.structured_logging import StructuredJsonFormatter
from scholaros.security.logging import SensitiveDataFilter


def console_handler(json_format: bool = False) -> logging.Handler:
    handler = logging.StreamHandler()
    formatter = StructuredJsonFormatter() if json_format else ScholarFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())
    return handler


def file_handler(log_dir: Path, json_format: bool = False) -> logging.Handler:
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_dir / "scholaros.log", encoding="utf-8")
    formatter = StructuredJsonFormatter() if json_format else ScholarFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())
    return handler
