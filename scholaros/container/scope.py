from __future__ import annotations

from typing import Any

from scholaros.container.builder import Builder
from scholaros.container.exceptions import ServiceNotFound
from scholaros.container.lifetime import ServiceLifetime
from scholaros.container.registry import ServiceRegistry


class Scope:

    def __init__(
        self,
        registry: ServiceRegistry,
    ) -> None:

        self._registry = registry
        self._instances: dict[type, Any] = {}
        self._builder = Builder(self.resolve)

    def resolve(
        self,
        interface: type,
    ) -> Any:

        if not self._registry.contains(interface):
            raise ServiceNotFound(interface.__name__)

        descriptor = self._registry.get(interface)

        if descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._builder.build(
                descriptor.implementation
            )

        if descriptor.lifetime == ServiceLifetime.SCOPED:

            if interface not in self._instances:
                self._instances[interface] = self._builder.build(
                    descriptor.implementation
                )

            return self._instances[interface]

        if descriptor.instance is None:
            descriptor.instance = self._builder.build(
                descriptor.implementation
            )

        return descriptor.instance