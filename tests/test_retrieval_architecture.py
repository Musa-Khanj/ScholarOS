"""
ScholarOS Retrieval Subsystem Architecture Tests.

Tests the complete retrieval architecture:
- RetrievalQuery & RetrievalResult models
- RetrievalContext & ContextBuilder
- Scoring algorithms (RRF, min-max, blend, deduplication)
- Multi-predicate filters
- Retrievers (Keyword, Semantic, Hybrid)
- Strategies & StrategyRegistry
- Rerankers (Score, CrossEncoder, LLM)
- Multi-stage RetrievalPipeline
- Operational Metrics & Diagnostics
- EventBus event integration
- RetrievalService lifecycle & DI Container registration
"""

from __future__ import annotations

import pytest

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.events.event import Event
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.storage import InMemoryStorage
from scholaros.retrieval.configuration import RetrievalConfiguration
from scholaros.retrieval.context import ContextBuilder
from scholaros.retrieval.events import (
    ContextBuilt,
    RetrievalCompleted,
    RetrievalStarted,
)
from scholaros.retrieval.exceptions import (
    RetrievalError,
    RetrieverNotFoundError,
)
from scholaros.retrieval.filters import RetrievalFilter
from scholaros.retrieval.hybrid import HybridRetriever
from scholaros.retrieval.keyword import KeywordRetriever
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.metrics import RetrievalMetrics
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.reranker import (
    CrossEncoderReranker,
    LLMReranker,
    ScoreReranker,
)
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.scoring import (
    deduplicate_results,
    min_max_normalize,
    reciprocal_rank_fusion,
)
from scholaros.retrieval.semantic import SemanticRetriever
from scholaros.retrieval.service import RetrievalService
from scholaros.retrieval.strategies import (
    KeywordStrategy,
    StrategyRegistry,
)
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.lifecycle import ServiceState


# ---------------------------------------------------------------------------
# Mock AI Provider for deterministic testing
# ---------------------------------------------------------------------------

class MockAIProvider(AIProvider):
    """Deterministic mock provider for embeddings and reranking generation."""

    def __init__(self) -> None:
        super().__init__(name="mock-ai")

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        embeddings: list[list[float]] = []
        for text in request.input:
            text_lower = text.lower()
            # Generate deterministic 4-dimensional normalized vectors based on content
            v0 = 1.0 if "transformer" in text_lower or "attention" in text_lower else 0.1
            v1 = 1.0 if "vision" in text_lower or "image" in text_lower else 0.1
            v2 = 1.0 if "nlp" in text_lower or "language" in text_lower else 0.1
            v3 = 1.0 if "graph" in text_lower else 0.1
            norm = (v0**2 + v1**2 + v2**2 + v3**2) ** 0.5
            embeddings.append([v0 / norm, v1 / norm, v2 / norm, v3 / norm])
        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model or "mock-embed",
            dimensions=4,
        )

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content="1, 2, 3",
            model=request.model or "mock-gen",
        )

    def stream(self, request: AIRequest):
        raise NotImplementedError

    def health(self) -> ServiceHealth:
        return ServiceHealth(
            service_name="MockAIProvider",
            status=HealthStatus.HEALTHY,
        )


# ---------------------------------------------------------------------------
# Tests: Part 1 — Query and Result Models
# ---------------------------------------------------------------------------

def test_retrieval_query_validation_and_methods():
    with pytest.raises(RetrievalError):
        RetrievalQuery(text="   ")

    with pytest.raises(RetrievalError):
        RetrievalQuery(text="valid", limit=0)

    q = RetrievalQuery(text="neural search", limit=5, min_score=0.3)
    assert q.text == "neural search"
    assert q.limit == 5
    assert q.min_score == 0.3

    q_filtered = q.with_filter("topic", "ai")
    assert q_filtered.filters == {"topic": "ai"}
    assert q.filters == {}

    q_lim = q.with_limit(20)
    assert q_lim.limit == 20

    q_strat = q.with_strategy("semantic")
    assert q_strat.strategy == "semantic"

    d = q.to_dict()
    q_reconstructed = RetrievalQuery.from_dict(d)
    assert q_reconstructed.text == q.text
    assert q_reconstructed.limit == q.limit


