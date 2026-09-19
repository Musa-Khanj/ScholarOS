"""
ScholarOS Retrieval Query Model.

Represents a typed query specification for retrieving knowledge items,
chunks, and documents with filtering, limit, and strategy criteria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scholaros.retrieval.exceptions import RetrievalError


@dataclass
class RetrievalQuery:
    """
    Strongly typed specification for a retrieval operation.
    """

    text: str
    limit: int = 10
    min_score: float = 0.0
    collections: list[str] = field(default_factory=list)
    document_ids: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    strategy: str = "default"
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise RetrievalError("RetrievalQuery text cannot be empty or blank.")
        if self.limit <= 0:
            raise RetrievalError(f"RetrievalQuery limit must be > 0, got {self.limit}")

    def with_filter(self, key: str, value: Any) -> RetrievalQuery:
        """Return a copy of the query with an additional metadata filter."""
        new_filters = dict(self.filters)
        new_filters[key] = value
        return RetrievalQuery(
            text=self.text,
            limit=self.limit,
            min_score=self.min_score,
            collections=list(self.collections),
            document_ids=list(self.document_ids),
            filters=new_filters,
            strategy=self.strategy,
            options=dict(self.options),
        )

    def with_limit(self, limit: int) -> RetrievalQuery:
        """Return a copy of the query with a modified result limit."""
        return RetrievalQuery(
            text=self.text,
            limit=limit,
            min_score=self.min_score,
            collections=list(self.collections),
            document_ids=list(self.document_ids),
            filters=dict(self.filters),
            strategy=self.strategy,
            options=dict(self.options),
        )

    def with_strategy(self, strategy: str) -> RetrievalQuery:
        """Return a copy of the query with a modified strategy."""
        return RetrievalQuery(
            text=self.text,
            limit=self.limit,
            min_score=self.min_score,
            collections=list(self.collections),
            document_ids=list(self.document_ids),
            filters=dict(self.filters),
            strategy=strategy,
            options=dict(self.options),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize query to a dictionary."""
        return {
            "text": self.text,
            "limit": self.limit,
            "min_score": self.min_score,
            "collections": list(self.collections),
            "document_ids": list(self.document_ids),
            "filters": dict(self.filters),
            "strategy": self.strategy,
            "options": dict(self.options),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalQuery:
        """Deserialize query from a dictionary."""
        return cls(
            text=data["text"],
            limit=data.get("limit", 10),
            min_score=data.get("min_score", 0.0),
            collections=data.get("collections", []),
            document_ids=data.get("document_ids", []),
            filters=data.get("filters", {}),
            strategy=data.get("strategy", "default"),
            options=data.get("options", {}),
        )


__all__ = [
    "RetrievalQuery",
]
