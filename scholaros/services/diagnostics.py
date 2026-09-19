"""
ScholarOS Service Diagnostics.

Tracks telemetry, runtime statistics, uptime, failures, and execution timings
for ScholarOS services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class ServiceDiagnostics:
    """
    Diagnostics and performance tracking record for a service.
    """

    service_name: str
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    startup_duration_ms: float = 0.0
    shutdown_duration_ms: float = 0.0
    restart_count: int = 0
    failure_count: int = 0
    last_error: str | None = None
    last_error_time: datetime | None = None
    custom_metrics: dict[str, Any] = field(default_factory=dict)

    def record_start(self, duration_ms: float = 0.0) -> None:
        """Record successful service start."""
        self.started_at = datetime.now(timezone.utc)
        self.stopped_at = None
        self.startup_duration_ms = duration_ms

    def record_stop(self, duration_ms: float = 0.0) -> None:
        """Record service stop."""
        self.stopped_at = datetime.now(timezone.utc)
        self.shutdown_duration_ms = duration_ms

    def record_restart(self) -> None:
        """Increment restart counter."""
        self.restart_count += 1

    def record_failure(self, error: Exception | str) -> None:
        """Record service failure."""
        self.failure_count += 1
        self.last_error = str(error)
        self.last_error_time = datetime.now(timezone.utc)

    @property
    def uptime_seconds(self) -> float:
        """Return total seconds the service has been running continuously."""
        if self.started_at is None:
            return 0.0
        end_time = self.stopped_at or datetime.now(timezone.utc)
        delta = end_time - self.started_at
        return max(0.0, delta.total_seconds())

    def to_dict(self) -> dict[str, Any]:
        """Return diagnostics dictionary."""
        return {
            "service_name": self.service_name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "uptime_seconds": self.uptime_seconds,
            "startup_duration_ms": self.startup_duration_ms,
            "shutdown_duration_ms": self.shutdown_duration_ms,
            "restart_count": self.restart_count,
            "failure_count": self.failure_count,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "custom_metrics": dict(self.custom_metrics),
        }


__all__ = [
    "ServiceDiagnostics",
]
