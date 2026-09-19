"""
ScholarOS Retrieval Manager.

Central orchestrator for the retrieval subsystem. Manages registered collections,
pluggable retrieval strategies, scoring, telemetry metrics, and events.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from scholaros.retrieval.collection import RetrievalCollection
from scholaros.retrieval.configuration import RetrievalConfiguration
from scholaros.retrieval.context import ContextBuilder, RetrievalContext
from scholaros.retrieval.diagnostics import RetrievalDiagnostics
from scholaros.retrieval.events import (
    ContextBuilt,
    RetrievalCompleted,
    RetrievalFailed,
    RetrievalStarted,
)
from scholaros.retrieval.exceptions import RetrievalError
from scholaros.retrieval.filters import RetrievalFilter
from scholaros.retrieval.metrics import RetrievalMetrics
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.registry import RetrievalRegistry
from scholaros.retrieval.reranker import BaseReranker, ScoreReranker
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.strategies import (
    DelegateStrategy,
    HybridStrategy,
    KeywordStrategy,
    SemanticStrategy,
    StrategyRegistry,
)

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider
    from scholaros.embeddings.generator import EmbeddingGenerator
    from scholaros.embeddings.provider import EmbeddingProvider
    from scholaros.embeddings.vector_store import VectorStore
    from scholaros.events.bus import EventBus
    from scholaros.knowledge.storage import KnowledgeStorage
    from scholaros.retrieval.hybrid import HybridRetriever
    from scholaros.retrieval.pipeline import RetrievalPipeline
    from scholaros.services.health import ServiceHealth


class RetrievalManager:
    """
    Coordinates collections, strategies, rerankers, metrics, and events for ScholarOS.
    """

    def __init__(
        self,
        registry: RetrievalRegistry | None = None,
        storage: KnowledgeStorage | None = None,
        ai_provider: AIProvider | None = None,
        event_bus: EventBus | None = None,
        config: RetrievalConfiguration | None = None,
        strategies: StrategyRegistry | None = None,
        metrics: RetrievalMetrics | None = None,
        reranker: BaseReranker | None = None,
        vector_store: VectorStore | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self._registry = registry if registry is not None else RetrievalRegistry()
        self._storage = storage
        self._ai_provider = ai_provider
        self._event_bus = event_bus
        self._config = config or RetrievalConfiguration()
        self._strategies = strategies or StrategyRegistry()
        self._metrics = metrics or RetrievalMetrics()
        self._reranker = reranker or ScoreReranker()
        self._vector_store = vector_store
        self._embedding_generator = embedding_generator
        self._embedding_provider = embedding_provider
        self._filter = RetrievalFilter()
        self._context_builder = ContextBuilder(
            token_budget=self._config.context_token_budget
        )
        self._diagnostics = RetrievalDiagnostics(self)
        self._hybrid_retriever: HybridRetriever | None = None

        self._initialize_default_strategies()

    def _initialize_default_strategies(self) -> None:
        """Register built-in strategies according to available dependencies."""
        from scholaros.retrieval.hybrid import HybridRetriever
        from scholaros.retrieval.keyword import KeywordRetriever
        from scholaros.retrieval.retriever import Retriever
        from scholaros.retrieval.semantic import SemanticRetriever

        # 1. Legacy collection strategy
        if not self._strategies.contains("collection"):
            legacy_retriever = Retriever(self, name="collection")
            self._strategies.register("collection", DelegateStrategy(legacy_retriever, name="collection"))

        # 2. Keyword strategy
        if not self._strategies.contains("keyword"):
            kw_retriever = KeywordRetriever(storage=self._storage, name="keyword")
            self._strategies.register("keyword", KeywordStrategy(kw_retriever, name="keyword"))

        # 3. Semantic strategy
        if not self._strategies.contains("semantic"):
            sem_retriever = SemanticRetriever(
                ai_provider=self._ai_provider,
                storage=self._storage,
                generator=self._embedding_generator,
                vector_store=self._vector_store,
                provider=self._embedding_provider,
                name="semantic",
            )
            self._strategies.register("semantic", SemanticStrategy(sem_retriever, name="semantic"))

        # 4. Vector strategy (explicit vector store strategy)
        if self._vector_store is not None and not self._strategies.contains("vector"):
            vec_retriever = SemanticRetriever(
                generator=self._embedding_generator,
                vector_store=self._vector_store,
                provider=self._embedding_provider,
                name="vector",
            )
            self._strategies.register("vector", SemanticStrategy(vec_retriever, name="vector"))

        # 5. Hybrid strategy
        if not self._strategies.contains("hybrid"):
            hybrid_retriever = HybridRetriever(
                storage=self._storage,
                ai_provider=self._ai_provider,
                vector_store=self._vector_store,
                generator=self._embedding_generator,
                provider=self._embedding_provider,
                semantic_retriever=sem_retriever if "sem_retriever" in locals() else None,
                fusion_mode="rrf",
                rrf_k=self._config.rrf_k,
                keyword_weight=self._config.keyword_weight,
                semantic_weight=self._config.semantic_weight,
                name="hybrid",
            )
            self._hybrid_retriever = hybrid_retriever
            self._strategies.register("hybrid", HybridStrategy(hybrid_retriever, name="hybrid"))
        elif hasattr(self._strategies.get("hybrid"), "retriever"):
            strat_retriever = getattr(self._strategies.get("hybrid"), "retriever")
            if isinstance(strat_retriever, HybridRetriever):
                self._hybrid_retriever = strat_retriever
            else:
                self._hybrid_retriever = None
        else:
            self._hybrid_retriever = None

    @property
    def registry(self) -> RetrievalRegistry:
        """Return the retrieval collection registry."""
        return self._registry

    @property
    def vector_store(self) -> VectorStore | None:
        """Return the configured vector store."""
        return self._vector_store

    @property
    def embedding_generator(self) -> EmbeddingGenerator | None:
        """Return the configured embedding generator."""
        return self._embedding_generator

    @property
    def storage(self) -> KnowledgeStorage | None:
        """Return the knowledge storage backend."""
        return self._storage

    @property
    def ai_provider(self) -> AIProvider | None:
        """Return the AI provider."""
        return self._ai_provider

    @property
    def event_bus(self) -> EventBus | None:
        """Return the event bus."""
        return self._event_bus

    @property
    def config(self) -> RetrievalConfiguration:
        """Return current configuration."""
        return self._config

    @property
    def strategies(self) -> StrategyRegistry:
        """Return strategy registry."""
        return self._strategies

    @property
    def metrics(self) -> RetrievalMetrics:
        """Return operational metrics recorder."""
        return self._metrics

    @property
    def diagnostics(self) -> RetrievalDiagnostics:
        """Return diagnostics manager."""
        return self._diagnostics

    @property
    def reranker(self) -> BaseReranker:
        """Return primary reranker."""
        return self._reranker

    @property
    def hybrid_retriever(self) -> HybridRetriever | None:
        """Return the default hybrid retriever, if configured."""
        return getattr(self, "_hybrid_retriever", None)

    # ---------------------------------------------------------
    # Core Retrieval Workflow
    # ---------------------------------------------------------

    def retrieve(self, query: RetrievalQuery | str) -> list[RetrievalResult]:
        """
        Execute candidate retrieval, filtering, and reranking for a query.
        """
        q = query if isinstance(query, RetrievalQuery) else RetrievalQuery(text=query)
        strategy_name = q.strategy if q.strategy != "default" else self._config.default_strategy

        # Fallback to collection strategy if requesting default on an empty storage with collections
        if (
            strategy_name in ("default", "hybrid", "keyword")
            and self._storage is None
            and len(self._registry) > 0
        ):
            strategy_name = "collection"

        start_time = time.perf_counter()

        if self._event_bus is not None and self._config.enable_events:
            self._event_bus.publish(
                RetrievalStarted(query=q.text, strategy=strategy_name, limit=q.limit)
            )

        try:
            strategy = self._strategies.get(strategy_name)
            raw_candidates = strategy.execute(q)

            # Filtering
            filtered = self._filter.filter_by_query(raw_candidates, q)

            # Reranking
            reranked = self._reranker.rerank(q.text, filtered, top_n=q.limit)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if self._config.enable_metrics:
                self._metrics.record_query(
                    strategy=strategy_name,
                    results_count=len(reranked),
                    latency_ms=elapsed_ms,
                    success=True,
                )

            if self._event_bus is not None and self._config.enable_events:
                self._event_bus.publish(
                    RetrievalCompleted(
                        query=q.text,
                        strategy=strategy_name,
                        count=len(reranked),
                        latency_ms=elapsed_ms,
                    )
                )

            return reranked

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if self._config.enable_metrics:
                self._metrics.record_query(
                    strategy=strategy_name,
                    results_count=0,
                    latency_ms=elapsed_ms,
                    success=False,
                )
            if self._event_bus is not None and self._config.enable_events:
                self._event_bus.publish(
                    RetrievalFailed(
                        query=q.text,
                        strategy=strategy_name,
                        error=str(e),
                    )
                )
            if isinstance(e, RetrievalError):
                raise
            raise RetrievalError(f"Retrieval operation failed: {e}") from e

    def build_context(
        self,
        query: RetrievalQuery | str,
        results: list[RetrievalResult] | None = None,
        max_tokens: int | None = None,
    ) -> RetrievalContext:
        """
        Build an LLM-ready prompt context package from retrieval results.
        """
        query_text = query.text if isinstance(query, RetrievalQuery) else str(query)
        res_list = results if results is not None else self.retrieve(query)

        context = self._context_builder.build(
            query=query_text,
            results=res_list,
            max_tokens=max_tokens or self._config.context_token_budget,
        )

        if self._event_bus is not None and self._config.enable_events:
            self._event_bus.publish(
                ContextBuilt(
                    query=query_text,
                    item_count=len(context),
                    total_tokens=context.total_tokens,
                    token_budget=max_tokens or self._config.context_token_budget,
                )
            )

        return context

    def create_pipeline(self, strategy: str = "default") -> RetrievalPipeline:
        """Create a full pipeline targeting the specified strategy."""
        from scholaros.retrieval.pipeline import RetrievalPipeline

        strat = self._strategies.get(
            strategy if strategy != "default" else self._config.default_strategy
        )
        if hasattr(strat, "retriever"):
            retriever = getattr(strat, "retriever")
        else:
            from scholaros.retrieval.retriever import Retriever
            retriever = Retriever(self)

        return RetrievalPipeline(
            retriever=retriever,
            retrieval_filter=self._filter,
            ranker=self._reranker,
            context_builder=self._context_builder,
        )

    def health(self) -> ServiceHealth:
        """Run diagnostics health check."""
        return self._diagnostics.check_health()

    # ---------------------------------------------------------
    # Backward-Compatible Legacy Registry Methods
    # ---------------------------------------------------------

    def register(
        self,
        name: str,
        collection: RetrievalCollection,
    ) -> None:
        """Register a retrieval collection."""
        self._registry.add(name, collection)

    def unregister(
        self,
        name: str,
    ) -> None:
        """Unregister a retrieval collection."""
        self._registry.remove(name)

    def get(
        self,
        name: str,
    ) -> RetrievalCollection | None:
        """Return a registered retrieval collection."""
        return self._registry.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """Return whether a retrieval collection is registered."""
        return self._registry.contains(name)

    def installed(
        self,
    ) -> list[str]:
        """Return registered retrieval collection names."""
        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """Remove all registered retrieval collections."""
        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """Return a developer-friendly representation of the retrieval manager."""
        return f"{self.__class__.__name__}(collections={len(self._registry)})"


__all__ = [
    "RetrievalManager",
]
