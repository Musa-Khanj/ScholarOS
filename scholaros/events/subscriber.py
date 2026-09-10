"""
ScholarOS Event Subscriber.

Base subscriber classes and typed subscription contracts supporting priorities,
predicate filters, and optional async event consumption.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from scholaros.events.priority import EventPriority
from scholaros.events.types import EventFilter

if TYPE_CHECKING:
    from scholaros.events.context import EventContext
    from scholaros.events.event import Event

E = TypeVar("E", bound="Event")


class Subscriber(ABC, Generic[E]):
    """
    Base subscriber class for application event handlers.

    Supports priority weighting and event filtering.
    """

    priority: int = EventPriority.NORMAL
    filters: list[EventFilter] = []

    @abstractmethod
    def handle(self, event: E) -> Any:
        """Process an incoming event."""
        ...

    def matches(self, event: Event) -> bool:
        """Check if this subscriber's filters accept the event."""
        for predicate in self.filters:
            try:
                if not predicate(event):
                    return False
            except Exception:
                return False
        return True


class AsyncSubscriber(Subscriber[E], ABC):
    """
    Base class for asynchronous event subscribers.
    """

    def handle(self, event: E) -> Any:
        """Synchronous fallback; raises NotImplementedError if async handler required."""
        raise NotImplementedError("AsyncSubscriber requires handle_async().")

    @abstractmethod
    async def handle_async(self, event: E, context: EventContext | None = None) -> Any:
        """Asynchronously process an incoming event."""

        ...


__all__ = [
    "AsyncSubscriber",
    "Subscriber",
]