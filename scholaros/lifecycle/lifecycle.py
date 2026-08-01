"""
ScholarOS
Lifecycle Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides lifecycle management
for ScholarOS components.
"""

from __future__ import annotations

from typing import Any


class LifecycleManager:
    """
    Coordinates startup and shutdown
    of ScholarOS components.
    """

    def __init__(
        self,
    ) -> None:

        self._components: dict[
            str,
            Any,
        ] = {}

    def register(
        self,
        name: str,
        component: Any,
    ) -> None:
        """
        Register a lifecycle component.
        """

        self._components[name] = component

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a lifecycle component.
        """

        self._components.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Return a registered component.
        """

        return self._components[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a component
        is registered.
        """

        return (
            name
            in self._components
        )

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered component
        names.
        """

        return sorted(
            self._components,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        components.
        """

        self._components.clear()

    @property
    def components(
        self,
    ) -> dict[
        str,
        Any,
    ]:
        """
        Return all registered
        components.
        """

        return self._components

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"components="
            f"{len(self._components)}"
            f")"
        )