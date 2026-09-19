"""
ScholarOS Observability Subsystem.

Provides end-to-end execution tracing, telemetry metrics, structured JSON logging,
subsystem health aggregation, and diagnostic inspection answering:
Query -> Strategy -> Retrieved Documents -> Scores -> Context -> Prompt -> Model -> Response.
"""

from __future__ import annotations

import logging

from scholaros.observability.context import (
    TraceContext,
    get_current_trace,
    reset_current_trace,
    set_current_trace,
    trace_scope,
)
from scholaros.observability.health import SystemHealthAggregator
from scholaros.observability.registry import DiagnosticsRegistry
from scholaros.observability.structured_logging import StructuredJsonFormatter, create_json_handler
from scholaros.observability.subscriber import TelemetryEventSubscriber
from scholaros.observability.telemetry import TelemetryCollector
from scholaros.observability.trace import RAGTrace, RetrievedChunkTrace


def enable_debug_mode(logger_name: str = "ScholarOS") -> None:
    """Enable verbose debug logging across ScholarOS."""
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)
    for h in log.handlers:
        h.setLevel(logging.DEBUG)


def disable_debug_mode(logger_name: str = "ScholarOS") -> None:
    """Disable debug mode and restore INFO level."""
    log = logging.getLogger(logger_name)
    log.setLevel(logging.INFO)
    for h in log.handlers:
        h.setLevel(logging.INFO)


__all__ = [
    "TraceContext",
    "get_current_trace",
    "set_current_trace",
    "reset_current_trace",
    "trace_scope",
    "RetrievedChunkTrace",
    "RAGTrace",
    "DiagnosticsRegistry",
    "TelemetryCollector",
    "StructuredJsonFormatter",
    "create_json_handler",
    "SystemHealthAggregator",
    "TelemetryEventSubscriber",
    "enable_debug_mode",
    "disable_debug_mode",
]
