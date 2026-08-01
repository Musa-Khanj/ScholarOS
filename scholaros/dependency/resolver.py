"""
ScholarOS
Dependency Resolver

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides dependency resolution
for ScholarOS services and
components.
"""

from __future__ import annotations

from typing import Any


class DependencyResolver:
    """
    Resolves registered
    dependencies.
    """

    def __init__(
        self,
    ) -> None:

        self._dependencies: dict[
            str,
            Any,
        ] = {}

    def register(
        self,
        name: str,
        dependency: Any,
    ) -> None:
        """
        Register a dependency.
        """

        self._dependencies[name] = dependency

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a dependency.
        """

        self._dependencies.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Return the specified
        dependency.
        """

        return self._dependencies[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether the dependency
        exists.
        """

        return (
            name
            in self._dependencies
        )

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered dependency
        names.
        """

        return sorted(
            self._dependencies,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all dependencies.
        """

        self._dependencies.clear()

    @property
    def dependencies(
        self,
    ) -> dict[
        str,
        Any,
    ]:
        """
        Return all registered
        dependencies.
        """

        return self._dependencies

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"dependencies="
            f"{len(self._dependencies)}"
            f")"
        )