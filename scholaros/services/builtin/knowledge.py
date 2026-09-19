"""
ScholarOS Built-in Knowledge Service.

Provides knowledge base management, entity extraction, and graph linking.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class KnowledgeService(Service):
    """Built-in Knowledge Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="KnowledgeService",
                version="1.0.0",
                description="ScholarOS Built-in Knowledge Service",
                capabilities=("knowledge_graph", "entity_linking", "taxonomies"),
                tags=("knowledge", "core"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "KnowledgeService",
]
