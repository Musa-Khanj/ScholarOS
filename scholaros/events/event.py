"""
ScholarOS Event.

Defines the immutable Event object used by the ScholarOS event system.
Events represent significant occurrences across the application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Event:
    """
    Represents an application event.

    Parameters
    ----------
    name:
        Event name or topic.
    payload:
        Event payload dictionary.
    metadata:
        Optional event metadata dictionary.
    timestamp:
        UTC timestamp generated automatically.
    id:
        Unique event identifier (UUID4 string).
    correlation_id:
        Optional correlation ID for distributed tracing and workflows.
    source:
        Component, module, or agent that produced the event.
    """

    name: str

    payload: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )

    id: str = field(
        default_factory=lambda: str(
            uuid4(),
        ),
    )

    correlation_id: str | None = None

    source: str | None = None

    def __post_init__(self) -> None:
        """Validate the event attributes."""
        if not isinstance(self.name, str):
            raise TypeError("Event name must be a string.")

        if not self.name.strip():
            raise ValueError("Event name cannot be empty.")

        if not isinstance(self.payload, dict):
            raise TypeError("Payload must be a dictionary.")

        if not isinstance(self.metadata, dict):
            raise TypeError("Metadata must be a dictionary.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, str):
            raise TypeError("correlation_id must be a string or None.")

        if self.source is not None and not isinstance(self.source, str):
            raise TypeError("source must be a string or None.")

    @property
    def has_payload(self) -> bool:
        """Return True if the event contains payload items."""
        return bool(self.payload)

    @property
    def has_metadata(self) -> bool:
        """Return True if metadata dictionary is non-empty."""
        return bool(self.metadata)

    def copy(self, **overrides: Any) -> Event:
        """
        Return a shallow copy of the event, with optional attribute overrides.
        """
        data: dict[str, Any] = {
            "name": self.name,
            "payload": dict(self.payload),
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp,
            "id": self.id,
            "correlation_id": self.correlation_id,
            "source": self.source,
        }
        data.update(overrides)
        return Event(**data)

    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        extra = []
        if self.correlation_id:
            extra.append(f"correlation_id={self.correlation_id!r}")
        if self.source:
            extra.append(f"source={self.source!r}")
        extra_str = (", " + ", ".join(extra)) if extra else ""

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"payload={self.payload!r}{extra_str}"
            f")"
        )


__all__ = [
    "Event",
]