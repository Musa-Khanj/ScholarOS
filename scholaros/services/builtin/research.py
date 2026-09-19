"""
ScholarOS Built-in Research Service.

Provides academic paper discovery, analysis, and research workflows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.agents.researcher import ResearchAgent
    from scholaros.container.container import Container
    from scholaros.knowledge.rag.service import RAGService
    from scholaros.research.manager import ResearchSessionManager
    from scholaros.research.pipeline import ResearchPipeline
    from scholaros.research.result import ResearchResult
    from scholaros.research.session import ResearchSession


class ResearchService(Service):
    """Built-in Research Service."""

    def __init__(
        self,
        pipeline: ResearchPipeline | None = None,
        rag_service: RAGService | None = None,
        session_manager: ResearchSessionManager | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="ResearchService",
                version="1.0.0",
                description="ScholarOS Built-in Research Service",
                capabilities=("paper_search", "synthesis", "citation_graph", "rag_research", "session_memory"),
                tags=("research", "domain"),
            )
        super().__init__(metadata=metadata)

        self._pipeline: ResearchPipeline | None
        if pipeline is not None:
            self._pipeline = pipeline
        elif rag_service is not None:
            from scholaros.research.pipeline import ResearchPipeline
            self._pipeline = ResearchPipeline.from_rag(rag_service)
        else:
            self._pipeline = None

        self._agent: ResearchAgent | None = None
        self._session_manager = session_manager

    @property
    def pipeline(self) -> ResearchPipeline | None:
        """Return the research pipeline if configured."""
        return self._pipeline

    @property
    def session_manager(self) -> ResearchSessionManager:
        """Return the attached or lazily created ResearchSessionManager."""
        if self._session_manager is None:
            from scholaros.research.manager import ResearchSessionManager
            self._session_manager = ResearchSessionManager(
                pipeline=self._pipeline,
            )
        elif self._session_manager.pipeline is None and self._pipeline is not None:
            self._session_manager.pipeline = self._pipeline
        return self._session_manager

    def create_session(self, title: str = "", query: str = "") -> ResearchSession:
        """Create and register a new research session."""
        return self.session_manager.create(query=query, title=title)

    @property
    def agent(self) -> ResearchAgent:
        """Return the lazily initialized ResearchAgent."""

        if self._agent is None:
            if self._pipeline is None:
                raise AttributeError("ResearchService has no configured ResearchPipeline.")
            from scholaros.agents.researcher import ResearchAgent
            self._agent = ResearchAgent(self._pipeline)
        return self._agent

    def research(self, query: str, **kwargs: Any) -> ResearchResult:
        """Execute a grounded research query."""
        if self._pipeline is None:
            raise AttributeError("ResearchService has no configured ResearchPipeline.")
        return self._pipeline.execute_rag(query, **kwargs)

    def run_workflow(self, query: str, **kwargs: Any) -> ResearchResult:
        """Execute a multi-stage research workflow."""
        if self._pipeline is None:
            raise AttributeError("ResearchService has no configured ResearchPipeline.")
        return self._pipeline.execute_workflow(query, **kwargs)

    def health(self) -> ServiceHealth:
        """Report health status of ResearchService."""
        has_pipeline = self._pipeline is not None
        status = HealthStatus.HEALTHY if has_pipeline else HealthStatus.UNKNOWN
        details = "Research service operational" if has_pipeline else "Research pipeline not configured"
        metrics: dict[str, Any] = {
            "has_pipeline": has_pipeline,
            "has_rag": self._pipeline.has_rag if self._pipeline else False,
        }
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=details,
            metrics=metrics,
        )

    def register_container(self, container: Container) -> None:
        """Register research components into DI container."""
        container.add_instance(ResearchService, self)
        from scholaros.research.manager import ResearchSessionManager
        container.add_instance(ResearchSessionManager, self.session_manager)
        if self._pipeline is not None:
            from scholaros.research.pipeline import ResearchPipeline
            container.add_instance(ResearchPipeline, self._pipeline)
            from scholaros.agents.researcher import ResearchAgent
            container.add_instance(ResearchAgent, self.agent)
            if self._pipeline.workflow_engine is not None:
                from scholaros.research.workflow_engine import ResearchWorkflowEngine
                container.add_instance(ResearchWorkflowEngine, self._pipeline.workflow_engine)
                from scholaros.planner.research_planner import ResearchPlanner
                container.add_instance(ResearchPlanner, self._pipeline.workflow_engine.planner)
                from scholaros.execution.workflow_executor import WorkflowExecutor
                container.add_instance(WorkflowExecutor, self._pipeline.workflow_engine.executor)

    @classmethod
    def configure_container(
        cls,
        container: Container,
        pipeline: ResearchPipeline | None = None,
        rag_service: RAGService | None = None,
        session_manager: ResearchSessionManager | None = None,
    ) -> ResearchService:
        """Convenience factory to wire ResearchService into the Container."""
        if rag_service is None and pipeline is None:
            # Check if RAGService is already in container
            from scholaros.knowledge.rag.service import RAGService
            try:
                rag_service = container.resolve(RAGService)
            except Exception:
                pass

        service = cls(pipeline=pipeline, rag_service=rag_service, session_manager=session_manager)
        try:
            from scholaros.memory.manager import MemoryManager
            service.session_manager._memory_manager = container.resolve(MemoryManager)
        except Exception:
            pass
        try:
            from scholaros.knowledge.manager import KnowledgeManager
            service.session_manager._knowledge_manager = container.resolve(KnowledgeManager)
        except Exception:
            pass

        service.register_container(container)
        return service



__all__ = [
    "ResearchService",
]
