"""
ScholarOS Service Collection.

Provides a typed, queryable collection for managing multiple services,
supporting filtering by tag, capability, state, and executing bulk operations.
"""

from __future__ import annotations

from typing import (
    Callable,
    Iterable,
    Iterator,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.lifecycle import ServiceState
from scholaros.services.service import Service

T = TypeVar("T", bound=Service)


class ServiceCollection:
    """
    A typed collection of Service instances supporting queries, filtering, and bulk operations.
    """

    def __init__(
        self,
        services: Sequence[Service] | Iterable[Service] | None = None,
    ) -> None:
        self._services: list[Service] = list(services) if services else []
        self._by_name: dict[str, Service] = {s.name: s for s in self._services}

    def add(self, service: Service) -> None:
        """Add or replace a service in the collection."""
        if service.name in self._by_name:
            idx = self._services.index(self._by_name[service.name])
            self._services[idx] = service
        else:
            self._services.append(service)
        self._by_name[service.name] = service

    def remove(self, name: str) -> bool:
        """Remove a service by name. Returns True if removed."""
        if name in self._by_name:
            service = self._by_name.pop(name)
            self._services.remove(service)
            return True
        return False

    def get(self, name: str) -> Service | None:
        """Get a service by name, returning None if not found."""
        return self._by_name.get(name)

    def get_by_type(self, service_type: type[T]) -> T | None:
        """Get the first service matching the given type."""
        for s in self._services:
            if isinstance(s, service_type):
                return s
        return None

    def filter_by_tag(self, tag: str) -> ServiceCollection:
        """Return a new ServiceCollection containing services with the specified tag."""
        matching = [s for s in self._services if tag in s.metadata.tags]
        return ServiceCollection(matching)

    def filter_by_capability(self, capability: str) -> ServiceCollection:
        """Return a new ServiceCollection containing services with the specified capability."""
        matching = [s for s in self._services if capability in s.metadata.capabilities]
        return ServiceCollection(matching)

    def filter_by_state(self, state: ServiceState) -> ServiceCollection:
        """Return a new ServiceCollection containing services in the specified state."""
        matching = [s for s in self._services if s.status == state]
        return ServiceCollection(matching)

    def filter(self, predicate: Callable[[Service], bool]) -> ServiceCollection:
        """Return a new ServiceCollection containing services that satisfy the predicate."""
        matching = [s for s in self._services if predicate(s)]
        return ServiceCollection(matching)

    def start_all(self) -> None:
        """Start all services that are not currently running."""
        for s in self._services:
            if not s.is_running():
                s.start()

    def stop_all(self) -> None:
        """Stop all running services in reverse order."""
        for s in reversed(self._services):
            if s.is_running():
                s.stop()

    def shutdown_all(self) -> None:
        """Shutdown all services in reverse order."""
        for s in reversed(self._services):
            s.shutdown()

    def health_summary(self) -> dict[str, ServiceHealth]:
        """Return a dictionary mapping service names to their health reports."""
        summary: dict[str, ServiceHealth] = {}
        for s in self._services:
            report = s.health()
            if isinstance(report, ServiceHealth):
                summary[s.name] = report
            else:
                status = HealthStatus.HEALTHY if report else HealthStatus.UNHEALTHY
                summary[s.name] = ServiceHealth(
                    service_name=s.name,
                    status=status,
                    details=f"State: {s.status.name}",
                )
        return summary

    def names(self) -> list[str]:
        """Return list of service names."""
        return [s.name for s in self._services]

    def clear(self) -> None:
        """Remove all services from the collection."""
        self._services.clear()
        self._by_name.clear()

    def __len__(self) -> int:
        return len(self._services)

    def __iter__(self) -> Iterator[Service]:
        return iter(self._services)

    @overload
    def __getitem__(self, index: int) -> Service: ...

    @overload
    def __getitem__(self, name: str) -> Service: ...

    def __getitem__(self, key: Union[int, str]) -> Service:
        if isinstance(key, str):
            if key in self._by_name:
                return self._by_name[key]
            raise KeyError(f"Service '{key}' not found in collection.")
        return self._services[key]

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return item in self._by_name
        if isinstance(item, Service):
            return item in self._services
        return False

    def __repr__(self) -> str:
        return f"ServiceCollection(services={len(self._services)})"


__all__ = [
    "ServiceCollection",
]
