"""
ScholarOS RAG Configuration.

Provides runtime configuration for RAG pipelines, including retrieval strategy,
token budgets, system prompts, timeouts, and fallback policies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from scholaros.knowledge.rag.exceptions import RAGConfigurationError


@dataclass
class RAGConfiguration:
    """
    Configuration settings for RAG execution pipelines.
    """

    default_strategy: str = "default"
    default_limit: int = 10
    default_min_score: float = 0.0
    default_max_tokens: int = 4000
    system_prompt: str | None = None
    fallback_on_empty: bool = False
    empty_fallback_message: str | None = None
    enable_events: bool = True
    enable_metrics: bool = True
    timeout_seconds: float = 30.0
    extra_options: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.default_limit <= 0:
            raise RAGConfigurationError(
                f"default_limit must be > 0, got {self.default_limit}"
            )
        if self.default_max_tokens <= 0:
            raise RAGConfigurationError(
                f"default_max_tokens must be > 0, got {self.default_max_tokens}"
            )
        if self.default_min_score < 0.0:
            raise RAGConfigurationError(
                f"default_min_score must be >= 0.0, got {self.default_min_score}"
            )
        if self.timeout_seconds <= 0.0:
            raise RAGConfigurationError(
                f"timeout_seconds must be > 0.0, got {self.timeout_seconds}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RAGConfiguration:
        """Create a validated RAGConfiguration instance from a dictionary."""
        known_keys = {
            "default_strategy",
            "default_limit",
            "default_min_score",
            "default_max_tokens",
            "system_prompt",
            "fallback_on_empty",
            "empty_fallback_message",
            "enable_events",
            "enable_metrics",
            "timeout_seconds",
            "extra_options",
        }
        kwargs: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        for k, v in data.items():
            if k in known_keys:
                kwargs[k] = v
            else:
                extra[k] = v

        if extra:
            if "extra_options" in kwargs and isinstance(kwargs["extra_options"], dict):
                kwargs["extra_options"].update(extra)
            else:
                kwargs["extra_options"] = extra

        cfg = cls(**kwargs)
        cfg.validate()
        return cfg


__all__ = [
    "RAGConfiguration",
]
