"""
ScholarOS Event Service.

Concrete kernel service responsible for managing the ScholarOS event bus
and registering event components into the dependency injection container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.core.base import ComponentMetadata
from scholaros.events.bus import EventBus
from scholaros.events.publisher import Publisher
from scholaros.kernel.service import Service

if TYPE_CHECKING:
    from scholaros.container.container import Container


class EventService(Service):
    """
    Concrete service responsible for managing the ScholarOS event bus
    and providing container registration.
    """

    def __init__(
        self,
        bus: EventBus | None = None,
    ) -> None:
        """Initialize the event service."""
        super().__init__(
            ComponentMetadata(
                name="Event Service",
                version="1.0",
                description="Provides the ScholarOS event bus.",
                author="ScholarOS",
            )
        )

        self.bus = bus if bus is not None else EventBus()
        self._running = False

    @property
    def is_running(self) -> bool:
        """Return True if event service is running."""
        return self._running

    def start(self) -> None:
        """Start the event service."""
        self._running = True

    def stop(self) -> None:
        """Stop the event service and clear subscriptions."""
        self._running = False
        self.bus.clear()

    def register_container(self, container: Container) -> None:
        """
        Register the EventBus, EventService, and Publisher into the DI container.
        """
        container.add_instance(EventBus, self.bus)
        container.add_instance(EventService, self)
        container.add_factory(Publisher, lambda: Publisher(self.bus))

    @classmethod
    def configure_container(cls, container: Container, bus: EventBus | None = None) -> EventService:
        """
        Convenience factory to instantiate EventService and wire it into a container.
        """
        service = cls(bus=bus)
        service.register_container(container)
        return service


__all__ = [
    "EventService",
]