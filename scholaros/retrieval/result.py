"""
ScholarOS Retrieval Result.

Represents the result of a retrieval operation with scores, metadata,
and source references.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.embeddings.embedding import Embedding
    from scholaros.knowledge.chunk import Chunk
    from scholaros.knowledge.document import KnowledgeDocument


class RetrievalResult:
    """
    Represents the result of a retrieval operation.
    """

    def __init__(
        self,
        source: str,
        content: str,
        score: float,
        metadata: dict[str, Any] | None = None,
        chunk_id: str | None = None,
        document_id: str | None = None,
        collection: str | None = None,
        raw_score: float | None = None,
        rerank_score: float | None = None,
    ) -> None:
        """
        Initialize the retrieval result.
        """
        self._source = source
        self._content = content
        self._score = score
        self._metadata = dict(metadata) if metadata is not None else {}
        self._chunk_id = chunk_id
        self._document_id = document_id
        self._collection = collection
        self._raw_score = raw_score if raw_score is not None else score
        self._rerank_score = rerank_score

    @property
    def source(self) -> str:
        """Return the retrieval source."""
        return self._source

    @property
    def content(self) -> str:
        """Return the retrieved content."""
        return self._content

    @property
    def score(self) -> float:
        """Return the current retrieval score."""
        return self._score

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the retrieval metadata."""
        return self._metadata

    @property
    def chunk_id(self) -> str | None:
        """Return the identifier of the chunk, if applicable."""
        return self._chunk_id

    @property
    def document_id(self) -> str | None:
        """Return the identifier of the parent document, if applicable."""
        return self._document_id

    @property
    def collection(self) -> str | None:
        """Return the collection name, if applicable."""
        return self._collection

    @property
    def raw_score(self) -> float:
        """Return the initial raw retrieval score before reranking."""
        return self._raw_score

    @property
    def rerank_score(self) -> float | None:
        """Return the rerank score if reranking has occurred."""
        return self._rerank_score

    def with_score(self, new_score: float) -> RetrievalResult:
        """Return a copy of this result with an updated score."""
        return RetrievalResult(
            source=self._source,
            content=self._content,
            score=new_score,
            metadata=dict(self._metadata),
            chunk_id=self._chunk_id,
            document_id=self._document_id,
            collection=self._collection,
            raw_score=self._raw_score,
            rerank_score=self._rerank_score,
        )

    def with_rerank_score(self, rerank_score: float) -> RetrievalResult:
        """Return a copy of this result with an updated rerank score and active score."""
        return RetrievalResult(
            source=self._source,
            content=self._content,
            score=rerank_score,
            metadata=dict(self._metadata),
            chunk_id=self._chunk_id,
            document_id=self._document_id,
            collection=self._collection,
            raw_score=self._raw_score,
            rerank_score=rerank_score,
        )

    def with_metadata(self, updates: dict[str, Any]) -> RetrievalResult:
        """Return a copy of this result with merged metadata."""
        merged = dict(self._metadata)
        merged.update(updates)
        return RetrievalResult(
            source=self._source,
            content=self._content,
            score=self._score,
            metadata=merged,
            chunk_id=self._chunk_id,
            document_id=self._document_id,
            collection=self._collection,
            raw_score=self._raw_score,
            rerank_score=self._rerank_score,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Return the retrieval result as a dictionary.
        Preserves compatibility with existing tests.
        """
        data: dict[str, Any] = {
            "source": self.source,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }
        if self._chunk_id is not None:
            data["chunk_id"] = self._chunk_id
        if self._document_id is not None:
            data["document_id"] = self._document_id
        if self._collection is not None:
            data["collection"] = self._collection
        if self._raw_score is not None and self._raw_score != self._score:
            data["raw_score"] = self._raw_score
        if self._rerank_score is not None:
            data["rerank_score"] = self._rerank_score
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalResult:
        """Construct a RetrievalResult from a dictionary."""
        return cls(
            source=data["source"],
            content=data["content"],
            score=float(data.get("score", 0.0)),
            metadata=data.get("metadata", {}),
            chunk_id=data.get("chunk_id"),
            document_id=data.get("document_id"),
            collection=data.get("collection"),
            raw_score=data.get("raw_score"),
            rerank_score=data.get("rerank_score"),
        )

    @classmethod
    def from_chunk(
        cls,
        chunk: Chunk,
        score: float = 1.0,
        collection: str | None = None,
    ) -> RetrievalResult:
        """Construct a RetrievalResult directly from a Knowledge Chunk."""
        meta = dict(chunk.metadata)
        return cls(
            source=f"chunk:{chunk.identifier}",
            content=chunk.content,
            score=score,
            metadata=meta,
            chunk_id=chunk.identifier,
            document_id=chunk.document_id,
            collection=collection,
            raw_score=score,
        )

    @classmethod
    def from_document(
        cls,
        doc: KnowledgeDocument,
        score: float = 1.0,
        collection: str | None = None,
    ) -> RetrievalResult:
        """Construct a RetrievalResult directly from a Knowledge Document."""
        if hasattr(doc.metadata, "to_dict"):
            meta = doc.metadata.to_dict()
        elif isinstance(doc.metadata, dict):
            meta = dict(doc.metadata)
        else:
            meta = {}
        return cls(
            source=f"doc:{doc.identifier}",
            content=doc.content,
            score=score,
            metadata=meta,
            document_id=doc.identifier,
            collection=collection,
            raw_score=score,
        )

    @classmethod
    def from_embedding(
        cls,
        embedding: Embedding,
        score: float = 1.0,
        collection: str | None = None,
    ) -> RetrievalResult:
        """Construct a RetrievalResult directly from an Embedding object."""
        meta = dict(embedding.metadata)
        source = str(meta.get("source", f"embedding:{hash(embedding.text)}"))
        chunk_id = str(meta.get("chunk_id")) if "chunk_id" in meta else None
        document_id = str(meta.get("document_id")) if "document_id" in meta else None
        col = collection or (str(meta.get("collection")) if "collection" in meta else None)
        return cls(
            source=source,
            content=embedding.text,
            score=score,
            metadata=meta,
            chunk_id=chunk_id,
            document_id=document_id,
            collection=col,
            raw_score=score,
        )

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the retrieval result."""
        return (
            f"{self.__class__.__name__}("
            f"source={self.source!r}, "
            f"score={self.score}"
            f")"
        )


__all__ = [
    "RetrievalResult",
]
