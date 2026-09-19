"""
ScholarOS Observability - Structured JSON Logging.

Formats Python standard library logging records into structured JSON lines
enriched with trace IDs, span IDs, timestamps, and contextual execution metadata.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from typing import Any

from scholaros.observability.context import get_current_trace


class StructuredJsonFormatter(logging.Formatter):
    """
    JSON log formatter enriching records with active execution and trace IDs.
    """

    STANDARD_ATTRS = frozenset(
        {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a structured JSON string."""
        message = record.getMessage()

        # Retrieve active trace if available
        trace = get_current_trace()
        trace_id = getattr(record, "trace_id", None) or (trace.trace_id if trace else None)
        span_id = getattr(record, "span_id", None) or (trace.span_id if trace else None)
        execution_id = getattr(record, "execution_id", None) or (trace.execution_id if trace else None)

        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)

        data: dict[str, Any] = {
            "timestamp": dt.isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "line": record.lineno,
            "func": record.funcName,
        }

        if trace_id:
            data["trace_id"] = trace_id
        if span_id:
            data["span_id"] = span_id
        if execution_id:
            data["execution_id"] = execution_id

        # Collect any custom extra attributes passed to logger.info(..., extra={...})
        extras: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in self.STANDARD_ATTRS and key not in {"trace_id", "span_id", "execution_id"}:
                try:
                    json.dumps(value)
                    extras[key] = value
                except (TypeError, OverflowError):
                    extras[key] = str(value)

        if extras:
            data["extra"] = extras

        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        return json.dumps(data)


def create_json_handler(stream: Any = None) -> logging.StreamHandler:
    """Create a StreamHandler configured with StructuredJsonFormatter."""
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredJsonFormatter())
    return handler


__all__ = [
    "StructuredJsonFormatter",
    "create_json_handler",
]
