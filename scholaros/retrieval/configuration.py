"""
ScholarOS Retrieval Configuration.

Provides runtime configuration for retrieval strategies, scoring weights,
rerankers, and context construction budgets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from scholaros.retrieval.exceptions import RetrievalConfigurationError


@dataclass
class RetrievalConfiguration:
    """
    Configuration settings for the retrieval subsystem.
    """

    default_strategy: str = "hybrid"
    default_limit: int = 10
    min_score_threshold: float = 0.0
    semantic_weight: float = 0.5
    keyword_weight: float = 0.5
    rrf_k: int = 60
    default_reranker: str = "score"
    context_token_budget: int = 4000
    enable_metrics: bool = True
    enable_events: bool = True
    extra_options: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate configuration values."""
        if self.default_limit <= 0:
            raise RetrievalConfigurationError(
                f"default_limit must be > 0, got {self.default_limit}"
            )
        if self.context_token_budget <= 0:
            raise RetrievalConfigurationError(
                f"context_token_budget must be > 0, got {self.context_token_budget}"
            )
        if self.semantic_weight < 0.0 or self.keyword_weight < 0.0:
            raise RetrievalConfigurationError(
                "Weights must be non-negative"
            )
        if self.rrf_k <= 0:
            raise RetrievalConfigurationError(
                f"rrf_k must be > 0, got {self.rrf_k}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalConfiguration:
        """Create configuration from dictionary."""
        known_keys = {
            "default_strategy",
            "default_limit",
            "min_score_threshold",
            "semantic_weight",
            "keyword_weight",
            "rrf_k",
            "default_reranker",
            "context_token_budget",
            "enable_metrics",
            "enable_events",
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
    "RetrievalConfiguration",
]
