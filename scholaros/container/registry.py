from __future__ import annotations

from scholaros.container.descriptor import ServiceDescriptor
from scholaros.container.exceptions import ServiceAlreadyRegistered
from scholaros.container.lifetime import ServiceLifetime


class ServiceRegistry:

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}

    def register(
        self,
        interface: type,
        implementation: type,
        lifetime: ServiceLifetime,
    ) -> None:

        if interface in self._services:
            raise ServiceAlreadyRegistered(interface.__name__)

        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime,
        )

    def get(self, interface: type) -> ServiceDescriptor:
        return self._services[interface]

    def contains(self, interface: type) -> bool:
        return interface in self._services