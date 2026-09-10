"""
ScholarOS Built-in Scheduler Service.

Provides task scheduling, background job execution, and cron management.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class SchedulerService(Service):
    """Built-in Scheduler Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="SchedulerService",
                version="1.0.0",
                description="ScholarOS Built-in Scheduler Service",
                capabilities=("job_scheduling", "cron", "timers"),
                tags=("scheduler", "system"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "SchedulerService",
]
