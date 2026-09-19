"""
ScholarOS AI Exceptions.

Defines the typed exception hierarchy for the ScholarOS AI subsystem.
"""

from __future__ import annotations


class AIError(Exception):
    """Base exception for all AI subsystem errors."""


class ProviderError(AIError):
    """Raised when an AI provider fails during an operation."""

    def __init__(self, message: str, provider_name: str | None = None) -> None:
        super().__init__(message)
        self.provider_name = provider_name


class ProviderNotFoundError(AIError):
    """Raised when a requested AI provider is not registered."""


class ModelNotFoundError(AIError):
    """Raised when a requested model is unsupported or not found."""


class RateLimitError(ProviderError):
    """Raised when an AI provider rate limit is exceeded."""


class AuthenticationError(ProviderError):
    """Raised when authentication with an AI provider fails."""


class ContextLengthExceededError(ProviderError):
    """Raised when the input context exceeds the model's maximum window."""


class StreamingError(AIError):
    """Raised when an error occurs during token streaming."""


class EmbeddingError(AIError):
    """Raised when an error occurs generating vector embeddings."""


class MiddlewareError(AIError):
    """Raised when an error occurs in the AI middleware pipeline."""


class SafetyViolationError(AIError):
    """Raised when content violates an AI safety guardrail or policy."""


class AIRequestTimeoutError(ProviderError, TimeoutError):
    """Raised when an AI request or provider operation times out."""

    def __init__(
        self,
        message: str = "AI request timed out",
        provider_name: str | None = None,
        timeout: float | None = None,
    ) -> None:
        super().__init__(message, provider_name=provider_name)
        self.timeout = timeout


__all__ = [
    "AIError",
    "AIRequestTimeoutError",
    "AuthenticationError",
    "ContextLengthExceededError",
    "EmbeddingError",
    "MiddlewareError",
    "ModelNotFoundError",
    "ProviderError",
    "ProviderNotFoundError",
    "RateLimitError",
    "SafetyViolationError",
    "StreamingError",
]
