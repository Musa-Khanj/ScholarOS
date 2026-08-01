"""
ScholarOS
Event Service

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Concrete service responsible for
managing the ScholarOS event bus.
"""

from __future__ import annotations

from scholaros.core.base import ComponentMetadata
from scholaros.events.bus import EventBus
from scholaros.kernel.service import Service


class EventService(Service):
    """
    Concrete service responsible for
    managing the ScholarOS event bus.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the event service.
        """

        super().__init__(
            ComponentMetadata(
                name="Event Service",
                version="1.0",
                description=(
                    "Provides the ScholarOS "
                    "event bus."
                ),
                author="ScholarOS",
            )
        )

        self.bus = EventBus()

    def start(
        self,
    ) -> None:
        """
        Start the event service.
        """

        pass

    def stop(
        self,
    ) -> None:
        """
        Stop the event service.
        """

        pass