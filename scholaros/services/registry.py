"""
ScholarOS Service Registry.

Stores service registrations, running/stopped state, metadata, and dependencies.
Contains purely registration storage, query, and lookup; contains NO lifecycle logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from scholaros.services.descriptor import ServiceDescriptor
from scholaros.services.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)

if TYPE_CHECKING:
    from scholaros.services.service import Service


class ServiceRegistry:
    """
    Pure registration and query repository for services.
    """

    def __init__(self) -> None:
        self._descriptors: dict[str, ServiceDescriptor] = {}
        self._type_index: dict[type[Service], str] = {}

    def register(self, descriptor: ServiceDescriptor) -> None:
        """
        Store a service descriptor.

        Raises
        ------
        ServiceAlreadyRegisteredError
            If a service with this name is already registered.
        """
        if descriptor.name in self._descriptors:
            raise ServiceAlreadyRegisteredError(
                f"Service '{descriptor.name}' is already registered."
            )

        self._descriptors[descriptor.name] = descriptor
        self._type_index[descriptor.service_type] = descriptor.name

    def unregister(self, name: str) -> bool:
        """
        Remove a service descriptor by name.
        """
        descriptor = self._descriptors.pop(name, None)
        if descriptor is not None:
            self._type_index.pop(descriptor.service_type, None)
            return True
        return False

    def get(self, name: str) -> ServiceDescriptor:
        """
        Retrieve a ServiceDescriptor by name.

        Raises
        ------
        ServiceNotFoundError
            If no service with the specified name exists.
        """
        if name not in self._descriptors:
            raise ServiceNotFoundError(f"Service '{name}' was not found.")
        return self._descriptors[name]

    def get_by_type(self, service_type: type[Service]) -> ServiceDescriptor | None:
        """Retrieve a ServiceDescriptor by concrete service type or subclass."""
        if service_type in self._type_index:
            name = self._type_index[service_type]
            return self._descriptors.get(name)

        # Search hierarchy if exact match not found
        for desc in self._descriptors.values():
            if issubclass(desc.service_type, service_type):
                return desc
        return None

    def contains(self, name: str) -> bool:
        """Return True if service name is registered."""
        return name in self._descriptors

    def registered_names(self) -> list[str]:
        """Return list of all registered service names sorted."""
        return sorted(self._descriptors.keys())

    def descriptors(self) -> list[ServiceDescriptor]:
        """Return list of all registered descriptors."""
        return list(self._descriptors.values())

    def clear(self) -> None:
        """Remove all registrations."""
        self._descriptors.clear()
        self._type_index.clear()

    def __len__(self) -> int:
        return len(self._descriptors)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.contains(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._descriptors)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(services={len(self._descriptors)})"


__all__ = [
    "ServiceRegistry",
]
