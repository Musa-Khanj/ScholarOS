"""
ScholarOS Knowledge Lifecycle and Query Events.

Defines events emitted by the knowledge subsystem into the EventBus.
"""

from __future__ import annotations

from typing import Any

from scholaros.events.event import Event


class KnowledgeEvent(Event):
    """Base event for knowledge subsystem occurrences."""

    def __init__(
        self,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name or self.__class__.__name__,
            payload=payload if payload is not None else {},
            metadata=metadata if metadata is not None else {},
            **kwargs,
        )


class DocumentAdded(KnowledgeEvent):
    """Emitted when a document is added to a collection."""

    def __init__(self, document_id: str, collection_name: str, **kwargs: Any) -> None:
        super().__init__(payload={"document_id": document_id, "collection_name": collection_name}, **kwargs)


class DocumentRemoved(KnowledgeEvent):
    """Emitted when a document is removed from a collection."""

    def __init__(self, document_id: str, collection_name: str, **kwargs: Any) -> None:
        super().__init__(payload={"document_id": document_id, "collection_name": collection_name}, **kwargs)


class DocumentUpdated(KnowledgeEvent):
    """Emitted when a document is modified or re-indexed."""

    def __init__(self, document_id: str, collection_name: str, **kwargs: Any) -> None:
        super().__init__(payload={"document_id": document_id, "collection_name": collection_name}, **kwargs)


class CollectionCreated(KnowledgeEvent):
    """Emitted when a new collection is created."""

    def __init__(self, collection_name: str, **kwargs: Any) -> None:
        super().__init__(payload={"collection_name": collection_name}, **kwargs)


class CollectionDeleted(KnowledgeEvent):
    """Emitted when a collection is deleted."""

    def __init__(self, collection_name: str, **kwargs: Any) -> None:
        super().__init__(payload={"collection_name": collection_name}, **kwargs)


class CollectionIndexed(KnowledgeEvent):
    """Emitted when index building finishes for a collection."""

    def __init__(self, collection_name: str, chunk_count: int, **kwargs: Any) -> None:
        super().__init__(payload={"collection_name": collection_name, "chunk_count": chunk_count}, **kwargs)


class SearchCompleted(KnowledgeEvent):
    """Emitted when a search query finishes execution."""

    def __init__(self, query: str, total_results: int, latency_ms: float, **kwargs: Any) -> None:
        super().__init__(
            payload={"query": query, "total_results": total_results, "latency_ms": latency_ms},
            **kwargs,
        )


class DocumentIngested(KnowledgeEvent):
    """Emitted when a document has been successfully ingested."""

    def __init__(
        self,
        document_id: str,
        collection_name: str,
        chunks_count: int = 0,
        embedded: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "document_id": document_id,
                "collection_name": collection_name,
                "chunks_count": chunks_count,
                "embedded": embedded,
            },
            **kwargs,
        )


class IngestionFailed(KnowledgeEvent):
    """Emitted when document ingestion fails."""

    def __init__(
        self,
        file_path: str,
        error: str,
        collection_name: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "file_path": file_path,
                "error": error,
                "collection_name": collection_name,
            },
            **kwargs,
        )


__all__ = [
    "CollectionCreated",
    "CollectionDeleted",
    "CollectionIndexed",
    "DocumentAdded",
    "DocumentIngested",
    "DocumentRemoved",
    "DocumentUpdated",
    "IngestionFailed",
    "KnowledgeEvent",
    "SearchCompleted",
]

