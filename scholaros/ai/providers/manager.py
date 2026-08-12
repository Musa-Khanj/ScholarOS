"""
ScholarOS
Provider Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
High-level interface for managing AI providers.

Responsibilities
----------------
• Register providers
• Retrieve providers
• Check provider existence
• List registered providers
• Clear provider registry
"""

from __future__ import annotations

from collections.abc import Callable

from scholaros.ai.providers.registry import (
    ProviderRegistry,
)


class ProviderManager:
    """
    High-level manager for AI providers.
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
    ) -> None:

        self._registry = (
            registry
            if registry is not None
            else ProviderRegistry()
        )

    def register(
        self,
        name: str,
        provider: Callable,
    ) -> None:
        """
        Register a provider.
        """

        self._registry.register(
            name,
            provider,
        )

    def get(
        self,
        name: str,
    ) -> Callable:
        """
        Return a registered provider.
        """

        return self._registry.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the provider exists.
        """

        return self._registry.contains(
            name,
        )

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Return all registered provider names.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered providers.
        """

        self._registry.clear()

    @property
    def registry(
        self,
    ) -> ProviderRegistry:
        """
        Return the underlying provider registry.
        """

        return self._registry

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return len(
            self._registry,
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the provider exists.
        """

        return (
            name
            in self._registry
        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered providers.
        """

        return iter(
            self._registry,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(providers={self.names()})"
        )