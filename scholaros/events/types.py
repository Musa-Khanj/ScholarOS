"""
ScholarOS Event System Types.

Defines core type aliases, protocols, and type variables used across
the ScholarOS event-driven architecture.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from scholaros.events.context import EventContext
    from scholaros.events.event import Event

E = TypeVar("E", bound="Event")

# Synchronous handler: func(event) -> Any or func(event, context) -> Any
SyncEventHandler: TypeAlias = Callable[..., Any]

# Asynchronous handler: async func(event) -> Any or async func(event, context) -> Any
AsyncEventHandler: TypeAlias = Callable[..., Awaitable[Any]]

# Unified event handler type (sync or async)
EventHandler: TypeAlias = SyncEventHandler | AsyncEventHandler

# Event filter predicate: func(event) -> bool
EventFilter: TypeAlias = Callable[["Event"], bool]


@runtime_checkable
class EventHandlerProtocol(Protocol):
    """Protocol for objects implementing event handling."""

    def handle(self, event: Event, context: EventContext | None = None) -> Any:
        """Handle an incoming event synchronously."""
        ...


@runtime_checkable
class AsyncEventHandlerProtocol(Protocol):
    """Protocol for objects implementing asynchronous event handling."""

    async def handle_async(self, event: Event, context: EventContext | None = None) -> Any:
        """Handle an incoming event asynchronously."""
        ...


__all__ = [
    "AsyncEventHandler",
    "AsyncEventHandlerProtocol",
    "E",
    "EventFilter",
    "EventHandler",
    "EventHandlerProtocol",
    "SyncEventHandler",
]
