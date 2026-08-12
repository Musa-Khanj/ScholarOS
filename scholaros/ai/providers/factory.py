"""
ScholarOS
Provider Factory

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Factory responsible for constructing LLM provider
instances.

Responsibilities
----------------
• Create provider instances
• Delegate provider lookup to ProviderManager
"""

from __future__ import annotations

from typing import Any

from scholaros.ai.llm.base import LLM
from scholaros.ai.providers.manager import (
    ProviderManager,
)


class ProviderFactory:
    """
    Factory responsible for constructing
    provider instances.
    """

    def __init__(
        self,
        manager: ProviderManager,
    ) -> None:

        self._manager = manager

    def create(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> LLM:
        """
        Create a provider instance.
        """

        provider = self._manager.get(
            name,
        )

        instance = provider(
            *args,
            **kwargs,
        )

        if not isinstance(
            instance,
            LLM,
        ):
            raise TypeError(
                f"Provider '{name}' does not "
                "implement the LLM interface."
            )

        return instance

    @property
    def manager(
        self,
    ) -> ProviderManager:
        """
        Return the underlying ProviderManager.
        """

        return self._manager

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(providers={len(self._manager)})"
        )