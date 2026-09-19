"""
ScholarOS Knowledge Chunk.

Represents a discrete semantic chunk or segment of a knowledge document.
"""

from __future__ import annotations

from typing import Any


class Chunk:
    """
    A segmented portion of a knowledge document, used for indexing and vector retrieval.
    """

    def __init__(
        self,
        content: str,
        document_id: str = "",
        identifier: str | None = None,
        id: str | None = None,
        index: int = 0,
        start_char: int = 0,
        end_char: int = 0,
        metadata: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
        token_count: int = 0,
    ) -> None:
        self.identifier = identifier or id or f"{document_id}_chunk_{index}"
        self.document_id = document_id
        self.content = content
        self.index = index
        self.start_char = start_char
        self.end_char = end_char if end_char > 0 else (start_char + len(content))
        self.metadata = metadata if metadata is not None else {}
        self.embedding = embedding
        self.token_count = token_count if token_count > 0 else max(1, len(content.split()))

    @property
    def id(self) -> str:
        """Return chunk id alias."""
        return self.identifier

    @id.setter
    def id(self, value: str) -> None:
        self.identifier = value

    def to_dict(self) -> dict[str, Any]:
        """Serialize chunk to dictionary."""
        return {
            "id": self.identifier,
            "identifier": self.identifier,
            "document_id": self.document_id,
            "content": self.content,
            "index": self.index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "token_count": self.token_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chunk:
        """Deserialize chunk from dictionary."""
        return cls(
            content=data["content"],
            document_id=data.get("document_id", ""),
            identifier=data.get("identifier") or data.get("id"),
            index=data.get("index", 0),
            start_char=data.get("start_char", 0),
            end_char=data.get("end_char", 0),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
            token_count=data.get("token_count", 0),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chunk):
            return False
        return self.identifier == other.identifier

    def __repr__(self) -> str:
        return f"Chunk(id={self.identifier!r}, doc={self.document_id!r}, tokens={self.token_count})"


__all__ = [
    "Chunk",
]
