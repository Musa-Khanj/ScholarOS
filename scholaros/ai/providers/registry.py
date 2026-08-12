"""
ScholarOS
Provider Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registry responsible for storing available
LLM providers.

Responsibilities
----------------
• Register providers
• Retrieve providers
• Prevent duplicate registrations
• List registered providers
"""

from __future__ import annotations

from collections.abc import Callable


class ProviderRegistry:
    """
    Registry for available LLM providers.
    """

    def __init__(
        self,
    ) -> None:

        self._providers: dict[
            str,
            Callable,
        ] = {}

    def register(
        self,
        name: str,
        provider: Callable,
    ) -> None:
        """
        Register a provider.
        """

        name = name.strip().lower()

        if not name:
            raise ValueError(
                "Provider name cannot be empty."
            )

        if name in self._providers:
            raise ValueError(
                f"Provider '{name}' is already registered."
            )

        self._providers[name] = provider

    def get(
        self,
        name: str,
    ) -> Callable:
        """
        Return the registered provider.
        """

        name = name.strip().lower()

        try:
            return self._providers[name]

        except KeyError as exc:
            raise KeyError(
                f"Unknown provider '{name}'."
            ) from exc

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the provider exists.
        """

        return (
            name.strip().lower()
            in self._providers
        )

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Return all registered provider names.
        """

        return tuple(
            self._providers.keys()
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered providers.
        """

        self._providers.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return len(
            self._providers
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.contains(
            name,
        )

    def __iter__(
        self,
    ):

        return iter(
            self._providers.items()
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(providers={list(self._providers)})"
        )