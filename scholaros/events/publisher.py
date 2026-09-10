"""
ScholarOS Event Publisher.

Thin, convenient wrapper over EventBus for publishing domain events,
with support for synchronous and asynchronous publication and helper builders.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.events.context import EventContext
from scholaros.events.event import Event

if TYPE_CHECKING:
    from scholaros.events.bus import EventBus


class Publisher:
    """
    Publisher component wrapping EventBus.
    Provides ergonomics for publishing existing events or instantiating and publishing events.
    """

    def __init__(self, bus: EventBus, default_source: str | None = None) -> None:
        self.bus = bus
        self.default_source = default_source

    def publish(self, event: Event, context: EventContext | None = None) -> None:
        """Publish an event synchronously through the underlying event bus."""
        if self.default_source and event.source is None:
            # Inject default source if none provided
            event = event.copy(source=self.default_source)
        self.bus.publish(event, context=context)

    async def publish_async(self, event: Event, context: EventContext | None = None) -> None:
        """Publish an event asynchronously through the underlying event bus."""
        if self.default_source and event.source is None:
            event = event.copy(source=self.default_source)
        await self.bus.publish_async(event, context=context)

    def create_and_publish(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        source: str | None = None,
        context: EventContext | None = None,
    ) -> Event:
        """Convenience method to construct and publish an event."""
        event = Event(
            name=name,
            payload=payload or {},
            metadata=metadata or {},
            correlation_id=correlation_id,
            source=source or self.default_source,
        )
        self.publish(event, context=context)
        return event

    async def create_and_publish_async(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        source: str | None = None,
        context: EventContext | None = None,
    ) -> Event:
        """Convenience method to construct and asynchronously publish an event."""
        event = Event(
            name=name,
            payload=payload or {},
            metadata=metadata or {},
            correlation_id=correlation_id,
            source=source or self.default_source,
        )
        await self.publish_async(event, context=context)
        return event


__all__ = [
    "Publisher",
]