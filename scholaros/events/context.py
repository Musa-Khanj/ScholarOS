"""
ScholarOS Event Context.

Encapsulates runtime dispatch context, metadata, propagation controls,
and handler feedback during event processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class EventContext:
    """
    Contextual execution data passed along with an event through middlewares and handlers.

    Supports:
    - Event propagation cancellation (stop_propagation)
    - Handler execution recording
    - Additional execution metadata
    """

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = field(default_factory=dict)
    _cancelled: bool = field(default=False, init=False)
    _cancel_reason: str | None = field(default=None, init=False)
    _handled_by: list[str] = field(default_factory=list, init=False)

    @property
    def is_cancelled(self) -> bool:
        """Return True if event propagation was stopped."""
        return self._cancelled

    @property
    def cancel_reason(self) -> str | None:
        """Return the reason why propagation was stopped, if any."""
        return self._cancel_reason

    @property
    def handled_by(self) -> tuple[str, ...]:
        """Return a tuple of handler names that processed this event."""
        return tuple(self._handled_by)

    def stop_propagation(self, reason: str | None = None) -> None:
        """
        Stop further dispatch of the event to subsequent handlers and middlewares.
        """
        self._cancelled = True
        self._cancel_reason = reason

    def record_handler(self, handler_name: str) -> None:
        """Record that a handler processed this event."""
        self._handled_by.append(handler_name)

    def set(self, key: str, value: Any) -> None:
        """Store context data."""
        self.metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve context data."""
        return self.metadata.get(key, default)


__all__ = [
    "EventContext",
]
