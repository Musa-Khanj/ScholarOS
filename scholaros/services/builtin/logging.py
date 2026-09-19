"""
ScholarOS Built-in Logging Service.

Provides centralized log ingestion, filtering, and structured logging.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class LoggingService(Service):
    """Built-in Logging Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="LoggingService",
                version="1.0.0",
                description="ScholarOS Built-in Logging Service",
                capabilities=("structured_logging", "trace_collection"),
                tags=("logging", "system"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "LoggingService",
]
