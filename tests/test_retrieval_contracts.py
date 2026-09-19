"""
ScholarOS Retrieval Contracts and Protocols Validation Tests.

Validates that all retrieval components adhere to formal runtime-checkable
contracts and protocols without duplicating subsystem logic.
"""

from __future__ import annotations



from scholaros.contracts.retrieval import (
    ContextBuilderProtocol,
    FilterProtocol,
    PipelineProtocol,
    RerankerProtocol,
    RetrieverProtocol,
    StrategyProtocol,
    VectorRetrieverContract,
)
from scholaros.retrieval import (
    ContextBuilder,
    CrossEncoderReranker,
    HybridRetriever,
    HybridStrategy,
    KeywordRetriever,
    KeywordStrategy,
    LLMReranker,
    RetrievalFilter,
    RetrievalManager,
    RetrievalPipeline,
    RetrievalQuery,
    RetrievalRanker,
    RetrievalRegistry,
    RetrievalResult,
    Retriever,
    ScoreReranker,
    SemanticRetriever,
    SemanticStrategy,
)


# ---------------------------------------------------------------------------
# Test 1: Concrete Retriever Protocol Compliance
# ---------------------------------------------------------------------------

def test_retriever_protocol_compliance():
    manager = RetrievalManager(RetrievalRegistry())

    collection_retriever = Retriever(manager)
    keyword_retriever = KeywordRetriever()
    semantic_retriever = SemanticRetriever()
    hybrid_retriever = HybridRetriever()

    for ret in (collection_retriever, keyword_retriever, semantic_retriever, hybrid_retriever):
        assert isinstance(ret, RetrieverProtocol)
        assert hasattr(ret, "name")
        assert callable(getattr(ret, "retrieve"))
        assert callable(getattr(ret, "search"))


# ---------------------------------------------------------------------------
# Test 2: Concrete Reranker Protocol Compliance
# ---------------------------------------------------------------------------

def test_reranker_protocol_compliance():
    score_reranker = ScoreReranker()
    legacy_ranker = RetrievalRanker()
    cross_encoder = CrossEncoderReranker()
    llm_reranker = LLMReranker()

    for reranker in (score_reranker, legacy_ranker, cross_encoder, llm_reranker):
        assert isinstance(reranker, RerankerProtocol)
        assert hasattr(reranker, "name")
        assert callable(getattr(reranker, "rerank"))
        assert callable(getattr(reranker, "rank"))


# ---------------------------------------------------------------------------
# Test 3: Filter Protocol Compliance
# ---------------------------------------------------------------------------

def test_filter_protocol_compliance():
    retrieval_filter = RetrievalFilter()

    assert isinstance(retrieval_filter, FilterProtocol)
    assert callable(getattr(retrieval_filter, "filter"))
    assert callable(getattr(retrieval_filter, "filter_by_query"))


# ---------------------------------------------------------------------------
# Test 4: Pipeline Protocol Compliance
# ---------------------------------------------------------------------------

def test_pipeline_protocol_compliance():
    manager = RetrievalManager(RetrievalRegistry())
    retriever = Retriever(manager)
    pipeline = RetrievalPipeline(
        retriever=retriever,
        retrieval_filter=RetrievalFilter(),
        ranker=RetrievalRanker(),
    )

    assert isinstance(pipeline, PipelineProtocol)
    assert callable(getattr(pipeline, "run"))
    assert callable(getattr(pipeline, "execute"))


# ---------------------------------------------------------------------------
# Test 5: ContextBuilder Protocol Compliance
# ---------------------------------------------------------------------------

def test_context_builder_protocol_compliance():
    builder = ContextBuilder()

    assert isinstance(builder, ContextBuilderProtocol)
    assert callable(getattr(builder, "build"))


# ---------------------------------------------------------------------------
# Test 6: Strategy Protocol Compliance
# ---------------------------------------------------------------------------

def test_strategy_protocol_compliance():
    kw_strat = KeywordStrategy(KeywordRetriever())
    sem_strat = SemanticStrategy(SemanticRetriever())
    hyb_strat = HybridStrategy(HybridRetriever())

    for strat in (kw_strat, sem_strat, hyb_strat):
        assert isinstance(strat, StrategyProtocol)
        assert hasattr(strat, "name")
        assert callable(getattr(strat, "execute"))


# ---------------------------------------------------------------------------
# Test 7: Custom / Duck-Typed Implementations Satisfy Contracts
# ---------------------------------------------------------------------------

class CustomRetriever:
    """Mock retriever implementing the RetrieverProtocol via duck typing."""

    @property
    def name(self) -> str:
        return "custom-mock"

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        return [
            RetrievalResult(source="mock", content=f"Result for {query.text}", score=0.99)
        ]

    def search(self, query: str, limit: int = 10) -> list[RetrievalResult]:
        q = RetrievalQuery(text=query, limit=limit)
        return self.retrieve(q)


class CustomReranker:
    """Mock reranker implementing RerankerProtocol via duck typing."""

    @property
    def name(self) -> str:
        return "custom-rerank"

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        return sorted(results, key=lambda r: r.score, reverse=True)

    def rank(
        self,
        results: list[RetrievalResult],
        reverse: bool = True,
    ) -> list[RetrievalResult]:
        return sorted(results, key=lambda r: r.score, reverse=reverse)


class CustomVectorRetriever:
    """Mock vector retriever implementing VectorRetrieverContract."""

    @property
    def name(self) -> str:
        return "mock-vector-retriever"

    def retrieve_vectors(
        self,
        query_vector: list[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                source="vector-store",
                content="Dense vector match",
                score=1.0,
            )
        ]


def test_custom_duck_typed_protocol_adherence():
    mock_ret = CustomRetriever()
    assert isinstance(mock_ret, RetrieverProtocol)

    mock_rerank = CustomReranker()
    assert isinstance(mock_rerank, RerankerProtocol)

    mock_vec = CustomVectorRetriever()
    assert isinstance(mock_vec, VectorRetrieverContract)

    # Plug custom duck-typed components into RetrievalPipeline
    pipeline = RetrievalPipeline(
        retriever=mock_ret,  # type: ignore[arg-type]
        retrieval_filter=RetrievalFilter(),
        ranker=mock_rerank,  # type: ignore[arg-type]
    )
    assert isinstance(pipeline, PipelineProtocol)

    results = pipeline.run("test query")
    assert len(results) == 1
    assert results[0].score == 0.99
