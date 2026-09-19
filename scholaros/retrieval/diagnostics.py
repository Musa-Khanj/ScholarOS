"""
ScholarOS Retrieval Diagnostics.

Performs system health checks, strategy inspections, and operational audits
for the retrieval subsystem.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.services.health import HealthStatus, ServiceHealth

if TYPE_CHECKING:
    from scholaros.retrieval.manager import RetrievalManager


class RetrievalDiagnostics:
    """
    Performs diagnostic audits on the retrieval subsystem components and dependencies.
    """

    def __init__(self, manager: RetrievalManager) -> None:
        self.manager = manager

    def check_health(self) -> ServiceHealth:
        """
        Execute comprehensive health inspection across strategies, storage, and AI providers.
        """
        issues: list[str] = []

        # Strategy check
        strategies = self.manager.strategies.list_strategies()
        if not strategies:
            issues.append("No retrieval strategies registered.")

        # Storage check
        storage = self.manager.storage
        if storage is not None:
            try:
                storage.list_collections()
            except Exception as e:
                issues.append(f"KnowledgeStorage check failed: {e}")

        # AI Provider check
        ai_provider = self.manager.ai_provider
        if ai_provider is not None:
            try:
                p_health = ai_provider.health()
                if p_health.status == HealthStatus.UNHEALTHY:
                    issues.append(f"AIProvider '{ai_provider.name}' is unhealthy.")
            except Exception as e:
                issues.append(f"AIProvider check failed: {e}")

        if issues:
            status = (
                HealthStatus.UNHEALTHY
                if not strategies
                else HealthStatus.DEGRADED
            )
            details = "; ".join(issues)
        else:
            status = HealthStatus.HEALTHY
            details = "Retrieval subsystem operational."

        metrics_dict: dict[str, Any] = {
            "strategies_count": len(strategies),
            "query_count": self.manager.metrics.query_count,
            "success_count": self.manager.metrics.success_count,
            "avg_latency_ms": self.manager.metrics.avg_latency_ms,
        }

        return ServiceHealth(
            service_name="RetrievalSubsystem",
            status=status,
            details=details,
            metrics=metrics_dict,
            errors=issues,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert diagnostic status to dictionary."""
        return self.check_health().to_dict()


__all__ = [
    "RetrievalDiagnostics",
]
