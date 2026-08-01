"""
ScholarOS
Dependency Container

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides a lightweight container
built on top of the dependency
resolver.
"""

from __future__ import annotations

from typing import Any

from scholaros.dependency.resolver import DependencyResolver


class DependencyContainer:
    """
    Stores and resolves
    application dependencies.
    """

    def __init__(
        self,
    ) -> None:

        self._resolver = DependencyResolver()

    def register(
        self,
        name: str,
        dependency: Any,
    ) -> None:
        """
        Register a dependency.
        """

        self._resolver.register(
            name,
            dependency,
        )

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a dependency.
        """

        self._resolver.unregister(
            name,
        )

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a dependency.
        """

        return self._resolver.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a dependency
        exists.
        """

        return self._resolver.contains(
            name,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        dependencies.
        """

        self._resolver.clear()

    @property
    def resolver(
        self,
    ) -> DependencyResolver:
        """
        Return the underlying
        dependency resolver.
        """

        return self._resolver

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
            f"{len(self._resolver.dependencies)}"
            f")"
        )