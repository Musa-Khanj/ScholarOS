"""
ScholarOS Service Provider.

Integrates the ScholarOS ServiceManager with the Dependency Injection Container,
exposing registered services to the application's inversion-of-control graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from scholaros.container.container import Container
    from scholaros.services.manager import ServiceManager
    from scholaros.services.service import Service

T = TypeVar("T", bound="Service")


class ServiceProvider:
    """
    Bridges ServiceManager and Container, allowing services managed by the
    service subsystem to be resolved through the DI container.
    """

    def __init__(
        self,
        manager: ServiceManager,
        container: Container | None = None,
    ) -> None:
        self.manager = manager
        self.container = container
        if container is not None:
            self.bind(container)

    def bind(self, container: Container) -> None:
        """
        Bind the ServiceManager and its registered services into the DI container.
        """
        self.container = container
        # Register the manager itself as an instance in the container
        from scholaros.services.manager import ServiceManager

        container.add_instance(ServiceManager, self.manager)

        # Register all currently available services into container
        self.register_services(container)

    def register_services(self, container: Container) -> None:
        """
        Register all services from ServiceManager into the container.
        """
        for desc in self.manager.registry.descriptors():
            self._register_descriptor(container, desc)

    def register_service(self, container: Container, name: str) -> None:
        """
        Register a specific service by name into the container.
        """
        desc = self.manager.registry.get(name)
        self._register_descriptor(container, desc)

    def _register_descriptor(self, container: Container, desc: object) -> None:
        from scholaros.services.descriptor import ServiceDescriptor

        if not isinstance(desc, ServiceDescriptor):
            return

        if desc.instance is not None:
            container.add_instance(desc.service_type, desc.instance)
        elif desc.factory is not None:
            container.add_factory(desc.service_type, desc.factory)

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service by type from the container or fallback to ServiceManager.
        """
        if self.container is not None:
            try:
                resolved: T = self.container.resolve(service_type)
                return resolved
            except Exception:
                pass

        by_type = self.manager.get_by_type(service_type)
        if by_type is not None:
            return by_type  # type: ignore[return-value]

        raise LookupError(f"Could not resolve service of type {service_type.__name__}.")


def configure_services(
    container: Container,
    manager: ServiceManager | None = None,
) -> ServiceManager:
    """
    Convenience function to create or bind a ServiceManager to a Container.
    """
    if manager is None:
        from scholaros.services.manager import ServiceManager

        manager = ServiceManager(container=container)

    provider = ServiceProvider(manager=manager, container=container)
    return manager


__all__ = [
    "ServiceProvider",
    "configure_services",
]
