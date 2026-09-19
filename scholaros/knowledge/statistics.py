"""
ScholarOS Knowledge Statistics.

Calculates and reports utilization, counts, size metrics, and index health.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.knowledge.index import InvertedIndex


@dataclass(slots=True, frozen=True)
class KnowledgeStatistics:
    """
    Aggregate metrics and utilization data for the knowledge subsystem.
    """

    document_count: int
    chunk_count: int
    storage_size_bytes: int
    average_chunk_size_chars: float
    index_status: str

    @property
    def total_characters(self) -> int:
        """Alias for storage_size_bytes or total character count."""
        return self.storage_size_bytes

    @property
    def avg_chunk_size(self) -> float:
        """Alias for average_chunk_size_chars."""
        return self.average_chunk_size_chars

    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary representation."""
        return {
            "document_count": self.document_count,
            "chunk_count": self.chunk_count,
            "storage_size_bytes": self.storage_size_bytes,
            "average_chunk_size_chars": round(self.average_chunk_size_chars, 2),
            "index_status": self.index_status,
        }


def calculate_statistics(
    target: Any = None,
    index: InvertedIndex | None = None,
    storage: Any = None,
) -> KnowledgeStatistics:
    """
    Compute real-time knowledge subsystem metrics from storage or a collection.
    """
    from scholaros.knowledge.collection import KnowledgeCollection

    actual_target = target if target is not None else storage

    if isinstance(actual_target, KnowledgeCollection):
        doc_count = len(actual_target)
        chunk_count = 0
        total_bytes = 0
        total_chunk_chars = 0

        for doc in actual_target.values():
            total_bytes += len(doc.content.encode("utf-8"))
            chunks = doc.chunks
            chunk_count += len(chunks)
            for c in chunks:
                total_chunk_chars += len(c.content)

        avg_size = (total_chunk_chars / chunk_count) if chunk_count > 0 else 0.0
        return KnowledgeStatistics(
            document_count=doc_count,
            chunk_count=chunk_count,
            storage_size_bytes=total_bytes,
            average_chunk_size_chars=avg_size,
            index_status="ready",
        )

    doc_count = 0
    chunk_count = 0
    total_bytes = 0
    total_chunk_chars = 0

    if actual_target is not None and hasattr(actual_target, "list_collections"):
        for coll_name in actual_target.list_collections():
            docs = actual_target.list_documents(coll_name)
            doc_count += len(docs)
            for doc in docs:
                total_bytes += len(doc.content.encode("utf-8"))
                chunks = doc.chunks or actual_target.get_chunks_for_document(doc.identifier)
                chunk_count += len(chunks)
                for c in chunks:
                    total_chunk_chars += len(c.content)

    avg_size = (total_chunk_chars / chunk_count) if chunk_count > 0 else 0.0
    index_status = "ready" if (index and index.total_chunks > 0) else "empty"

    return KnowledgeStatistics(
        document_count=doc_count,
        chunk_count=chunk_count,
        storage_size_bytes=total_bytes,
        average_chunk_size_chars=avg_size,
        index_status=index_status,
    )


__all__ = [
    "KnowledgeStatistics",
    "calculate_statistics",
]
