"""
ScholarOS Built-in Tool Service.

Provides tool registration, validation, and execution.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class ToolService(Service):
    """Built-in Tool Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="ToolService",
                version="1.0.0",
                description="ScholarOS Built-in Tool Service",
                capabilities=("tool_registry", "tool_execution"),
                tags=("tool", "core"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "ToolService",
]
