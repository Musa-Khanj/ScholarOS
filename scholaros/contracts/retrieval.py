"""
ScholarOS Retrieval Contracts and Protocols.

Defines runtime-checkable protocols and formal interface contracts for retrieval,
reranking, filtering, pipelines, and prompt context building across ScholarOS.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from scholaros.retrieval.context import RetrievalContext
    from scholaros.retrieval.query import RetrievalQuery
    from scholaros.retrieval.result import RetrievalResult


@runtime_checkable
class RetrieverProtocol(Protocol):
    """
    Protocol for components that retrieve candidates based on queries.
    """

    @property
    def name(self) -> str:
        """Return the retriever name."""
        ...

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Retrieve candidate results for a strongly-typed query."""
        ...

    def search(self, query: str, limit: int = 10) -> list[RetrievalResult]:
        """Convenience search by raw text query."""
        ...


@runtime_checkable
class RerankerProtocol(Protocol):
    """
    Protocol for components that re-score and re-order candidate results.
    """

    @property
    def name(self) -> str:
        """Return the reranker name."""
        ...

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        """Re-score and re-order candidate results."""
        ...

    def rank(
        self,
        results: list[RetrievalResult],
        reverse: bool = True,
    ) -> list[RetrievalResult]:
        """Rank results strictly by score."""
        ...


@runtime_checkable
class FilterProtocol(Protocol):
    """
    Protocol for components that filter retrieval results against predicates.
    """

    def filter(
        self,
        results: list[RetrievalResult],
        minimum_score: float = 0.0,
        **kwargs: Any,
    ) -> list[RetrievalResult]:
        """Filter results based on minimum score and optional criteria."""
        ...

    def filter_by_query(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Filter results using parameters defined on a RetrievalQuery."""
        ...


@runtime_checkable
class PipelineProtocol(Protocol):
    """
    Protocol for multi-stage retrieval pipelines.
    """

    def run(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> list[RetrievalResult]:
        """Execute legacy pipeline execution."""
        ...

    def execute(
        self,
        query: RetrievalQuery | str,
        build_context: bool = False,
    ) -> tuple[list[RetrievalResult], RetrievalContext | None]:
        """Execute multi-stage pipeline execution."""
        ...


@runtime_checkable
class ContextBuilderProtocol(Protocol):
    """
    Protocol for prompt context builders packaging retrieval results.
    """

    def build(
        self,
        query: str,
        results: list[RetrievalResult],
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> RetrievalContext:
        """Construct structured RetrievalContext within token budgets."""
        ...


@runtime_checkable
class StrategyProtocol(Protocol):
    """
    Protocol for retrieval strategies managed by a StrategyRegistry.
    """

    @property
    def name(self) -> str:
        """Return the strategy identifier."""
        ...

    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute the strategy."""
        ...


@runtime_checkable
class VectorRetrieverContract(Protocol):
    """
    Contract for retrievers backed by vector embeddings and vector stores.
    """

    @property
    def name(self) -> str:
        """Return the vector retriever name."""
        ...

    def retrieve_vectors(
        self,
        query_vector: list[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[RetrievalResult]:
        """Retrieve candidates by raw embedding vector."""
        ...


@runtime_checkable
class HybridRetrieverContract(Protocol):
    """
    Contract for hybrid retrievers combining lexical and semantic retrieval streams.
    """

    @property
    def name(self) -> str:
        """Return the retriever name."""
        ...

    @property
    def keyword_retriever(self) -> Any:
        """Return the lexical keyword retriever."""
        ...

    @property
    def semantic_retriever(self) -> Any:
        """Return the dense semantic retriever."""
        ...

    @property
    def fusion_mode(self) -> str:
        """Return the fusion strategy ('rrf' or 'linear')."""
        ...

    @property
    def rrf_k(self) -> int:
        """Return the RRF smoothing constant k."""
        ...

    @property
    def keyword_weight(self) -> float:
        """Return the relative weight for keyword retrieval."""
        ...

    @property
    def semantic_weight(self) -> float:
        """Return the relative weight for semantic retrieval."""
        ...

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute hybrid search combining both streams."""
        ...


__all__ = [
    "RetrieverProtocol",
    "RerankerProtocol",
    "FilterProtocol",
    "PipelineProtocol",
    "ContextBuilderProtocol",
    "StrategyProtocol",
    "VectorRetrieverContract",
    "HybridRetrieverContract",
]
