"""
ScholarOS Knowledge Document.

Represents a single knowledge document within ScholarOS, with metadata, provenance, and chunks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.knowledge.metadata import KnowledgeMetadata

if TYPE_CHECKING:
    from scholaros.knowledge.chunk import Chunk
    from scholaros.knowledge.source import KnowledgeSource


class KnowledgeDocument:
    """
    Represents a single knowledge document.
    """

    def __init__(
        self,
        identifier: str = "",
        title: str = "",
        content: str = "",
        metadata: KnowledgeMetadata | None = None,
        source: KnowledgeSource | None = None,
        chunks: list[Chunk] | None = None,
        id: str | None = None,
    ) -> None:
        """
        Initialize the knowledge document.
        """
        self._identifier = id or identifier or "doc"
        self._title = title or self._identifier
        self._content = content
        self._metadata = (
            metadata
            if metadata is not None
            else KnowledgeMetadata()
        )
        self._source = source
        self._chunks: list[Chunk] = list(chunks) if chunks else []

    @property
    def id(self) -> str:
        """Return document identifier alias."""
        return self._identifier

    @id.setter
    def id(self, value: str) -> None:
        self._identifier = value

    @property
    def identifier(self) -> str:
        """Return the document identifier."""
        return self._identifier

    @property
    def title(self) -> str:
        """Return the document title."""
        return self._title

    @property
    def content(self) -> str:
        """Return the document content."""
        return self._content

    @property
    def content_hash(self) -> str:
        """Return SHA-256 hash of document content."""
        import hashlib

        return hashlib.sha256(self._content.encode("utf-8")).hexdigest()

    @property
    def status(self) -> str:
        """Return document lifecycle status."""
        status_val = self._metadata.extra.get("status", "draft")
        return str(status_val)

    @status.setter
    def status(self, value: str | Any) -> None:
        """Set document lifecycle status."""
        from scholaros.knowledge.lifecycle import DocumentStatus

        if isinstance(value, DocumentStatus):
            self._metadata.extra["status"] = value.value
        else:
            self._metadata.extra["status"] = str(value)

    @property
    def metadata(self) -> KnowledgeMetadata:
        """Return the document metadata."""
        return self._metadata

    @property
    def source(self) -> KnowledgeSource | None:
        """Return document source provenance."""
        return self._source

    @source.setter
    def source(self, value: KnowledgeSource | None) -> None:
        self._source = value

    @property
    def chunks(self) -> list[Chunk]:
        """Return the list of document chunks."""
        return list(self._chunks)

    def add_chunk(self, chunk: Chunk) -> None:
        """Append a chunk to the document."""
        self._chunks.append(chunk)

    def set_chunks(self, chunks: list[Chunk]) -> None:
        """Set or replace all chunks."""
        self._chunks = list(chunks)

    def clear_chunks(self) -> None:
        """Clear all chunks from the document."""
        self._chunks.clear()

    def create_chunks(self, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Chunk]:
        """Create and store chunks for this document."""
        from scholaros.knowledge.loader import KnowledgeLoader

        chunks = KnowledgeLoader.chunk_text(
            document_id=self._identifier,
            text=self._content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.set_chunks(chunks)
        return self._chunks

    def to_dict(self) -> dict[str, Any]:
        """Serialize document to dictionary."""
        return {
            "id": self._identifier,
            "identifier": self._identifier,
            "title": self._title,
            "content": self._content,
            "metadata": self._metadata.to_dict(),
            "source": self._source.to_dict() if self._source else None,
            "chunks": [c.to_dict() for c in self._chunks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeDocument:
        """Deserialize document from dictionary."""
        from scholaros.knowledge.chunk import Chunk
        from scholaros.knowledge.source import KnowledgeSource

        doc_id = data.get("identifier") or data.get("id") or "doc"
        title = data.get("title", doc_id)
        content = data.get("content", "")
        meta = KnowledgeMetadata.from_dict(data["metadata"]) if "metadata" in data else None
        source = KnowledgeSource.from_dict(data["source"]) if data.get("source") else None
        chunks = [Chunk.from_dict(c) for c in data.get("chunks", [])]

        return cls(
            identifier=doc_id,
            title=title,
            content=content,
            metadata=meta,
            source=source,
            chunks=chunks,
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the document.
        """
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"title={self.title!r}"
            f")"
        )


# Canonical alias
Document = KnowledgeDocument

__all__ = [
    "Document",
    "KnowledgeDocument",
]