def test_retrieval_result_extended_features():
    chunk = Chunk(
        identifier="chunk-101",
        document_id="doc-42",
        content="Self-attention improves deep language models.",
        metadata={"domain": "cs.cl"},
    )
    res = RetrievalResult.from_chunk(chunk, score=0.88, collection="arxiv")
    assert res.chunk_id == "chunk-101"
    assert res.document_id == "doc-42"
    assert res.collection == "arxiv"
    assert res.score == 0.88
    assert res.raw_score == 0.88
    assert res.metadata["domain"] == "cs.cl"

    # Score update & rerank update
    res_mod = res.with_score(0.95)
    assert res_mod.score == 0.95
    assert res_mod.raw_score == 0.88

    res_rerank = res.with_rerank_score(0.99)
    assert res_rerank.score == 0.99
    assert res_rerank.rerank_score == 0.99

    res_meta = res.with_metadata({"verified": True})
    assert res_meta.metadata["verified"] is True
    assert res_meta.metadata["domain"] == "cs.cl"


# ---------------------------------------------------------------------------
# Tests: Part 2 — Context Construction
# ---------------------------------------------------------------------------

def test_context_builder_and_retrieval_context():
    r1 = RetrievalResult(source="doc1", content="Paragraph one about transformers.", score=0.9)
    r2 = RetrievalResult(source="doc2", content="Paragraph two about self-attention mechanisms.", score=0.8)
    r3 = RetrievalResult(source="doc3", content="Paragraph three about vision transformers.", score=0.7)

    builder = ContextBuilder(token_budget=50)
    context = builder.build("what is self-attention?", [r1, r2, r3])

    assert len(context) >= 2
    assert "doc1" in context.sources()
    assert context.total_tokens > 0

    text_view = context.format_as_text(include_sources=True, include_metadata=False)
    assert "[1] (Source: doc1)" in text_view
    assert "Paragraph one" in text_view

    messages = context.format_as_messages(role="system")
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert "Relevant context:" in messages[0]["content"]


# ---------------------------------------------------------------------------
# Tests: Part 3 — Scoring Algorithms
# ---------------------------------------------------------------------------

def test_scoring_and_fusion():
    r1 = RetrievalResult(source="s1", content="content a", score=10.0, chunk_id="c1")
    r2 = RetrievalResult(source="s2", content="content b", score=5.0, chunk_id="c2")

    # Min-max normalization
    norm = min_max_normalize([r1, r2])
    assert pytest.approx(norm[0].score, 0.01) == 1.0
    assert pytest.approx(norm[1].score, 0.01) == 0.0

    # Reciprocal rank fusion
    list_a = [r1, r2]
    list_b = [r2, r1]
    fused = reciprocal_rank_fusion([list_a, list_b], k=60)
    assert len(fused) == 2
    # Both items have identical ranks across the two lists (1 and 2), so fused scores are equal
    assert pytest.approx(fused[0].score, 1e-4) == fused[1].score

    # Deduplication
    dupe = RetrievalResult(source="s1", content="content a", score=12.0, chunk_id="c1")
    deduped = deduplicate_results([r1, dupe], key_func="chunk")
    assert len(deduped) == 1
    assert deduped[0].score == 12.0


# ---------------------------------------------------------------------------
# Tests: Part 4 — Filters
# ---------------------------------------------------------------------------

