"""
ScholarOS Knowledge Source.

Represents the origin, provenance, and locator of a knowledge document.
"""

from __future__ import annotations

from typing import Any


class KnowledgeSource:
    """
    Provenance and locator record for a knowledge document.
    """

    def __init__(
        self,
        identifier: str = "",
        source_type: str = "file",
        uri: str = "",
        metadata: dict[str, Any] | None = None,
        type: str | None = None,
        location: str | None = None,
        id: str | None = None,
    ) -> None:
        self.source_type = type or source_type
        self.uri = location or uri
        self.identifier = id or identifier or f"{self.source_type}:{self.uri or 'source'}"
        self.metadata = metadata if metadata is not None else {}

    @property
    def id(self) -> str:
        """Return source identifier."""
        return self.identifier

    @property
    def type(self) -> str:
        """Return source type (alias for source_type)."""
        return self.source_type

    @property
    def location(self) -> str:
        """Return source location (alias for uri)."""
        return self.uri

    def to_dict(self) -> dict[str, Any]:
        """Serialize source to dictionary."""
        return {
            "id": self.identifier,
            "identifier": self.identifier,
            "type": self.source_type,
            "source_type": self.source_type,
            "location": self.uri,
            "uri": self.uri,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeSource:
        """Deserialize source from dictionary."""
        return cls(
            identifier=data.get("identifier") or data.get("id") or "",
            source_type=data.get("source_type") or data.get("type") or "file",
            uri=data.get("uri") or data.get("location") or "",
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return f"KnowledgeSource(type={self.source_type!r}, uri={self.uri!r})"


Source = KnowledgeSource

__all__ = [
    "KnowledgeSource",
    "Source",
]
