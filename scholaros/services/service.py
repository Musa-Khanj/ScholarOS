"""
ScholarOS Service Base.

Defines the abstract base class for all ScholarOS services, supporting
metadata, discrete lifecycle hooks (initialize, start, stop, shutdown),
health checks, and execution capabilities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.lifecycle import LifecycleTracker, ServiceState
from scholaros.services.metadata import ServiceMetadata


class Service(ABC):
    """
    Base class for all ScholarOS services.

    Subclasses can define service-specific lifecycle behavior and execution logic.
    """

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name=self.__class__.__name__,
                description=f"{self.__class__.__name__} service",
            )
        self._metadata = metadata
        self._lifecycle = LifecycleTracker(ServiceState.REGISTERED)
        self._last_error: str | None = None

    # ---------------------------------------------------------
    # Backward-compatible property abstractions
    # ---------------------------------------------------------

    @property
    def metadata(self) -> ServiceMetadata:
        """Return the service metadata."""
        return self._metadata

    @property
    def name(self) -> str:
        """Return the service name."""
        return self._metadata.name

    @property
    def description(self) -> str:
        """Return the service description."""
        return self._metadata.description

    @property
    def version(self) -> str:
        """Return the service version."""
        return self._metadata.version

    @property
    def enabled(self) -> bool:
        """Return whether the service is enabled / running."""
        return self.is_running()

    # ---------------------------------------------------------
    # Lifecycle Methods
    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the service and prepare resources prior to starting.
        """
        self._lifecycle.transition_to(ServiceState.INITIALIZED)

    def start(self) -> None:
        """
        Start the service.
        """
        if self._lifecycle.state == ServiceState.REGISTERED:
            self.initialize()
        self._lifecycle.transition_to(ServiceState.STARTED)
        self._lifecycle.transition_to(ServiceState.RUNNING)

    def stop(self) -> None:
        """
        Stop the service.
        """
        self._lifecycle.transition_to(ServiceState.STOPPING)
        self._lifecycle.transition_to(ServiceState.STOPPED)

    def shutdown(self) -> None:
        """
        Shut down the service and permanently release resources.
        """
        if self._lifecycle.state not in (ServiceState.STOPPED, ServiceState.SHUTDOWN):
            self.stop()
        self._lifecycle.transition_to(ServiceState.SHUTDOWN)

    # ---------------------------------------------------------
    # Health & Diagnostics
    # ---------------------------------------------------------

    def health(self) -> ServiceHealth | bool:
        """
        Return the health report of the service.
        """
        status = HealthStatus.HEALTHY if self.is_running() else HealthStatus.UNKNOWN
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=f"State: {self.status.name}",
        )

    @property
    def status(self) -> ServiceState:
        """Return the current service state."""
        return self._lifecycle.state

    def is_running(self) -> bool:
        """Return True if the service is in STARTED or RUNNING state."""
        return self._lifecycle.is_running()

    def last_error(self) -> str | None:
        """Return the last recorded error message, if any."""
        return self._last_error

    def set_error(self, error: Exception | str) -> None:
        """Record an error and mark lifecycle as FAILED if unrecoverable."""
        self._last_error = str(error)
        if self._lifecycle.can_transition_to(ServiceState.FAILED):
            self._lifecycle.transition_to(ServiceState.FAILED)

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Optional execution hook for runnable services.
        """
        return None

    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled!r}"
            f")"
        )


__all__ = [
    "Service",
]