"""
ScholarOS Service Health Monitoring.

Defines health report structures, health statuses, and metrics tracking
for individual services and overall system monitoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any


class HealthStatus(Enum):
    """
    Health check status of a service.
    """

    HEALTHY = auto()
    DEGRADED = auto()
    UNHEALTHY = auto()
    UNKNOWN = auto()

    def __repr__(self) -> str:
        return f"HealthStatus.{self.name}"


@dataclass(slots=True)
class ServiceHealth:
    """
    Structured health report for a service.
    """

    service_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    details: str = "Operating normally"
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Return True if service status is HEALTHY."""
        return self.status == HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        """Return True if service status is DEGRADED."""
        return self.status == HealthStatus.DEGRADED

    @property
    def is_unhealthy(self) -> bool:
        """Return True if service status is UNHEALTHY."""
        return self.status == HealthStatus.UNHEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert health report to dictionary."""
        return {
            "service_name": self.service_name,
            "status": self.status.name,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
            "metrics": dict(self.metrics),
            "errors": list(self.errors),
        }


__all__ = [
    "HealthStatus",
    "ServiceHealth",
]
