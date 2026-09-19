"""
ScholarOS Hybrid Retriever.

Combines lexical keyword retrieval and dense semantic vector retrieval using
Reciprocal Rank Fusion (RRF) or linear score blending with full provenance tracking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from scholaros.contracts.retrieval import HybridRetrieverContract
from scholaros.retrieval.keyword import KeywordRetriever
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever
from scholaros.retrieval.scoring import (
    blend_scores,
    deduplicate_results,
    reciprocal_rank_fusion,
)
from scholaros.retrieval.semantic import SemanticRetriever

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider
    from scholaros.embeddings.generator import EmbeddingGenerator
    from scholaros.embeddings.provider import EmbeddingProvider
    from scholaros.embeddings.similarity_metric import SimilarityMetric
    from scholaros.embeddings.vector_store import VectorStore
    from scholaros.knowledge.storage import KnowledgeStorage


class HybridRetriever(BaseRetriever, HybridRetrieverContract):
    """
    Blends keyword and semantic retrieval results using configurable fusion strategies,
    supporting both VectorStore/EmbeddingGenerator and AIProvider/KnowledgeStorage backends.
    """

    def __init__(
        self,
        keyword_retriever: KeywordRetriever | None = None,
        semantic_retriever: SemanticRetriever | None = None,
        storage: KnowledgeStorage | None = None,
        ai_provider: AIProvider | None = None,
        vector_store: VectorStore | None = None,
        generator: EmbeddingGenerator | None = None,
        provider: EmbeddingProvider | None = None,
        metric: SimilarityMetric | None = None,
        fusion_mode: Literal["rrf", "linear"] = "rrf",
        rrf_k: int = 60,
        keyword_weight: float = 0.5,
        semantic_weight: float = 0.5,
        name: str = "HybridRetriever",
    ) -> None:
        super().__init__(name=name)
        self._keyword_retriever = keyword_retriever or KeywordRetriever(storage=storage)
        self._semantic_retriever = semantic_retriever or SemanticRetriever(
            ai_provider=ai_provider,
            storage=storage,
            vector_store=vector_store,
            generator=generator,
            provider=provider,
            metric=metric,
        )
        self._fusion_mode: Literal["rrf", "linear"] = fusion_mode
        self._rrf_k = rrf_k
        self._keyword_weight = keyword_weight
        self._semantic_weight = semantic_weight

    @property
    def keyword_retriever(self) -> KeywordRetriever:
        """Return the lexical keyword retriever."""
        return self._keyword_retriever

    @property
    def semantic_retriever(self) -> SemanticRetriever:
        """Return the dense semantic retriever."""
        return self._semantic_retriever

    @property
    def fusion_mode(self) -> Literal["rrf", "linear"]:
        """Return the fusion strategy ('rrf' or 'linear')."""
        return self._fusion_mode

    @property
    def rrf_k(self) -> int:
        """Return the RRF smoothing constant k."""
        return self._rrf_k

    @property
    def keyword_weight(self) -> float:
        """Return the relative weight for keyword retrieval."""
        return self._keyword_weight

    @property
    def semantic_weight(self) -> float:
        """Return the relative weight for semantic retrieval."""
        return self._semantic_weight

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Execute hybrid search combining keyword and semantic streams.
        """
        # Fetch broader candidate pools for fusion
        fetch_limit = max(query.limit * 2, 20)
        sub_query = query.with_limit(fetch_limit)

        kw_results = self._keyword_retriever.retrieve(sub_query)
        sem_results = self._semantic_retriever.retrieve(sub_query)

        if not kw_results and not sem_results:
            return []
        if not kw_results:
            single_fused = deduplicate_results(sem_results)
            if query.min_score > 0.0:
                single_fused = [r for r in single_fused if r.score >= query.min_score]
            return single_fused[: query.limit]
        if not sem_results:
            single_fused = deduplicate_results(kw_results)
            if query.min_score > 0.0:
                single_fused = [r for r in single_fused if r.score >= query.min_score]
            return single_fused[: query.limit]

        if self._fusion_mode == "rrf":
            fused = reciprocal_rank_fusion(
                [kw_results, sem_results],
                k=self._rrf_k,
                weights=[self._keyword_weight, self._semantic_weight],
                stream_names=["keyword", "semantic"],
            )
        else:
            fused = blend_scores(
                kw_results,
                sem_results,
                weight_a=self._keyword_weight,
                weight_b=self._semantic_weight,
                name_a="keyword",
                name_b="semantic",
            )

        fused = deduplicate_results(fused)
        if query.min_score > 0.0:
            fused = [r for r in fused if r.score >= query.min_score]

        return fused[: query.limit]


__all__ = [
    "HybridRetriever",
]
