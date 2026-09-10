"""
ScholarOS Built-in Indexing Service.

Provides vector indexing, inverted index search, and document chunking.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class IndexingService(Service):
    """Built-in Indexing Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="IndexingService",
                version="1.0.0",
                description="ScholarOS Built-in Indexing Service",
                capabilities=("vector_indexing", "lexical_indexing", "chunking"),
                tags=("indexing", "search"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "IndexingService",
]