def test_retrieval_filter_multi_predicate():
    r1 = RetrievalResult(
        source="s1",
        content="Machine learning overview",
        score=0.85,
        collection="papers",
        document_id="d1",
        metadata={"year": 2024, "peer_reviewed": True},
    )
    r2 = RetrievalResult(
        source="s2",
        content="Deep learning basics",
        score=0.45,
        collection="drafts",
        document_id="d2",
        metadata={"year": 2021, "peer_reviewed": False},
    )

    f = RetrievalFilter()

    # Minimum score filter
    assert len(f.filter([r1, r2], minimum_score=0.5)) == 1

    # Collection filter
    assert len(f.filter([r1, r2], collections=["papers"])) == 1
    assert f.filter([r1, r2], collections=["papers"])[0].document_id == "d1"

    # Metadata predicate filter
    assert len(f.filter([r1, r2], metadata_filters={"year": 2024})) == 1
    assert len(f.filter([r1, r2], metadata_filters={"peer_reviewed": False})) == 1

    # Query object filter
    q = RetrievalQuery(text="test", min_score=0.8, collections=["papers"])
    filtered_by_query = f.filter_by_query([r1, r2], q)
    assert len(filtered_by_query) == 1
    assert filtered_by_query[0].document_id == "d1"


# ---------------------------------------------------------------------------
# Tests: Part 5 — Retrievers (Keyword, Semantic, Hybrid)
# ---------------------------------------------------------------------------

def test_keyword_retriever():
    storage = InMemoryStorage()
    doc = KnowledgeDocument(
        identifier="doc-1",
        title="Attention Paper",
        content="Transformer neural network models with self-attention.",
        chunks=[
            Chunk(identifier="c1", document_id="doc-1", content="Transformers rely on multi-head attention mechanisms."),
            Chunk(identifier="c2", document_id="doc-1", content="Convolutional layers process visual feature grids."),
        ],
    )
    storage.save_document(doc, collection_name="default")

    retriever = KeywordRetriever(storage=storage)
    results = retriever.retrieve(RetrievalQuery(text="attention mechanism", limit=5))

    assert len(results) >= 1
    assert results[0].chunk_id == "c1"
    assert results[0].score > 0.0


def test_semantic_and_hybrid_retriever():
    storage = InMemoryStorage()
    doc = KnowledgeDocument(
        identifier="doc-ai",
        title="NLP and Vision",
        content="Overview of multimodal models.",
        chunks=[
            Chunk(identifier="c-trans", document_id="doc-ai", content="Transformer self-attention for language."),
            Chunk(identifier="c-vis", document_id="doc-ai", content="Vision models for image processing."),
        ],
    )
    storage.save_document(doc, collection_name="default")

    ai_provider = MockAIProvider()

    sem_retriever = SemanticRetriever(ai_provider=ai_provider, storage=storage)
    sem_results = sem_retriever.retrieve(RetrievalQuery(text="transformer attention", limit=5))
    assert len(sem_results) >= 1
    assert sem_results[0].chunk_id == "c-trans"

    hybrid_retriever = HybridRetriever(
        storage=storage,
        ai_provider=ai_provider,
        fusion_mode="rrf",
    )
    hybrid_results = hybrid_retriever.retrieve(RetrievalQuery(text="transformer attention", limit=5))
    assert len(hybrid_results) >= 1
    assert hybrid_results[0].chunk_id == "c-trans"


# ---------------------------------------------------------------------------
# Tests: Part 6 — Rerankers
# ---------------------------------------------------------------------------

def test_rerankers():
    r1 = RetrievalResult(source="s1", content="Short mention", score=0.9)
    r2 = RetrievalResult(source="s2", content="Deep Transformer neural network self-attention architecture", score=0.6)

    # Score reranker preserves initial score order
    score_reranker = ScoreReranker()
    res_score = score_reranker.rerank("transformer attention", [r1, r2])
    assert res_score[0].source == "s1"

    # Cross encoder reranker gives higher score to higher relevance/overlap
    ce_reranker = CrossEncoderReranker()
    res_ce = ce_reranker.rerank("transformer attention", [r1, r2])
    assert res_ce[0].source == "s2"
    assert res_ce[0].rerank_score is not None

    # LLM reranker with fallback
    llm_reranker = LLMReranker(ai_provider=MockAIProvider())
    res_llm = llm_reranker.rerank("transformer attention", [r1, r2])
    assert len(res_llm) == 2


