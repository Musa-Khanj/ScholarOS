"""
ScholarOS Built-in Research Service.

Provides academic paper discovery, analysis, and research workflows.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class ResearchService(Service):
    """Built-in Research Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="ResearchService",
                version="1.0.0",
                description="ScholarOS Built-in Research Service",
                capabilities=("paper_search", "synthesis", "citation_graph"),
                tags=("research", "domain"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "ResearchService",
]
