"""
ScholarOS
Registry Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates one or more service
registries used throughout
ScholarOS.
"""

from __future__ import annotations

from scholaros.registry.registry import ServiceRegistry


class RegistryManager:
    """
    Manages ServiceRegistry
    instances.
    """

    def __init__(
        self,
    ) -> None:

        self._registries: dict[
            str,
            ServiceRegistry,
        ] = {}

    def register(
        self,
        name: str,
        registry: ServiceRegistry,
    ) -> None:
        """
        Register a registry.
        """

        self._registries[name] = registry

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a registry.
        """

        self._registries.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> ServiceRegistry:
        """
        Return the specified
        registry.
        """

        return self._registries[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether the registry
        exists.
        """

        return (
            name
            in self._registries
        )

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered registry
        names.
        """

        return sorted(
            self._registries,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registries.
        """

        self._registries.clear()

    @property
    def registries(
        self,
    ) -> dict[
        str,
        ServiceRegistry,
    ]:
        """
        Return all registered
        registries.
        """

        return self._registries

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"registries="
            f"{len(self._registries)}"
            f")"
        )