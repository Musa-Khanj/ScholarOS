from __future__ import annotations

from collections.abc import Iterator
from typing import Generic
from typing import TypeVar

from scholaros.core.base import Component
from scholaros.core.exceptions import RegistryError

T = TypeVar("T", bound=Component)


class Registry(Generic[T]):
    def __init__(self) -> None:
        self._components: dict[str, T] = {}

    def register(self, component: T) -> None:
        name = component.name

        if name in self._components:
            raise RegistryError(
                f"Component '{name}' already registered."
            )

        self._components[name] = component

    def unregister(self, name: str) -> None:
        if name not in self._components:
            raise RegistryError(
                f"Unknown component '{name}'."
            )

        del self._components[name]

    def get(self, name: str) -> T:
        try:
            return self._components[name]
        except KeyError as exc:
            raise RegistryError(
                f"Component '{name}' not found."
            ) from exc

    def exists(self, name: str) -> bool:
        return name in self._components

    def list(self) -> list[str]:
        return sorted(self._components.keys())

    def clear(self) -> None:
        self._components.clear()

    def __len__(self) -> int:
        return len(self._components)

    def __contains__(self, name: object) -> bool:
        return name in self._components

    def __iter__(self) -> Iterator[T]:
        return iter(self._components.values())