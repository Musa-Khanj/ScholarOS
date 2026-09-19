"""
ScholarOS AI Providers Package.

Exposes provider implementations and management services.
"""

from __future__ import annotations

from scholaros.ai.providers.anthropic import AnthropicProvider
from scholaros.ai.providers.factory import ProviderFactory
from scholaros.ai.providers.google import GoogleProvider
from scholaros.ai.providers.loader import ProviderLoader
from scholaros.ai.providers.manager import ProviderManager
from scholaros.ai.providers.mock import MockProvider
from scholaros.ai.providers.ollama import OllamaProvider
from scholaros.ai.providers.openai import OpenAIProvider
from scholaros.ai.providers.openrouter import OpenRouterProvider
from scholaros.ai.providers.registration import register_ai_services
from scholaros.ai.providers.registry import ProviderRegistry

__all__ = [
    # Providers
    "AnthropicProvider",
    "GoogleProvider",
    "MockProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "OpenRouterProvider",
    # Legacy / Registry exports
    "ProviderFactory",
    "ProviderLoader",
    "ProviderManager",
    "ProviderRegistry",
    "register_ai_services",
]
