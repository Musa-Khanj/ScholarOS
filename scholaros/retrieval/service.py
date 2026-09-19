"""
ScholarOS Retrieval Service.

Bridges the retrieval subsystem with the ScholarOS Service Framework and
Dependency Injection Container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scholaros.retrieval.configuration import RetrievalConfiguration
from scholaros.retrieval.context import RetrievalContext
from scholaros.retrieval.diagnostics import RetrievalDiagnostics
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.metrics import RetrievalMetrics
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.registry import RetrievalRegistry
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.strategies import StrategyRegistry
from scholaros.services.health import ServiceHealth
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider
    from scholaros.container.container import Container
    from scholaros.embeddings.generator import EmbeddingGenerator
    from scholaros.embeddings.provider import EmbeddingProvider
    from scholaros.embeddings.vector_store import VectorStore
    from scholaros.events.bus import EventBus
    from scholaros.knowledge.storage import KnowledgeStorage


class RetrievalService(Service):
    """
    Service encapsulating ScholarOS query retrieval, search strategies,
    reranking, and prompt context building.
    """

    def __init__(
        self,
        manager: RetrievalManager | None = None,
        storage: KnowledgeStorage | None = None,
        ai_provider: AIProvider | None = None,
        event_bus: EventBus | None = None,
        config: RetrievalConfiguration | None = None,
        vector_store: VectorStore | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="RetrievalService",
                version="1.0.0",
                description="ScholarOS Information Retrieval & Reranking Subsystem",
                capabilities=("keyword", "semantic", "hybrid", "rerank", "context_packing"),
                tags=("retrieval", "search", "rag"),
            )
        super().__init__(metadata=metadata)

        self._manager = manager or RetrievalManager(
            storage=storage,
            ai_provider=ai_provider,
            event_bus=event_bus,
            config=config,
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            embedding_provider=embedding_provider,
        )

    @property
    def manager(self) -> RetrievalManager:
        """Return the core retrieval manager."""
        return self._manager

    @property
    def metrics(self) -> RetrievalMetrics:
        """Return operational metrics."""
        return self._manager.metrics

    @property
    def diagnostics(self) -> RetrievalDiagnostics:
        """Return diagnostics manager."""
        return self._manager.diagnostics

    # ---------------------------------------------------------
    # Core Operations
    # ---------------------------------------------------------

    def retrieve(self, query: RetrievalQuery | str) -> list[RetrievalResult]:
        """Execute query retrieval."""
        return self._manager.retrieve(query)

    def search(self, query: str, limit: int = 10) -> list[RetrievalResult]:
        """Convenience search helper."""
        q = RetrievalQuery(text=query, limit=limit)
        return self.retrieve(q)

    def build_context(
        self,
        query: RetrievalQuery | str,
        results: list[RetrievalResult] | None = None,
        max_tokens: int | None = None,
    ) -> RetrievalContext:
        """Build structured prompt context."""
        return self._manager.build_context(query=query, results=results, max_tokens=max_tokens)

    def create_pipeline(self, strategy: str = "default") -> RetrievalPipeline:
        """Create a full pipeline targeting the specified strategy."""
        strat = self._manager.strategies.get(
            strategy if strategy != "default" else self._manager.config.default_strategy
        )
        if hasattr(strat, "retriever"):
            retriever = getattr(strat, "retriever")
        else:
            from scholaros.retrieval.retriever import Retriever
            retriever = Retriever(self._manager)

        return RetrievalPipeline(
            retriever=retriever,
            retrieval_filter=self._manager._filter,
            ranker=self._manager.reranker,
            context_builder=self._manager._context_builder,
        )

    # ---------------------------------------------------------
    # Service Lifecycle Hooks
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
        """Run diagnostics and return service health report."""
        return self._manager.health()

    # ---------------------------------------------------------
    # DI Container Integration
    # ---------------------------------------------------------

    def register_container(self, container: Container) -> None:
        """Register retrieval components into the DI container."""
        container.add_instance(RetrievalService, self)
        container.add_instance(RetrievalManager, self._manager)
        container.add_instance(RetrievalRegistry, self._manager.registry)
        container.add_instance(StrategyRegistry, self._manager.strategies)
        container.add_instance(RetrievalMetrics, self._manager.metrics)
        container.add_instance(RetrievalDiagnostics, self._manager.diagnostics)
        container.add_instance(RetrievalConfiguration, self._manager.config)
        if self._manager.hybrid_retriever is not None:
            from scholaros.retrieval.hybrid import HybridRetriever
            container.add_instance(HybridRetriever, self._manager.hybrid_retriever)
        if self._manager.vector_store is not None:
            from scholaros.embeddings.vector_store import VectorStore
            container.add_instance(VectorStore, self._manager.vector_store)
        if self._manager.embedding_generator is not None:
            from scholaros.embeddings.generator import EmbeddingGenerator
            container.add_instance(EmbeddingGenerator, self._manager.embedding_generator)

    @classmethod
    def configure_container(
        cls,
        container: Container,
        manager: RetrievalManager | None = None,
        storage: KnowledgeStorage | None = None,
        ai_provider: AIProvider | None = None,
        event_bus: EventBus | None = None,
        config: RetrievalConfiguration | None = None,
        vector_store: VectorStore | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> RetrievalService:
        """Convenience factory to create RetrievalService and register in Container."""
        service = cls(
            manager=manager,
            storage=storage,
            ai_provider=ai_provider,
            event_bus=event_bus,
            config=config,
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            embedding_provider=embedding_provider,
        )
        service.register_container(container)
        return service

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"status={self.status.name}"
            f")"
        )


__all__ = [
    "RetrievalService",
]
