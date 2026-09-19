"""
ScholarOS Observability - System Health Aggregator.

Aggregates operational health inspections across AI providers, retrieval,
knowledge storage, plugins, and core services into a unified health status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.services.health import HealthStatus, ServiceHealth

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager
    from scholaros.knowledge.storage import KnowledgeStorage
    from scholaros.plugins.manager import PluginManager
    from scholaros.retrieval.manager import RetrievalManager


class SystemHealthAggregator:
    """
    Unified aggregator checking health across all ScholarOS subsystems.
    """

    def __init__(
        self,
        retrieval_manager: RetrievalManager | None = None,
        ai_manager: AIManager | None = None,
        knowledge_storage: KnowledgeStorage | None = None,
        plugin_manager: PluginManager | None = None,
    ) -> None:
        self.retrieval_manager = retrieval_manager
        self.ai_manager = ai_manager
        self.knowledge_storage = knowledge_storage
        self.plugin_manager = plugin_manager

    def check_health(self) -> ServiceHealth:
        """
        Execute comprehensive multi-subsystem health check.
        """
        subsystems: dict[str, Any] = {}
        all_errors: list[str] = []
        is_critical_unhealthy = False
        is_degraded = False

        # 1. Retrieval subsystem
        if self.retrieval_manager is not None:
            try:
                from scholaros.retrieval.diagnostics import RetrievalDiagnostics

                r_diag = RetrievalDiagnostics(self.retrieval_manager)
                r_health = r_diag.check_health()
                subsystems["retrieval"] = r_health.to_dict()
                if r_health.status == HealthStatus.UNHEALTHY:
                    is_critical_unhealthy = True
                    all_errors.extend(r_health.errors)
                elif r_health.status == HealthStatus.DEGRADED:
                    is_degraded = True
                    all_errors.extend(r_health.errors)
            except Exception as e:
                is_degraded = True
                msg = f"Retrieval health check failed: {e}"
                all_errors.append(msg)
                subsystems["retrieval"] = {"status": "ERROR", "error": msg}

        # 2. AI Providers
        if self.ai_manager is not None:
            try:
                active_provider_name = getattr(self.ai_manager, "default_provider", None) or "default"
                ai_health = HealthStatus.HEALTHY
                if hasattr(self.ai_manager, "health"):
                    h_val = getattr(self.ai_manager, "health")()
                    ai_health = h_val if isinstance(h_val, HealthStatus) else getattr(h_val, "status", HealthStatus.HEALTHY)
                elif hasattr(self.ai_manager, "select_provider"):
                    try:
                        p = self.ai_manager.select_provider()
                        active_provider_name = p.name
                        p_health = p.health()
                        ai_health = p_health.status
                    except Exception:
                        ai_health = HealthStatus.DEGRADED

                subsystems["ai"] = {
                    "active_provider": active_provider_name,
                    "status": ai_health.name,
                }
                if ai_health == HealthStatus.UNHEALTHY:
                    is_critical_unhealthy = True
                    all_errors.append("Active AI Provider is UNHEALTHY.")
                elif ai_health == HealthStatus.DEGRADED:
                    is_degraded = True
                    all_errors.append("Active AI Provider is DEGRADED.")
            except Exception as e:
                is_degraded = True
                msg = f"AI subsystem health check failed: {e}"
                all_errors.append(msg)
                subsystems["ai"] = {"status": "ERROR", "error": msg}

        # 3. Knowledge Storage
        if self.knowledge_storage is not None:
            try:
                from scholaros.knowledge.diagnostics import KnowledgeDiagnostics

                k_diag = KnowledgeDiagnostics()
                k_report = k_diag.run_checks(self.knowledge_storage)
                subsystems["knowledge"] = k_report.to_dict()
                if not k_report.is_healthy:
                    is_degraded = True
                    for issue in k_report.issues:
                        all_errors.append(f"Knowledge issue ({issue.issue_type}): {issue.description}")
            except Exception as e:
                is_degraded = True
                msg = f"Knowledge health check failed: {e}"
                all_errors.append(msg)
                subsystems["knowledge"] = {"status": "ERROR", "error": msg}

        # 4. Plugins
        if self.plugin_manager is not None:
            try:
                loaded = len(self.plugin_manager.plugins)
                subsystems["plugins"] = {
                    "loaded_count": loaded,
                    "status": "HEALTHY",
                }
            except Exception as e:
                subsystems["plugins"] = {"status": "ERROR", "error": str(e)}

        # Determine overall system status
        if is_critical_unhealthy:
            overall_status = HealthStatus.UNHEALTHY
            details = f"System unhealthy: {len(all_errors)} errors detected."
        elif is_degraded:
            overall_status = HealthStatus.DEGRADED
            details = f"System degraded: {len(all_errors)} issues detected."
        else:
            overall_status = HealthStatus.HEALTHY
            details = "All monitored subsystems operational."

        return ServiceHealth(
            service_name="ScholarOSSystem",
            status=overall_status,
            details=details,
            metrics={"subsystems": subsystems},
            errors=all_errors,
        )


__all__ = [
    "SystemHealthAggregator",
]
