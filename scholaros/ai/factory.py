"""
ScholarOS AI Factory.

Provides factory methods for constructing providers, managers, and clients.
"""

from __future__ import annotations

from typing import Any

from scholaros.ai.client import AIClient
from scholaros.ai.exceptions import ProviderNotFoundError
from scholaros.ai.manager import AIManager
from scholaros.ai.provider import AIProvider
from scholaros.ai.providers.anthropic import AnthropicProvider
from scholaros.ai.providers.google import GoogleProvider
from scholaros.ai.providers.mock import MockProvider
from scholaros.ai.providers.ollama import OllamaProvider
from scholaros.ai.providers.openai import OpenAIProvider
from scholaros.ai.providers.openrouter import OpenRouterProvider
from scholaros.ai.registry import ProviderRegistry


class AIFactory:
    """
    Factory for instantiating AI providers, managers, and clients.
    """

    _PROVIDER_MAP: dict[str, type[AIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
        "mock": MockProvider,
    }

    @classmethod
    def create_provider(cls, name: str, **kwargs: Any) -> AIProvider:
        """
        Instantiate a provider by its canonical name.
        """
        canonical = name.strip().lower()
        if canonical not in cls._PROVIDER_MAP:
            raise ProviderNotFoundError(f"Unknown AI provider '{name}'.")

        provider_cls = cls._PROVIDER_MAP[canonical]
        return provider_cls(**kwargs)

    @classmethod
    def create_manager(
        cls,
        providers: list[str | AIProvider] | None = None,
        default_provider: str | None = None,
        **manager_kwargs: Any,
    ) -> AIManager:
        """
        Construct and configure an AIManager with registered providers.
        """
        registry = ProviderRegistry()
        manager = AIManager(registry=registry, default_provider=default_provider, **manager_kwargs)

        target_providers = providers if providers is not None else ["mock"]
        for p in target_providers:
            if isinstance(p, str):
                prov_instance = cls.create_provider(p)
            else:
                prov_instance = p
            manager.register_provider(prov_instance)

        return manager

    @classmethod
    def create_client(
        cls,
        manager: AIManager | None = None,
        **factory_kwargs: Any,
    ) -> AIClient:
        """
        Construct a fully configured AIClient.
        """
        mgr = manager or cls.create_manager(**factory_kwargs)
        return AIClient(mgr)


__all__ = [
    "AIFactory",
]
