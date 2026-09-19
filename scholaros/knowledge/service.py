"""
ScholarOS Knowledge Service.

Bridges the Knowledge subsystem with the ScholarOS Service Framework,
Dependency Injection Container, and Event Bus.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.knowledge.loader import KnowledgeLoader
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.registry import KnowledgeRegistry
from scholaros.knowledge.search import SearchEngine, SearchQuery, SearchResponse
from scholaros.knowledge.storage import KnowledgeStorage
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.container.container import Container
    from scholaros.knowledge.diagnostics import DiagnosticReport
    from scholaros.knowledge.document import KnowledgeDocument
    from scholaros.knowledge.statistics import KnowledgeStatistics


class KnowledgeService(Service):
    """
    Core Knowledge subsystem service for ScholarOS.
    """

    def __init__(
        self,
        manager: KnowledgeManager | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="KnowledgeService",
                version="1.0.0",
                description="ScholarOS Core Knowledge Service",
                capabilities=("storage", "search", "indexing", "diagnostics"),
                tags=("knowledge", "core"),
            )
        super().__init__(metadata=metadata)

        self.manager = manager or KnowledgeManager()
        self.loader = KnowledgeLoader(manager=self.manager)

    # ---------------------------------------------------------
    # Lifecycle Hooks
    # ---------------------------------------------------------

    def initialize(self) -> None:
        super().initialize()

    def start(self) -> None:
        super().start()

    def stop(self) -> None:
        super().stop()

    def shutdown(self) -> None:
        super().shutdown()

    def health(self) -> ServiceHealth:
        """Report overall health of the knowledge subsystem."""
        if not self.is_running():
            return ServiceHealth(
                service_name=self.name,
                status=HealthStatus.UNKNOWN,
                details=f"Service in state: {self.status.name}",
            )

        diag = self.manager.run_diagnostics()
        status = HealthStatus.HEALTHY if diag.is_healthy else HealthStatus.DEGRADED
        details = "Healthy" if diag.is_healthy else f"Diagnostics found {len(diag.issues)} issues"
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=details,
        )

    def is_healthy(self) -> bool:
        """Convenience check if service is running and healthy."""
        return self.health().status == HealthStatus.HEALTHY

    # ---------------------------------------------------------
    # Facade Query & Ingestion Methods
    # ---------------------------------------------------------

    def search(self, query: str | SearchQuery, **kwargs: Any) -> SearchResponse:
        """Search knowledge base."""
        return self.manager.search(query, **kwargs)

    def add_document(self, document: KnowledgeDocument, collection_name: str = "default") -> None:
        """Add and index a document."""
        self.manager.add_document(document, collection_name=collection_name)

    def statistics(self) -> KnowledgeStatistics:
        """Retrieve subsystem metrics."""
        return self.manager.statistics()

    def run_diagnostics(self) -> DiagnosticReport:
        """Execute integrity diagnostics."""
        return self.manager.run_diagnostics()

    # ---------------------------------------------------------
    # DI Container Integration
    # ---------------------------------------------------------

    def register_container(self, container: Container) -> None:
        """
        Register knowledge components into the DI container.
        """
        container.add_instance(KnowledgeService, self)
        container.add_instance(KnowledgeManager, self.manager)
        container.add_instance(KnowledgeRegistry, self.manager.registry)
        container.add_instance(KnowledgeStorage, self.manager.storage)
        container.add_instance(KnowledgeLoader, self.loader)
        container.add_instance(SearchEngine, self.manager.search_engine)

    def register_into_container(self, container: Container) -> None:
        """Alias for register_container."""
        self.register_container(container)

    @classmethod
    def configure_container(
        cls,
        container: Container,
        manager: KnowledgeManager | None = None,
    ) -> KnowledgeService:
        """
        Convenience factory to create KnowledgeService and wire it into Container.
        """
        service = cls(manager=manager)
        service.register_container(container)
        return service


__all__ = [
    "KnowledgeService",
]
