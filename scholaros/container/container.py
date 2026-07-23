from __future__ import annotations

from scholaros.container.exceptions import ServiceNotFound
from scholaros.container.lifetime import ServiceLifetime
from scholaros.container.registry import ServiceRegistry


class Container:

    def __init__(self):
        self.registry = ServiceRegistry()

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

    def resolve(self, interface: type):

        if not self.registry.contains(interface):
            raise ServiceNotFound(interface.__name__)

        descriptor = self.registry.get(interface)

        if descriptor.lifetime == ServiceLifetime.SINGLETON:

            if descriptor.instance is None:
                descriptor.instance = descriptor.implementation()

            return descriptor.instance

        return descriptor.implementation()