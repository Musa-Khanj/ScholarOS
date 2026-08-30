"""
ScholarOS
Event Bus

Version : 2.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides publish-subscribe messaging for
ScholarOS.

Components communicate by publishing events.
Interested listeners subscribe to specific
event names.

The EventBus contains no application logic.
It only routes events.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scholaros.events.event import Event

EventHandler = Callable[[Event], Any]

class EventBus:
    """
    Publish-subscribe event dispatcher.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the event bus.
        """

        self._listeners: dict[
            str,
            list[EventHandler],
        ] = {}

    # ---------------------------------------------------------
    # Subscription
    # ---------------------------------------------------------

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """
        Subscribe a handler to an event.
        """

        if not isinstance(
            event_name,
            str,
        ):
            raise TypeError(
                "Event name must be a string."
            )

        if not event_name.strip():
            raise ValueError(
                "Event name cannot be empty."
            )

        if not (
            callable(handler)
            or hasattr(handler, "handle")
        ):
            raise TypeError(
                "Handler must be callable or implement handle()."
            )

        listeners = self._listeners.setdefault(
            event_name,
            [],
        )

        if handler not in listeners:
            listeners.append(
                handler,
            )

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> bool:
        """
        Remove a subscribed handler.

        Returns
        -------
        bool
            True if removed.
        """

        listeners = self._listeners.get(
            event_name,
        )

        if listeners is None:
            return False

        try:
            listeners.remove(
                handler,
            )

            if not listeners:
                del self._listeners[
                    event_name
                ]

            return True

        except ValueError:
            return False

    # ---------------------------------------------------------
    # Publishing
    # ---------------------------------------------------------

    def publish(
        self,
        event: Event,
    ) -> None:
        """
        Publish an event.
        """

        if not isinstance(
            event,
            Event,
        ):
            raise TypeError(
                "Expected Event instance."
            )

        listeners = self._listeners.get(
            event.name,
            (),
        )

        for handler in tuple(listeners):

            if callable(handler):
                handler(event)
            else:
                handler.handle(event)

    # ---------------------------------------------------------
    # Introspection
    # ---------------------------------------------------------

    def listeners(
        self,
        event_name: str,
    ) -> tuple[EventHandler, ...]:
        """
        Return listeners for an event.
        """

        return tuple(
            self._listeners.get(
                event_name,
                (),
            )
        )

    def event_names(
        self,
    ) -> tuple[str, ...]:
        """
        Return registered event names.
        """

        return tuple(
            sorted(
                self._listeners.keys(),
            )
        )

    def has_subscribers(
        self,
        event_name: str,
    ) -> bool:
        """
        Return True if listeners exist.
        """

        return (
            event_name
            in self._listeners
        )

    # ---------------------------------------------------------
    # Maintenance
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove every subscription.
        """

        self._listeners.clear()

    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------

    def __contains__(
        self,
        event_name: object,
    ) -> bool:
        """
        Support:

            if "chat.opened" in bus:
        """

        return (
            isinstance(
                event_name,
                str,
            )
            and event_name
            in self._listeners
        )

    def __len__(
        self,
    ) -> int:
        """
        Number of registered event names.
        """

        return len(
            self._listeners,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"events={len(self)}"
            f")"
        )