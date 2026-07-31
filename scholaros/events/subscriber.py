from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.events.event import Event


class Subscriber(ABC):

    @abstractmethod
    def handle(self, event: Event) -> None:
        ...