"""
ScholarOS Retrieval Pipeline.

Coordinates the multi-stage retrieval pipeline:
Query -> Retrieve Candidates -> Filter -> Rank -> Rerank -> Context Construction.
Maintains full backward compatibility with legacy 3-stage pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scholaros.retrieval.context import ContextBuilder, RetrievalContext
from scholaros.retrieval.filters import RetrievalFilter
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.reranker import BaseReranker, RetrievalRanker, ScoreReranker
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever, Retriever

if TYPE_CHECKING:
    pass


class RetrievalPipeline:
    """
    Coordinates candidate retrieval, filtering, ranking, reranking,
    and context construction.
    """

    def __init__(
        self,
        retriever: BaseRetriever | Retriever,
        retrieval_filter: RetrievalFilter | None = None,
        ranker: BaseReranker | RetrievalRanker | ScoreReranker | None = None,
        reranker: BaseReranker | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self._retriever = retriever
        self._filter = retrieval_filter or RetrievalFilter()
        self._ranker = ranker or RetrievalRanker()
        self._reranker = reranker
        self._context_builder = context_builder or ContextBuilder()

    @property
    def retriever(self) -> BaseRetriever | Retriever:
        """Return the candidate retriever."""
        return self._retriever

    @property
    def filter(self) -> RetrievalFilter:
        """Return the retrieval filter."""
        return self._filter

    @property
    def ranker(self) -> BaseReranker | RetrievalRanker | ScoreReranker:
        """Return the retrieval ranker."""
        return self._ranker

    @property
    def reranker(self) -> BaseReranker | None:
        """Return the secondary reranker, if configured."""
        return self._reranker

    @property
    def context_builder(self) -> ContextBuilder:
        """Return the context builder."""
        return self._context_builder

    def run(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> list[RetrievalResult]:
        """
        Execute the retrieval pipeline (legacy 3-stage interface).
        """
        results = self._retriever.search(query)
        results = self._filter.filter(results, minimum_score=minimum_score)
        return self._ranker.rank(results)

    def execute(
        self,
        query: RetrievalQuery | str,
        build_context: bool = False,
    ) -> tuple[list[RetrievalResult], RetrievalContext | None]:
        """
        Execute the full multi-stage retrieval pipeline:
        Retrieve -> Filter -> Rank -> Optional Rerank -> Optional Context.
        """
        q = query if isinstance(query, RetrievalQuery) else RetrievalQuery(text=query)

        # 1. Retrieve candidates
        candidates = self._retriever.retrieve(q)

        # 2. Apply multi-predicate filtering
        filtered = self._filter.filter_by_query(candidates, q)

        # 3. Initial Score Ranking
        ranked = self._ranker.rank(filtered)

        # 4. Optional secondary reranking (Cross-encoder or LLM)
        if self._reranker is not None:
            ranked = self._reranker.rerank(q.text, ranked, top_n=q.limit)
        else:
            ranked = ranked[: q.limit]

        # 5. Optional context construction
        context: RetrievalContext | None = None
        if build_context:
            context = self._context_builder.build(q.text, ranked)

        return ranked, context

    def execute_context(self, query: RetrievalQuery | str) -> RetrievalContext:
        """Execute pipeline and return the final packed RetrievalContext."""
        _, ctx = self.execute(query, build_context=True)
        assert ctx is not None
        return ctx

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the retrieval pipeline."""
        if hasattr(self.retriever, "manager") and hasattr(self.retriever.manager, "registry"):
            return (
                f"{self.__class__.__name__}("
                f"collections="
                f"{len(self.retriever.manager.registry)}"
                f")"
            )
        return (
            f"{self.__class__.__name__}("
            f"retriever={self._retriever.name!r}"
            f")"
        )


__all__ = [
    "RetrievalPipeline",
]
