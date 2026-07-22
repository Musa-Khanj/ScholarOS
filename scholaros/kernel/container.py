from __future__ import annotations

from typing import TypeVar

from scholaros.kernel.service import Service

T = TypeVar("T", bound=Service)


class ServiceContainer:
    def __init__(self) -> None:
        self._services: dict[type[Service], Service] = {}

    def add(self, service: Service) -> None:
        self._services[type(service)] = service

    def get(self, cls: type[T]) -> T:
        return self._services[cls]  # type: ignore[return-value]

    def has(self, cls: type[Service]) -> bool:
        return cls in self._services

    def remove(self, cls: type[Service]) -> None:
        self._services.pop(cls, None)

    def clear(self) -> None:
        self._services.clear()