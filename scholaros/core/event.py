"""
ScholarOS
Core Event Bus

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides a lightweight publish/subscribe event system used by
all ScholarOS subsystems.

The EventBus allows independent modules to communicate without
creating direct dependencies between them.

Typical publishers include:

- GUI
- AI Engine
- Plugin Manager
- Research Engine
- Workspace
- Background Jobs

Typical subscribers include:

- Plugins
- Logging
- Notifications
- GUI Updates
- Status Monitor
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

EventCallback = Callable[["Event"], None]


@dataclass(
    frozen=True,
    slots=True,
)
class Event:
    """
    Immutable application event.

    Parameters
    ----------
    name:
        Unique event identifier.

    payload:
        Optional event payload.

    metadata:
        Optional metadata.
    """

    name: str

    payload: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Validate the event.
        """

        if not self.name.strip():
            raise ValueError(
                "Event name cannot be empty."
            )


class EventBus:
    """
    ScholarOS publish/subscribe event bus.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the event bus.
        """

        self._listeners: dict[
            str,
            list[EventCallback],
        ] = defaultdict(list)

    # ---------------------------------------------------------
    # Subscription
    # ---------------------------------------------------------

    def subscribe(
        self,
        event_name: str,
        callback: EventCallback,
    ) -> None:
        """
        Register a listener.
        """

        if not event_name.strip():
            raise ValueError(
                "Event name cannot be empty."
            )

        if not callable(callback):
            raise TypeError(
                "Callback must be callable."
            )

        listeners = self._listeners[event_name]

        if callback not in listeners:
            listeners.append(callback)

    def unsubscribe(
        self,
        event_name: str,
        callback: EventCallback,
    ) -> bool:
        """
        Remove a listener.

        Returns
        -------
        bool
            True if removed.
        """

        listeners = self._listeners.get(
            event_name,
        )

        if not listeners:
            return False

        try:
            listeners.remove(callback)
        except ValueError:
            return False

        if not listeners:
            del self._listeners[event_name]

        return True

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
                "publish() requires an Event."
            )

        listeners = tuple(
            self._listeners.get(
                event.name,
                (),
            )
        )

        for callback in listeners:
            callback(event)

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
    # Introspection
    # ---------------------------------------------------------

    def listeners(
        self,
        event_name: str,
    ) -> tuple[EventCallback, ...]:
        """
        Return listeners for an event.
        """

        return tuple(
            self._listeners.get(
                event_name,
                (),
            )
        )

    def has_subscribers(
        self,
        event_name: str,
    ) -> bool:
        """
        Return True if subscribers exist.
        """

        return bool(
            self._listeners.get(
                event_name,
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
                self._listeners.keys()
            )
        )

    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------

    def __contains__(
        self,
        event_name: str,
    ) -> bool:
        """
        Support:

            "chat.message" in bus
        """

        return self.has_subscribers(
            event_name,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return total registered listeners.
        """

        return sum(
            len(callbacks)
            for callbacks
            in self._listeners.values()
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"events={len(self._listeners)}, "
            f"listeners={len(self)}"
            f")"
        )