"""
ScholarOS Service Manager.

Central orchestrator for ScholarOS services, responsible for:
- Discovery (scanning modules and packages)
- Registration (storing descriptors and instances)
- Dependency ordering (topological startup and reverse shutdown)
- Lifecycle management (initialize, start, stop, restart, shutdown)
- Diagnostics (uptime, durations, failure and restart counters)
- Health reporting
- Event publishing (publishing lifecycle events to EventBus)
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable, Iterator, TypeVar

from scholaros.services.dependency import ServiceDependencyResolver
from scholaros.services.descriptor import ServiceDescriptor
from scholaros.services.diagnostics import ServiceDiagnostics
from scholaros.services.discovery import DiscoveredService, ServiceDiscovery
from scholaros.services.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceLifecycleError,
    ServiceNotFoundError,
)
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.lifecycle import (
    ServiceFailed,
    ServiceInitialized,
    ServiceLifecycleEvent,
    ServiceRegistered,
    ServiceRestarted,
    ServiceShutdown,
    ServiceStarted,
    ServiceState,
    ServiceStopped,
)
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.registry import ServiceRegistry
from scholaros.services.service import Service
from scholaros.services.service_collection import ServiceCollection

if TYPE_CHECKING:
    from scholaros.container.container import Container
    from scholaros.events.bus import EventBus

T = TypeVar("T", bound=Service)


class ServiceManager:
    """
    Central manager for ScholarOS services.
    """

    def __init__(
        self,
        registry: ServiceRegistry | None = None,
        resolver: ServiceDependencyResolver | None = None,
        discovery: ServiceDiscovery | None = None,
        event_bus: EventBus | None = None,
        container: Container | None = None,
    ) -> None:
        self.registry = registry if registry is not None else ServiceRegistry()
        self.resolver = resolver if resolver is not None else ServiceDependencyResolver()
        self.discovery = discovery if discovery is not None else ServiceDiscovery()
        self.event_bus = event_bus
        self.container = container

        # Internal dictionary kept in sync for backwards compatibility
        self._services: dict[str, Service] = {}

    # ---------------------------------------------------------
    # Registration & Discovery
    # ---------------------------------------------------------

    def register(
        self,
        service: Service,
        metadata: ServiceMetadata | None = None,
        factory: Callable[..., Service] | None = None,
    ) -> ServiceDescriptor:
        """
        Register a service instance with the manager.
        """
        name = service.name
        meta = metadata or getattr(service, "metadata", None) or ServiceMetadata(name=name)
        deps = tuple(meta.dependencies)

        descriptor = ServiceDescriptor(
            name=name,
            service_type=type(service),
            instance=service,
            factory=factory,
            metadata=meta,
            dependencies=deps,
        )

        self.registry.register(descriptor)
        self._services[name] = service

        self._publish(ServiceRegistered(service_name=name, state=service.status))
        return descriptor

    def register_type(
        self,
        service_type: type[Service],
        factory: Callable[..., Service] | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> ServiceDescriptor:
        """
        Register a service class or factory before instantiation.
        """
        name = getattr(service_type, "name", service_type.__name__)
        meta = metadata or ServiceMetadata(name=name)
        deps = tuple(meta.dependencies)

        descriptor = ServiceDescriptor(
            name=name,
            service_type=service_type,
            instance=None,
            factory=factory or (lambda: service_type()),
            metadata=meta,
            dependencies=deps,
        )

        self.registry.register(descriptor)
        return descriptor

    def unregister(self, name: str) -> None:
        """
        Unregister a service. If the service is running, stops it first.
        """
        if self.contains(name):
            service = self._services.get(name)
            if service is not None and service.is_running():
                self.stop(name)

            self.registry.unregister(name)
            self._services.pop(name, None)

    def get(self, name: str) -> Service:
        """
        Retrieve a service instance by name. If not yet instantiated, instantiates it.
        """
        if name in self._services:
            return self._services[name]

        desc = self.registry.get(name)
        if desc.instance is None:
            if desc.factory is not None:
                desc.instance = desc.factory()
            else:
                desc.instance = desc.service_type()
            self._services[name] = desc.instance
        return desc.instance

    def get_by_type(self, service_type: type[T]) -> T | None:
        """
        Retrieve a service instance matching the given type.
        """
        for s in self._services.values():
            if isinstance(s, service_type):
                return s

        desc = self.registry.get_by_type(service_type)
        if desc is not None:
            svc = self.get(desc.name)
            if isinstance(svc, service_type):
                return svc
        return None

    def contains(self, name: str) -> bool:
        """Return True if service name is registered."""
        return name in self._services or self.registry.contains(name)

    def registered(self) -> list[str]:
        """Return sorted list of registered service names."""
        names = set(self._services.keys()) | set(self.registry.registered_names())
        return sorted(names)

    def clear(self) -> None:
        """Unregister and clear all services."""
        self.registry.clear()
        self._services.clear()

    @property
    def services(self) -> dict[str, Service]:
        """Return dictionary of registered service instances."""
        return self._services

    def collection(self) -> ServiceCollection:
        """Return a typed ServiceCollection of all current service instances."""
        return ServiceCollection(list(self._services.values()))

    def discover(
        self,
        package_or_module: str,
        auto_register: bool = True,
    ) -> list[DiscoveredService]:
        """
        Scan a module or package for Service subclasses.
        """
        discovered = self.discovery.discover_package(package_or_module)
        if not discovered:
            discovered = self.discovery.discover_module(package_or_module)

        if auto_register:
            for item in discovered:
                try:
                    instance = item.instantiate()
                    if not self.contains(instance.name):
                        self.register(instance)
                except Exception:
                    pass

        return discovered

    # ---------------------------------------------------------
    # Dependency Resolution
    # ---------------------------------------------------------

    def resolve_startup_order(self) -> list[str]:
        """
        Compute the startup sequence in topological order based on dependencies.
        """
        deps_map: dict[str, tuple[str, ...]] = {}
        for desc in self.registry.descriptors():
            deps_map[desc.name] = desc.dependencies
        for name, service in self._services.items():
            if name not in deps_map:
                deps_map[name] = service.metadata.dependencies
        return self.resolver.resolve_startup_order(deps_map)

    def resolve_shutdown_order(self) -> list[str]:
        """
        Compute the shutdown sequence in reverse topological order.
        """
        deps_map: dict[str, tuple[str, ...]] = {}
        for desc in self.registry.descriptors():
            deps_map[desc.name] = desc.dependencies
        for name, service in self._services.items():
            if name not in deps_map:
                deps_map[name] = service.metadata.dependencies
        return self.resolver.resolve_shutdown_order(deps_map)

    # ---------------------------------------------------------
    # Lifecycle Management
    # ---------------------------------------------------------

    def initialize(self, name: str) -> None:
        """
        Initialize a service.
        """
        service = self.get(name)
        try:
            service.initialize()
            self._publish(ServiceInitialized(service_name=name, state=service.status))
        except Exception as e:
            self._record_error(name, service, e)
            raise

    def start(self, name: str) -> None:
        """
        Start a service and update diagnostics.
        """
        service = self.get(name)
        diag = self.diagnostics(name)
        start_time = time.perf_counter()

        try:
            service.start()
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            diag.record_start(duration_ms)
            self._publish(ServiceStarted(service_name=name, state=service.status))
        except Exception as e:
            self._record_error(name, service, e)
            raise

    def stop(self, name: str) -> None:
        """
        Stop a service and update diagnostics.
        """
        service = self.get(name)
        diag = self.diagnostics(name)

        try:
            service.stop()
            diag.record_stop()
            self._publish(ServiceStopped(service_name=name, state=service.status))
        except Exception as e:
            self._record_error(name, service, e)
            raise

    def restart(self, name: str) -> None:
        """
        Restart a service.
        """
        service = self.get(name)
        diag = self.diagnostics(name)

        if service.is_running():
            self.stop(name)
        self.start(name)
        diag.record_restart()
        self._publish(ServiceRestarted(service_name=name, state=service.status))

    def shutdown(self, name: str) -> None:
        """
        Shut down a service permanently.
        """
        service = self.get(name)
        diag = self.diagnostics(name)

        try:
            service.shutdown()
            diag.record_stop()
            self._publish(ServiceShutdown(service_name=name, state=service.status))
        except Exception as e:
            self._record_error(name, service, e)
            raise

    def start_all(self) -> list[str]:
        """
        Start all registered services in topological dependency order.
        """
        order = self.resolve_startup_order()
        started: list[str] = []
        for name in order:
            service = self.get(name)
            if not service.is_running():
                self.start(name)
                started.append(name)
        return started

    def stop_all(self) -> list[str]:
        """
        Stop all running services in reverse topological dependency order.
        """
        order = self.resolve_shutdown_order()
        stopped: list[str] = []
        for name in order:
            if self.contains(name):
                service = self.get(name)
                if service.is_running():
                    self.stop(name)
                    stopped.append(name)
        return stopped

    def shutdown_all(self) -> list[str]:
        """
        Shutdown all services in reverse topological dependency order.
        """
        order = self.resolve_shutdown_order()
        shutdown_names: list[str] = []
        for name in order:
            if self.contains(name):
                self.shutdown(name)
                shutdown_names.append(name)
        return shutdown_names

    # ---------------------------------------------------------
    # Diagnostics & Health
    # ---------------------------------------------------------

    def diagnostics(self, name: str) -> ServiceDiagnostics:
        """
        Return the diagnostics record for a service.
        """
        if self.registry.contains(name):
            return self.registry.get(name).diagnostics

        service = self._services.get(name)
        if service is None:
            raise ServiceNotFoundError(f"Service '{name}' not found.")

        # If not registered via descriptor, create and store one
        desc = self.register(service)
        return desc.diagnostics

    def diagnostics_all(self) -> dict[str, ServiceDiagnostics]:
        """
        Return diagnostics for all registered services.
        """
        result: dict[str, ServiceDiagnostics] = {}
        for name in self.registered():
            result[name] = self.diagnostics(name)
        return result

    def health(self, name: str) -> ServiceHealth:
        """
        Query the health of a specific service.
        """
        service = self.get(name)
        report = service.health()
        if isinstance(report, ServiceHealth):
            return report

        status = HealthStatus.HEALTHY if report else HealthStatus.UNHEALTHY
        return ServiceHealth(
            service_name=name,
            status=status,
            details=f"State: {service.status.name}",
        )

    def health_all(self) -> dict[str, ServiceHealth]:
        """
        Query the health of all registered services.
        """
        result: dict[str, ServiceHealth] = {}
        for name in self.registered():
            result[name] = self.health(name)
        return result

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _record_error(self, name: str, service: Service, error: Exception) -> None:
        service.set_error(error)
        diag = self.diagnostics(name)
        diag.record_failure(str(error))
        self._publish(ServiceFailed(service_name=name, state=service.status, payload={"error": str(error)}))

    def _publish(self, event: ServiceLifecycleEvent) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(event)  # type: ignore[arg-type]
            except Exception:
                pass

    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------

    def __len__(self) -> int:
        return len(self.registered())

    def __iter__(self) -> Iterator[str]:
        return iter(self.registered())

    def __getitem__(self, name: str) -> Service:
        return self.get(name)

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the ServiceManager.
        """
        return f"{self.__class__.__name__}(services={len(self._services)})"


__all__ = [
    "ServiceManager",
]