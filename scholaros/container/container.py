from __future__ import annotations

from typing import Any
from scholaros.container.scope import Scope
from scholaros.container.builder import Builder
from scholaros.container.exceptions import ServiceNotFound
from scholaros.container.lifetime import ServiceLifetime
from scholaros.container.registry import ServiceRegistry


class Container:
    """
    Public Dependency Injection Container.

    Responsibilities:
        • Register services.
        • Resolve services.
        • Apply lifetime policy.
        • Delegate object construction to Builder.
    """
    def create_scope(self) -> Scope:
     return Scope(self.registry)

    def __init__(self) -> None:
        self.registry = ServiceRegistry()
        self.builder = Builder(self.resolve)

    def add_singleton(
        self,
        interface: type,
        implementation: type,
    ) -> None:

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SINGLETON,
        )

    def add_scoped(
        self,
        interface: type,
        implementation: type,
    ) -> None:

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SCOPED,
        )

    def add_transient(
        self,
        interface: type,
        implementation: type,
    ) -> None:

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.TRANSIENT,
        )

    def resolve(self, interface: type) -> Any:

        if not self.registry.contains(interface):
            raise ServiceNotFound(interface.__name__)

        descriptor = self.registry.get(interface)

        if descriptor.lifetime == ServiceLifetime.SINGLETON:

            if descriptor.instance is None:
                descriptor.instance = self.builder.build(
                    descriptor.implementation
                )

            return descriptor.instance

        return self.builder.build(
            descriptor.implementation
        )