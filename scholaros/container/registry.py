"""
ScholarOS Container Service Registry.

Pure registration store for service descriptors without any resolution logic.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Callable

from scholaros.container.descriptor import ServiceDescriptor
from scholaros.container.exceptions import (
    RegistrationError,
    ServiceAlreadyRegistered,
    ServiceNotFound,
)
from scholaros.container.lifetime import ServiceLifetime


class ServiceRegistry:
    """
    Stores and manages service descriptors.
    Contains solely registration storage and retrieval; no resolution logic.
    """

    def __init__(self) -> None:
        self._services: dict[type, ServiceDescriptor] = {}

    def register(
        self,
        interface: type,
        implementation: type,
        lifetime: ServiceLifetime,
        metadata: dict[str, Any] | None = None,
    ) -> ServiceDescriptor:
        """Register a service type with an implementation and lifetime."""
        if not isinstance(interface, type):
            raise RegistrationError(f"Interface must be a type, got {type(interface).__name__}")
        if not isinstance(implementation, type):
            raise RegistrationError(f"Implementation must be a type, got {type(implementation).__name__}")

        if interface in self._services:
            raise ServiceAlreadyRegistered(interface.__name__)

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime,
            metadata=metadata or {},
        )
        self._services[interface] = descriptor
        return descriptor

    def register_factory(
        self,
        interface: type,
        factory: Callable[..., Any],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        metadata: dict[str, Any] | None = None,
    ) -> ServiceDescriptor:
        """Register a service interface with a factory callable."""
        if not isinstance(interface, type):
            raise RegistrationError(f"Interface must be a type, got {type(interface).__name__}")
        if not callable(factory):
            raise RegistrationError(f"Factory must be callable, got {type(factory).__name__}")

        if interface in self._services:
            raise ServiceAlreadyRegistered(interface.__name__)

        descriptor = ServiceDescriptor(
            interface=interface,
            factory=factory,
            lifetime=lifetime,
            metadata=metadata or {},
        )
        self._services[interface] = descriptor
        return descriptor

    def register_instance(
        self,
        interface: type,
        instance: Any,
        metadata: dict[str, Any] | None = None,
    ) -> ServiceDescriptor:
        """Register a pre-existing singleton instance."""
        if not isinstance(interface, type):
            raise RegistrationError(f"Interface must be a type, got {type(interface).__name__}")

        if interface in self._services:
            raise ServiceAlreadyRegistered(interface.__name__)

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=type(instance),
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance,
            metadata=metadata or {},
        )
        self._services[interface] = descriptor
        return descriptor

    def register_descriptor(self, descriptor: ServiceDescriptor) -> None:
        """Store an existing ServiceDescriptor directly."""
        if descriptor.interface in self._services:
            raise ServiceAlreadyRegistered(descriptor.interface.__name__)
        self._services[descriptor.interface] = descriptor

    def get(self, interface: type) -> ServiceDescriptor:
        """Retrieve the ServiceDescriptor for an interface."""
        if interface not in self._services:
            raise ServiceNotFound(interface.__name__)
        return self._services[interface]

    def contains(self, interface: type) -> bool:
        """Check if an interface is registered."""
        return interface in self._services

    def unregister(self, interface: type) -> bool:
        """Remove a registration for an interface."""
        return self._services.pop(interface, None) is not None

    def clear(self) -> None:
        """Remove all registrations."""
        self._services.clear()

    def descriptors(self) -> tuple[ServiceDescriptor, ...]:
        """Return all registered service descriptors."""
        return tuple(self._services.values())

    def find_by_name(self, name: str) -> type | None:
        """Find a registered interface matching name case-insensitively."""
        normalized = name.lower()
        for interface in self._services:
            if interface.__name__.lower() == normalized:
                return interface
        return None

    def __contains__(self, interface: type) -> bool:
        return self.contains(interface)

    def __len__(self) -> int:
        return len(self._services)

    def __iter__(self) -> Iterator[type]:
        return iter(self._services)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(registered={len(self._services)})"


__all__ = [
    "ServiceRegistry",
]