"""
ScholarOS Unified AI Provider Interface.

Defines the abstract base contract that every AI model provider must implement:
- generate()
- stream()
- embed()
- health()
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.models import ModelCapability
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamingIterator
from scholaros.services.health import ServiceHealth


class AIProvider(ABC):
    """
    Abstract unified interface for all AI model providers in ScholarOS.
    """

    def __init__(
        self,
        name: str,
        capabilities: set[str] | None = None,
        default_model: str | None = None,
    ) -> None:
        self._name = name.strip().lower()
        self._capabilities = set(capabilities) if capabilities else {
            ModelCapability.TEXT.value,
            ModelCapability.STREAMING.value,
        }
        self._default_model = default_model

    @property
    def name(self) -> str:
        """Return the unique canonical provider name."""
        return self._name

    @property
    def capabilities(self) -> set[str]:
        """Return the set of capabilities supported by this provider."""
        return set(self._capabilities)

    @property
    def default_model(self) -> str | None:
        """Return the default model name for this provider, if configured."""
        return self._default_model

    def supports(self, capability: str | ModelCapability) -> bool:
        """Check if this provider supports a given capability."""
        cap = capability.value if isinstance(capability, ModelCapability) else str(capability)
        return cap in self._capabilities

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate a complete response for the given request.
        """

    @abstractmethod
    def stream(self, request: AIRequest) -> StreamingIterator:
        """
        Stream response tokens incrementally.
        """

    @abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate dense vector embeddings for input text.
        """

    @abstractmethod
    def health(self) -> ServiceHealth:
        """
        Check the availability and connectivity of the provider.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, capabilities={sorted(self.capabilities)})"


__all__ = [
    "AIProvider",
]
