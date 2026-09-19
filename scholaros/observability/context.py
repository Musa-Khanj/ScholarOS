"""
ScholarOS Observability - Trace Context.

Provides execution trace propagation across tasks and services using
contextvars, generating trace and span identifiers for distributed
tracing and telemetry.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
import time
from typing import Any, Generator
from uuid import uuid4


@dataclass(slots=True)
class TraceContext:
    """
    Context tracking an execution span or trace across ScholarOS components.
    """

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid4())[:8])
    parent_span_id: str | None = None
    execution_id: str | None = None
    name: str = "root"
    tags: dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.perf_counter)

    def new_span(self, name: str, tags: dict[str, Any] | None = None) -> TraceContext:
        """Create a child span sharing the same trace_id."""
        merged_tags = dict(self.tags)
        if tags:
            merged_tags.update(tags)
        return TraceContext(
            trace_id=self.trace_id,
            span_id=str(uuid4())[:8],
            parent_span_id=self.span_id,
            execution_id=self.execution_id,
            name=name,
            tags=merged_tags,
            start_time=time.perf_counter(),
        )

    def elapsed_ms(self) -> float:
        """Return milliseconds elapsed since this span was initialized."""
        return (time.perf_counter() - self.start_time) * 1000.0

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "execution_id": self.execution_id,
            "name": self.name,
            "tags": dict(self.tags),
            "elapsed_ms": self.elapsed_ms(),
        }


# Context variable for thread/task-local trace propagation
_ACTIVE_TRACE: ContextVar[TraceContext | None] = ContextVar(
    "scholaros_active_trace", default=None
)


def get_current_trace() -> TraceContext | None:
    """Return the currently active trace context, if any."""
    return _ACTIVE_TRACE.get()


def set_current_trace(context: TraceContext | None) -> Token[TraceContext | None]:
    """Set the currently active trace context and return token for reset."""
    return _ACTIVE_TRACE.set(context)


def reset_current_trace(token: Token[TraceContext | None]) -> None:
    """Reset the trace context to previous token state."""
    _ACTIVE_TRACE.reset(token)


@contextmanager
def trace_scope(
    name: str = "scope",
    trace_id: str | None = None,
    execution_id: str | None = None,
    tags: dict[str, Any] | None = None,
) -> Generator[TraceContext, None, None]:
    """
    Context manager establishing an active trace or child span.
    """
    current = get_current_trace()
    if current is None:
        ctx = TraceContext(
            trace_id=trace_id or str(uuid4()),
            execution_id=execution_id,
            name=name,
            tags=tags or {},
        )
    else:
        ctx = current.new_span(name=name, tags=tags)
        if execution_id:
            ctx.execution_id = execution_id

    token = set_current_trace(ctx)
    try:
        yield ctx
    finally:
        reset_current_trace(token)


__all__ = [
    "TraceContext",
    "get_current_trace",
    "set_current_trace",
    "reset_current_trace",
    "trace_scope",
]
