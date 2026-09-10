"""
ScholarOS Service Lifecycle.

Defines the discrete states of a service lifecycle and provides
state-tracking and transition validation.

State Progression
-----------------
REGISTERED -> INITIALIZED -> STARTED -> RUNNING -> STOPPING -> STOPPED -> SHUTDOWN
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from scholaros.events.event import Event
from scholaros.services.exceptions import ServiceLifecycleError


class ServiceState(Enum):
    """
    Discrete lifecycle states for ScholarOS services.
    """

    REGISTERED = auto()
    INITIALIZED = auto()
    STARTED = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    SHUTDOWN = auto()
    FAILED = auto()

    def __repr__(self) -> str:
        return f"ServiceState.{self.name}"


class LifecycleTracker:
    """
    Manages and validates lifecycle state transitions for a service instance.
    """

    # Valid direct state transitions
    _VALID_TRANSITIONS: dict[ServiceState, set[ServiceState]] = {
        ServiceState.REGISTERED: {ServiceState.INITIALIZED, ServiceState.STARTED, ServiceState.FAILED, ServiceState.SHUTDOWN},
        ServiceState.INITIALIZED: {ServiceState.STARTED, ServiceState.FAILED, ServiceState.SHUTDOWN},
        ServiceState.STARTED: {ServiceState.RUNNING, ServiceState.STOPPING, ServiceState.FAILED, ServiceState.SHUTDOWN},
        ServiceState.RUNNING: {ServiceState.STOPPING, ServiceState.STOPPED, ServiceState.FAILED, ServiceState.SHUTDOWN},
        ServiceState.STOPPING: {ServiceState.STOPPED, ServiceState.FAILED, ServiceState.SHUTDOWN},
        ServiceState.STOPPED: {ServiceState.INITIALIZED, ServiceState.STARTED, ServiceState.SHUTDOWN, ServiceState.FAILED},
        ServiceState.SHUTDOWN: {ServiceState.REGISTERED},  # Can be re-registered/recycled
        ServiceState.FAILED: {ServiceState.INITIALIZED, ServiceState.STARTED, ServiceState.STOPPED, ServiceState.SHUTDOWN},
    }

    def __init__(self, initial_state: ServiceState = ServiceState.REGISTERED) -> None:
        self._state = initial_state
        self._state_history: list[tuple[ServiceState, datetime]] = [
            (initial_state, datetime.now(timezone.utc))
        ]

    @property
    def state(self) -> ServiceState:
        """Return the current service state."""
        return self._state

    @property
    def history(self) -> list[tuple[ServiceState, datetime]]:
        """Return the chronological state transition history."""
        return list(self._state_history)

    def can_transition_to(self, target_state: ServiceState) -> bool:
        """Return True if transition from current state to target_state is allowed."""
        return target_state in self._VALID_TRANSITIONS.get(self._state, set())

    def transition_to(self, target_state: ServiceState) -> None:
        """
        Transition to target_state.

        Raises
        ------
        ServiceLifecycleError
            If the transition is not allowed.
        """
        if target_state == self._state:
            return

        if not self.can_transition_to(target_state):
            raise ServiceLifecycleError(
                f"Invalid lifecycle transition from {self._state.name} to {target_state.name}."
            )

        self._state = target_state
        self._state_history.append((target_state, datetime.now(timezone.utc)))

    def is_running(self) -> bool:
        """Return True if service is running or started."""
        return self._state in (ServiceState.STARTED, ServiceState.RUNNING)

    def is_stopped(self) -> bool:
        """Return True if service is stopped or shutdown."""
        return self._state in (ServiceState.STOPPED, ServiceState.SHUTDOWN, ServiceState.REGISTERED)


class ServiceLifecycleEvent(Event):
    """Base event for service lifecycle transitions."""

    def __init__(
        self,
        service_name: str,
        state: ServiceState | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        source: str | None = None,
    ) -> None:
        p: dict[str, Any] = {"service_name": service_name}
        if state is not None:
            p["state"] = state.name
        if payload:
            p.update(payload)

        super().__init__(
            name=self.__class__.__name__,
            payload=p,
            metadata=metadata if metadata is not None else {},
            correlation_id=correlation_id,
            source=source,
        )


class ServiceRegistered(ServiceLifecycleEvent):
    """Emitted when a service is registered."""


class ServiceInitialized(ServiceLifecycleEvent):
    """Emitted when a service is initialized."""


class ServiceStarted(ServiceLifecycleEvent):
    """Emitted when a service is started."""


class ServiceStopped(ServiceLifecycleEvent):
    """Emitted when a service is stopped."""


class ServiceRestarted(ServiceLifecycleEvent):
    """Emitted when a service is restarted."""


class ServiceFailed(ServiceLifecycleEvent):
    """Emitted when a service encounters a failure."""


class ServiceShutdown(ServiceLifecycleEvent):
    """Emitted when a service is shut down."""


__all__ = [
    "LifecycleTracker",
    "ServiceFailed",
    "ServiceInitialized",
    "ServiceLifecycleEvent",
    "ServiceRegistered",
    "ServiceRestarted",
    "ServiceShutdown",
    "ServiceStarted",
    "ServiceState",
    "ServiceStopped",
]

