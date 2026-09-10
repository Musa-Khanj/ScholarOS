"""
ScholarOS Built-in AI Service.

Provides core AI capabilities and model interactions.
"""

from __future__ import annotations

from typing import Any

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class AIService(Service):
    """Built-in AI Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="AIService",
                version="1.0.0",
                description="ScholarOS Built-in AI Service",
                capabilities=("inference", "embeddings", "generation"),
                tags=("ai", "core"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "AIService",
]
