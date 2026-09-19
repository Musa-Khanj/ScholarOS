"""
ScholarOS Event System Priorities.

Defines subscription priorities controlling handler dispatch order.
Higher priority handlers execute before lower priority handlers.
"""

from __future__ import annotations

from enum import IntEnum


class EventPriority(IntEnum):
    """
    Event priority levels.

    Handlers with higher integer priority values are invoked first.
    Default handler priority is NORMAL (0).
    """

    CRITICAL = 100
    HIGH = 50
    NORMAL = 0
    LOW = -50
    MONITOR = -100  # Intended for passive observation, runs last

    def __repr__(self) -> str:
        return f"EventPriority.{self.name}"


# Convenient aliases
CRITICAL: EventPriority = EventPriority.CRITICAL
HIGH: EventPriority = EventPriority.HIGH
NORMAL: EventPriority = EventPriority.NORMAL
LOW: EventPriority = EventPriority.LOW
MONITOR: EventPriority = EventPriority.MONITOR

__all__ = [
    "CRITICAL",
    "EventPriority",
    "HIGH",
    "LOW",
    "MONITOR",
    "NORMAL",
]
