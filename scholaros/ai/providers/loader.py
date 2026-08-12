"""
ScholarOS
Provider Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads the built-in AI providers into the
ProviderManager.

Responsibilities
----------------
• Register built-in providers
• Avoid duplicate registrations
"""

from __future__ import annotations

from scholaros.ai.llm.anthropic import (
    AnthropicLLM,
)
from scholaros.ai.llm.ollama import (
    OllamaLLM,
)
from scholaros.ai.llm.openai import (
    OpenAILLM,
)
from scholaros.ai.providers.manager import (
    ProviderManager,
)


class ProviderLoader:
    """
    Loads built-in LLM providers.
    """

    _BUILTINS = (
        (
            "ollama",
            OllamaLLM,
        ),
        (
            "openai",
            OpenAILLM,
        ),
        (
            "anthropic",
            AnthropicLLM,
        ),
    )

    def __init__(
        self,
        manager: ProviderManager,
    ) -> None:

        self._manager = manager

    def load(
        self,
    ) -> None:
        """
        Register all built-in providers.
        """

        for (
            name,
            provider,
        ) in self._BUILTINS:

            if not self._manager.contains(
                name,
            ):
                self._manager.register(
                    name,
                    provider,
                )

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
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(providers={len(self._BUILTINS)})"
        )