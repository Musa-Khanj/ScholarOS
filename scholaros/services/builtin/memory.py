"""
ScholarOS Built-in Memory Service.

Provides short-term and long-term agent memory persistence.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class MemoryService(Service):
    """Built-in Memory Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="MemoryService",
                version="1.0.0",
                description="ScholarOS Built-in Memory Service",
                capabilities=("conversation_memory", "semantic_memory", "working_memory"),
                tags=("memory", "agent"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "MemoryService",
]