# ---------------------------------------------------------------------------
# Tests: Part 7 — Strategies and StrategyRegistry
# ---------------------------------------------------------------------------

def test_strategies_and_registry():
    storage = InMemoryStorage()
    kw_retriever = KeywordRetriever(storage=storage)
    strategy = KeywordStrategy(kw_retriever)

    registry = StrategyRegistry()
    registry.register("keyword", strategy)

    assert registry.contains("keyword")
    assert registry.get("keyword") is strategy
    assert "keyword" in registry.list_strategies()

    with pytest.raises(RetrieverNotFoundError):
        registry.get("non-existent")


# ---------------------------------------------------------------------------
# Tests: Part 8 — RetrievalManager, Pipeline, Events, and Metrics
# ---------------------------------------------------------------------------

def test_retrieval_manager_pipeline_events_and_metrics():
    storage = InMemoryStorage()
    doc = KnowledgeDocument(
        identifier="doc-arch",
        title="Architecture",
        content="Transformer models with self-attention.",
        chunks=[
            Chunk(identifier="c-arch-1", document_id="doc-arch", content="Transformer models revolutionize NLP."),
        ],
    )
    storage.save_document(doc, collection_name="default")

    event_bus = EventBus()
    received_events: list[Event] = []
    event_bus.subscribe("RetrievalStarted", lambda ev: received_events.append(ev))
    event_bus.subscribe("RetrievalCompleted", lambda ev: received_events.append(ev))
    event_bus.subscribe("ContextBuilt", lambda ev: received_events.append(ev))

    metrics = RetrievalMetrics()
    config = RetrievalConfiguration(default_strategy="keyword", enable_events=True, enable_metrics=True)

    manager = RetrievalManager(
        storage=storage,
        ai_provider=MockAIProvider(),
        event_bus=event_bus,
        config=config,
        metrics=metrics,
    )

    # Retrieval
    results = manager.retrieve(RetrievalQuery(text="transformer nlp", limit=5))
    assert len(results) >= 1

    # Check metrics
    assert metrics.query_count == 1
    assert metrics.success_count == 1
    assert metrics.failure_count == 0

    # Check events
    event_types = [type(e) for e in received_events]
    assert RetrievalStarted in event_types
    assert RetrievalCompleted in event_types

    # Context building
    context = manager.build_context("transformer nlp", results)
    assert len(context) >= 1
    assert ContextBuilt in [type(e) for e in received_events]

    # Pipeline
    pipeline = manager.create_pipeline("keyword")
    pipe_results, pipe_ctx = pipeline.execute(RetrievalQuery(text="transformer nlp"), build_context=True)
    assert len(pipe_results) >= 1
    assert pipe_ctx is not None


# ---------------------------------------------------------------------------
# Tests: Part 9 — RetrievalService & DI Container
# ---------------------------------------------------------------------------

def test_retrieval_service_lifecycle_and_container():
    storage = InMemoryStorage()
    container = Container()

    service = RetrievalService.configure_container(
        container=container,
        storage=storage,
        ai_provider=MockAIProvider(),
    )

    # Lifecycle transitions
    assert service.status == ServiceState.REGISTERED
    service.initialize()
    assert service.status == ServiceState.INITIALIZED
    service.start()
    assert service.status == ServiceState.RUNNING
    assert service.is_running() is True

    # Health check
    health = service.health()
    assert health.status == HealthStatus.HEALTHY

    service.stop()
    assert service.status == ServiceState.STOPPED

    service.shutdown()
    assert service.status == ServiceState.SHUTDOWN

    # DI Container verification
    resolved_service = container.resolve(RetrievalService)
    assert resolved_service is service

    resolved_manager = container.resolve(RetrievalManager)
    assert resolved_manager is service.manager

    resolved_metrics = container.resolve(RetrievalMetrics)
    assert resolved_metrics is service.metrics
