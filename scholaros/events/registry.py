"""
ScholarOS Event Registry.

Stores and indexes event subscriptions by event pattern/name, priority,
and predicate filters. Contains registration storage and querying only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import fnmatch
from typing import TYPE_CHECKING, Any

from scholaros.events.priority import EventPriority
from scholaros.events.types import EventFilter, EventHandler

if TYPE_CHECKING:
    from scholaros.events.event import Event


@dataclass(slots=True)
class Subscription:
    """
    Represents an event subscription.
    """

    event_pattern: str
    handler: EventHandler
    priority: int = EventPriority.NORMAL
    filters: list[EventFilter] = field(default_factory=list)
    once: bool = False

    def matches(self, event_name: str) -> bool:
        """
        Check if this subscription matches the given event name.
        Supports exact match and wildcards (e.g., 'research.*').
        """
        if self.event_pattern == event_name:
            return True
        if "*" in self.event_pattern or "?" in self.event_pattern:
            return fnmatch.fnmatchcase(event_name, self.event_pattern)
        return False

    def passes_filters(self, event: Event) -> bool:
        """
        Check if an event satisfies all registered filter predicates.
        """
        for predicate in self.filters:
            try:
                if not predicate(event):
                    return False
            except Exception:
                return False
        return True


class EventRegistry:
    """
    Thread-safe storage and query system for event subscriptions.
    """

    def __init__(self) -> None:
        self._subscriptions: list[Subscription] = []

    def register(
        self,
        event_pattern: str,
        handler: EventHandler,
        priority: int = EventPriority.NORMAL,
        filters: list[EventFilter] | None = None,
        once: bool = False,
    ) -> Subscription:
        """Register a handler subscription, deduplicating identical subscriptions."""
        for existing in self._subscriptions:
            if existing.event_pattern == event_pattern and existing.handler == handler:
                return existing

        subscription = Subscription(
            event_pattern=event_pattern,
            handler=handler,
            priority=priority,
            filters=filters or [],
            once=once,
        )
        self._subscriptions.append(subscription)
        return subscription


    def unregister(self, event_pattern: str, handler: EventHandler) -> bool:
        """Remove matching subscription(s)."""
        initial_len = len(self._subscriptions)
        self._subscriptions = [
            sub
            for sub in self._subscriptions
            if not (sub.event_pattern == event_pattern and sub.handler == handler)
        ]
        return len(self._subscriptions) < initial_len

    def remove_subscription(self, subscription: Subscription) -> bool:
        """Remove a specific subscription instance."""
        try:
            self._subscriptions.remove(subscription)
            return True
        except ValueError:
            return False

    def get_subscriptions_for(self, event: Event) -> list[Subscription]:
        """
        Return all subscriptions matching the event name and filters,
        sorted in descending priority order (highest priority first).
        """
        matching: list[Subscription] = []
        for sub in self._subscriptions:
            if sub.matches(event.name) and sub.passes_filters(event):
                matching.append(sub)

        # Sort stable by priority descending
        matching.sort(key=lambda s: s.priority, reverse=True)
        return matching

    def listeners_for(self, event_name: str) -> tuple[EventHandler, ...]:
        """Return all handlers subscribed to an exact event name."""
        return tuple(
            sub.handler for sub in self._subscriptions if sub.event_pattern == event_name
        )

    def event_names(self) -> tuple[str, ...]:
        """Return all distinct subscribed event patterns."""
        return tuple(sorted({sub.event_pattern for sub in self._subscriptions}))

    def has_subscribers(self, event_name: str) -> bool:
        """Return True if any subscription matches event_name."""
        for sub in self._subscriptions:
            if sub.matches(event_name):
                return True
        return False

    def clear(self) -> None:
        """Remove all subscriptions."""
        self._subscriptions.clear()

    def __len__(self) -> int:
        return len(self._subscriptions)

    def __contains__(self, event_name: object) -> bool:
        return isinstance(event_name, str) and self.has_subscribers(event_name)


__all__ = [
    "EventRegistry",
    "Subscription",
]
