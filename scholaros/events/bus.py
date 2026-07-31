from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict

from scholaros.events.event import Event
from scholaros.events.subscriber import Subscriber


class EventBus:

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_name: str, subscriber: Subscriber) -> None:
        self._subscribers[event_name].append(subscriber)

    def unsubscribe(self, event_name: str, subscriber: Subscriber) -> None:
        if subscriber in self._subscribers[event_name]:
            self._subscribers[event_name].remove(subscriber)

    def publish(self, event: Event) -> None:
        for subscriber in self._subscribers[event.name]:
            subscriber.handle(event)