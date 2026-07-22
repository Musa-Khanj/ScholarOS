from __future__ import annotations

from typing import Any
from typing import TypeVar

from scholaros.kernel.provider import ServiceProvider

T = TypeVar("T")


class ServiceContainer:
    def __init__(self) -> None:
        self._services: dict[tuple[type[Any], str | None], ServiceProvider[Any]] = {}

    def register(
        self,
        interface: type[T],
        implementation: T,
        *,
        singleton: bool = True,
        name: str | None = None,
    ) -> None:
        key = (interface, name)

        self._services[key] = ServiceProvider(
            interface=interface,
            implementation=implementation,
            singleton=singleton,
            name=name,
        )

    def resolve(
        self,
        interface: type[T],
        *,
        name: str | None = None,
    ) -> T:
        key = (interface, name)

        provider = self._services[key]

        return provider.implementation

    def registered(
        self,
        interface: type[Any],
        *,
        name: str | None = None,
    ) -> bool:
        return (interface, name) in self._services

    def unregister(
        self,
        interface: type[Any],
        *,
        name: str | None = None,
    ) -> None:
        self._services.pop((interface, name), None)

    def clear(self) -> None:
        self._services.clear()