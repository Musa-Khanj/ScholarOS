from __future__ import annotations

from scholaros.events.event import Event


class Publisher:

    def __init__(self, bus) -> None:
        self.bus = bus

    def publish(self, event: Event) -> None:
        self.bus.publish(event)