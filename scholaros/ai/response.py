"""
ScholarOS AI Response Model.

Defines the strongly typed response object returned by all AI providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class AIResponse:
    """
    Represents a response returned by an AI model.
    """

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    role: str = "assistant"
    finish_reason: str | None = None
    latency_ms: float = 0.0
    cost: float = 0.0
    provider: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.total_tokens == 0 and (self.prompt_tokens > 0 or self.completion_tokens > 0):
            object.__setattr__(self, "total_tokens", self.prompt_tokens + self.completion_tokens)

    @property
    def has_content(self) -> bool:
        """Return True if content is non-empty."""
        return bool(self.content and self.content.strip())

    def to_dict(self) -> dict[str, Any]:
        """Serialize response to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "role": self.role,
            "finish_reason": self.finish_reason,
            "latency_ms": self.latency_ms,
            "cost": self.cost,
            "provider": self.provider,
            "raw": self.raw,
            "metadata": self.metadata,
        }


__all__ = [
    "AIResponse",
]
