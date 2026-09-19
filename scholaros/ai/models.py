"""
ScholarOS AI Models and Specifications.

Provides metadata, capability tracking, pricing, and context limits for AI models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class ModelTier(Enum):
    """Classification tiers for models based on performance and cost."""

    FLAGSHIP = auto()
    BALANCED = auto()
    FAST = auto()
    EMBEDDING = auto()


class ModelCapability(Enum):
    """Capabilities supported by models."""

    TEXT = "text"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    EMBEDDINGS = "embeddings"
    STREAMING = "streaming"


@dataclass(slots=True, frozen=True)
class ModelSpec:
    """
    Specification and capabilities of an AI model.
    """

    name: str
    provider: str
    context_window: int = 8192
    max_output_tokens: int = 4096
    tier: ModelTier = ModelTier.BALANCED
    capabilities: frozenset[str] = field(
        default_factory=lambda: frozenset({ModelCapability.TEXT.value, ModelCapability.STREAMING.value})
    )
    input_cost_per_1m: float = 0.0
    output_cost_per_1m: float = 0.0

    def supports(self, capability: str | ModelCapability) -> bool:
        """Check if model supports a given capability."""
        cap = capability.value if isinstance(capability, ModelCapability) else str(capability)
        return cap in self.capabilities


# Predefined model specifications
KNOWN_MODELS: dict[str, ModelSpec] = {
    # OpenAI
    "gpt-4o": ModelSpec(
        name="gpt-4o",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        tier=ModelTier.FLAGSHIP,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=5.0,
        output_cost_per_1m=15.0,
    ),
    "gpt-4o-mini": ModelSpec(
        name="gpt-4o-mini",
        provider="openai",
        context_window=128000,
        max_output_tokens=16384,
        tier=ModelTier.FAST,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=0.15,
        output_cost_per_1m=0.60,
    ),
    "text-embedding-3-small": ModelSpec(
        name="text-embedding-3-small",
        provider="openai",
        context_window=8191,
        max_output_tokens=0,
        tier=ModelTier.EMBEDDING,
        capabilities=frozenset({ModelCapability.EMBEDDINGS.value}),
        input_cost_per_1m=0.02,
        output_cost_per_1m=0.0,
    ),
    # Anthropic
    "claude-3-5-sonnet": ModelSpec(
        name="claude-3-5-sonnet",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=8192,
        tier=ModelTier.FLAGSHIP,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=3.0,
        output_cost_per_1m=15.0,
    ),
    "claude-3-haiku": ModelSpec(
        name="claude-3-haiku",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        tier=ModelTier.FAST,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=0.25,
        output_cost_per_1m=1.25,
    ),
    # Google
    "gemini-1.5-pro": ModelSpec(
        name="gemini-1.5-pro",
        provider="google",
        context_window=2000000,
        max_output_tokens=8192,
        tier=ModelTier.FLAGSHIP,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=3.5,
        output_cost_per_1m=10.5,
    ),
    "gemini-1.5-flash": ModelSpec(
        name="gemini-1.5-flash",
        provider="google",
        context_window=1000000,
        max_output_tokens=8192,
        tier=ModelTier.FAST,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.VISION.value,
            ModelCapability.FUNCTION_CALLING.value,
            ModelCapability.STREAMING.value,
        }),
        input_cost_per_1m=0.35,
        output_cost_per_1m=1.05,
    ),
    # Ollama
    "llama3": ModelSpec(
        name="llama3",
        provider="ollama",
        context_window=8192,
        max_output_tokens=4096,
        tier=ModelTier.BALANCED,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.STREAMING.value,
        }),
    ),
    "nomic-embed-text": ModelSpec(
        name="nomic-embed-text",
        provider="ollama",
        context_window=8192,
        max_output_tokens=0,
        tier=ModelTier.EMBEDDING,
        capabilities=frozenset({ModelCapability.EMBEDDINGS.value}),
    ),
    # Mock for testing
    "mock-model": ModelSpec(
        name="mock-model",
        provider="mock",
        context_window=32768,
        max_output_tokens=4096,
        tier=ModelTier.BALANCED,
        capabilities=frozenset({
            ModelCapability.TEXT.value,
            ModelCapability.STREAMING.value,
            ModelCapability.EMBEDDINGS.value,
            ModelCapability.FUNCTION_CALLING.value,
        }),
    ),
}


def get_model_spec(model_name: str) -> ModelSpec:
    """
    Retrieve model specification by name, or return a default fallback spec.
    """
    normalized = model_name.strip().lower()
    if normalized in KNOWN_MODELS:
        return KNOWN_MODELS[normalized]

    # Try matching prefix
    for key, spec in KNOWN_MODELS.items():
        if normalized.startswith(key):
            return spec

    # Generic fallback
    return ModelSpec(name=model_name, provider="unknown")


__all__ = [
    "KNOWN_MODELS",
    "ModelCapability",
    "ModelSpec",
    "ModelTier",
    "get_model_spec",
]
