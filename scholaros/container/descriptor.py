"""
ScholarOS Container Service Descriptor.

Stores metadata and specifications for service registrations in the DI container.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from scholaros.container.lifetime import ServiceLifetime
from scholaros.container.provider import (
    ConstructorProvider,
    FactoryProvider,
    InstanceProvider,
    ServiceProvider,
)


@dataclass(slots=True)
class ServiceDescriptor:
    """
    Holds registration specifications for a service in the container.
    """

    interface: type
    implementation: type | None = None
    factory: Callable[..., Any] | None = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    instance: Any = None
    provider: ServiceProvider[Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.provider is None:
            if self.instance is not None:
                self.provider = InstanceProvider(self.instance)
            elif self.factory is not None:
                self.provider = FactoryProvider(self.factory, lifetime=self.lifetime)
            elif self.implementation is not None:
                self.provider = ConstructorProvider(self.implementation, lifetime=self.lifetime)

    @property
    def is_singleton(self) -> bool:
        """Return True if lifetime is Singleton."""
        return self.lifetime == ServiceLifetime.SINGLETON

    @property
    def is_scoped(self) -> bool:
        """Return True if lifetime is Scoped."""
        return self.lifetime == ServiceLifetime.SCOPED

    @property
    def is_transient(self) -> bool:
        """Return True if lifetime is Transient."""
        return self.lifetime == ServiceLifetime.TRANSIENT

    @property
    def has_instance(self) -> bool:
        """Return True if an instance is already created/cached."""
        return self.instance is not None

    @property
    def has_factory(self) -> bool:
        """Return True if a factory is registered for this service."""
        return self.factory is not None


__all__ = [
    "ServiceDescriptor",
]