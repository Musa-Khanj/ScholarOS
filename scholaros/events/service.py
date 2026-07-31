from __future__ import annotations

from scholaros.events.bus import EventBus
from scholaros.kernel.service import Service


class EventService(Service):

    def __init__(self) -> None:
        super().__init__()
        self.bus = EventBus()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass