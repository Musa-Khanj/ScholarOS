"""
ScholarOS Milestone 10C — Hybrid Retrieval Integration Tests.

Tests the end-to-end integration between:
- HybridRetrieverContract & RetrieverProtocol compliance
- KeywordRetriever & SemanticRetriever (VectorStore backed)
- Reciprocal Rank Fusion (RRF) with stream weights & provenance tracking
- Linear score blending with min-max normalization
- Deduplication and metadata preservation
- Collection and score filtering
- RetrievalManager hybrid strategy execution
- DI Container registration
"""

from __future__ import annotations

import math

from scholaros.container.container import Container
from scholaros.contracts.retrieval import (
    HybridRetrieverContract,
    RetrieverProtocol,
)
from scholaros.embeddings.cosine_similarity import CosineSimilarity
from scholaros.embeddings.embedding import Embedding
from scholaros.embeddings.generator import EmbeddingGenerator
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.embeddings.provider import EmbeddingProvider
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.storage import InMemoryStorage
from scholaros.retrieval.configuration import RetrievalConfiguration
from scholaros.retrieval.hybrid import HybridRetriever
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.scoring import (
    blend_scores,
    deduplicate_results,
    reciprocal_rank_fusion,
)
from scholaros.retrieval.service import RetrievalService


# ---------------------------------------------------------------------------
# Test Fixtures & Deterministic Provider
# ---------------------------------------------------------------------------

class DeterministicProvider(EmbeddingProvider):
    """
    Produces deterministic 3-dimensional normalized vectors.
    Dimension 0: Quantum / physics
    Dimension 1: Neural / AI
    Dimension 2: General / astronomy
    """

    @property
    def name(self) -> str:
        return "DeterministicProvider"

    @property
    def description(self) -> str:
        return "Deterministic provider for hybrid tests"

    @property
    def version(self) -> str:
        return "1.0.0"

    def embed(self, text: str) -> Embedding:
        low = text.lower()
        v0 = 1.0 if any(w in low for w in ("quantum", "physics", "qubit")) else 0.1
        v1 = 1.0 if any(w in low for w in ("neural", "network", "transformer", "attention")) else 0.1
        v2 = 1.0 if any(w in low for w in ("astronomy", "star", "galaxy", "telescope")) else 0.1

        norm = math.sqrt(v0 * v0 + v1 * v1 + v2 * v2) or 1.0
        return Embedding(text=text, vector=[v0 / norm, v1 / norm, v2 / norm])

    def embed_many(self, texts: list[str]) -> list[Embedding]:
        return [self.embed(t) for t in texts]


# ---------------------------------------------------------------------------
# 10C.1: Protocol & Contract Compliance
# ---------------------------------------------------------------------------

def test_hybrid_retriever_contract_compliance():
    """Verify HybridRetriever adheres to HybridRetrieverContract & RetrieverProtocol."""
    retriever = HybridRetriever(name="CustomHybrid")

    assert isinstance(retriever, HybridRetrieverContract)
    assert isinstance(retriever, RetrieverProtocol)
    assert retriever.name == "CustomHybrid"
    assert retriever.fusion_mode == "rrf"
    assert retriever.rrf_k == 60
    assert retriever.keyword_weight == 0.5
    assert retriever.semantic_weight == 0.5
    assert retriever.keyword_retriever is not None
    assert retriever.semantic_retriever is not None


# ---------------------------------------------------------------------------
# 10C.2 & 10C.3: RRF & Linear Blending with Stream Provenance
# ---------------------------------------------------------------------------

def test_reciprocal_rank_fusion_with_stream_weights_and_provenance():
    """Verify RRF calculates weighted ranks and maintains provenance metadata."""
    res1 = RetrievalResult(source="doc1", content="Quantum computing", score=0.9, chunk_id="c1")
    res2 = RetrievalResult(source="doc2", content="Neural networks", score=0.8, chunk_id="c2")
    res3 = RetrievalResult(source="doc3", content="Classical physics", score=0.7, chunk_id="c3")

    kw_stream = [res1, res2]
    sem_stream = [res2, res3, res1]

    fused = reciprocal_rank_fusion(
        [kw_stream, sem_stream],
        k=60,
        weights=[0.6, 0.4],
        stream_names=["keyword", "semantic"],
    )

    assert len(fused) == 3
    # res2 is in both streams (rank 2 in kw, rank 1 in sem)
    # RRF score = 0.6 * (1 / (60 + 2)) + 0.4 * (1 / (60 + 1))
    expected_res2 = (0.6 / 62) + (0.4 / 61)

    res2_fused = next(r for r in fused if r.chunk_id == "c2")
    assert math.isclose(res2_fused.score, expected_res2, rel_tol=1e-4)

    # Check provenance
    prov = res2_fused.metadata["provenance"]
    assert "keyword" in prov["streams"]
    assert "semantic" in prov["streams"]
    assert prov["keyword_rank"] == 2
    assert prov["semantic_rank"] == 1


def test_linear_score_blending_normalization_and_provenance():
    """Verify linear blending normalizes scores and blends with specified weights."""
    res_kw = [
        RetrievalResult(source="doc1", content="Transformer", score=10.0, chunk_id="c1"),
        RetrievalResult(source="doc2", content="RNN", score=5.0, chunk_id="c2"),
    ]
    res_sem = [
        RetrievalResult(source="doc1", content="Transformer", score=0.9, chunk_id="c1"),
        RetrievalResult(source="doc3", content="CNN", score=0.45, chunk_id="c3"),
    ]

    blended = blend_scores(
        res_kw,
        res_sem,
        weight_a=0.7,
        weight_b=0.3,
        name_a="keyword",
        name_b="semantic",
    )

    assert len(blended) == 3
    # c1 is top in both (normalized score 1.0 in kw, 1.0 in sem)
    # Blended = (1.0 * 0.7) + (1.0 * 0.3) = 1.0
    top_result = blended[0]
    assert top_result.chunk_id == "c1"
    assert math.isclose(top_result.score, 1.0, rel_tol=1e-4)

    prov = top_result.metadata["provenance"]
    assert prov["streams"] == ["keyword", "semantic"]
    assert prov["keyword_score"] == 1.0
    assert prov["semantic_score"] == 1.0


# ---------------------------------------------------------------------------
# 10C.4: Deduplication and Metadata Preservation
# ---------------------------------------------------------------------------

def test_deduplicate_results_merges_metadata_and_preserves_provenance():
    """Verify deduplication preserves the highest score and merges stream metadata."""
    r1 = RetrievalResult(
        source="doc1",
        content="Artificial Intelligence",
        score=0.75,
        chunk_id="c_ai",
        metadata={"keyword_match": True, "provenance": {"streams": ["keyword"]}},
    )
    r2 = RetrievalResult(
        source="doc1",
        content="Artificial Intelligence",
        score=0.92,
        chunk_id="c_ai",
        metadata={"embedding_model": "test-v1", "provenance": {"streams": ["semantic"]}},
    )

    deduped = deduplicate_results([r1, r2])
    assert len(deduped) == 1
    assert deduped[0].score == 0.92
    assert deduped[0].metadata["keyword_match"] is True
    assert deduped[0].metadata["embedding_model"] == "test-v1"
    assert deduped[0].metadata["provenance"]["streams"] == ["keyword", "semantic"]


# ---------------------------------------------------------------------------
# 10C.5 & 10C.6: HybridRetriever with VectorStore and Storage
# ---------------------------------------------------------------------------

def test_hybrid_retriever_dense_and_lexical_fusion():
    """Verify HybridRetriever combines lexical search with VectorStore dense search."""
    storage = InMemoryStorage()
    doc1 = KnowledgeDocument(
        identifier="doc1",
        title="Deep Learning",
        content="Deep learning and neural network architectures for vision",
    )
    storage.save_document(doc1, collection_name="ai")
    chunk1 = Chunk(
        content="Deep learning and neural network architectures for vision",
        document_id=doc1.identifier,
        identifier="chunk_ai_1",
    )
    storage.save_chunk(chunk1, collection_name="ai")

    # Dense VectorStore backend
    vstore = InMemoryVectorStore(metric=CosineSimilarity())
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider=provider)

    emb2 = generator.generate("Quantum teleportation and quantum state computing")
    emb2.metadata["chunk_id"] = "chunk_quantum"
    emb2.metadata["collection"] = "physics"
    vstore.add(emb2)

    hybrid = HybridRetriever(
        storage=storage,
        vector_store=vstore,
        generator=generator,
        fusion_mode="rrf",
        rrf_k=60,
    )

    # Query matching chunk1 via keyword and emb2 via semantic
    query = RetrievalQuery(text="neural network architectures", limit=5)
    results = hybrid.retrieve(query)

    assert len(results) >= 1
    # chunk1 should be discovered
    assert any(r.chunk_id == chunk1.identifier for r in results)


def test_retrieval_manager_hybrid_strategy_execution():
    """Verify RetrievalManager executes the hybrid strategy with vector integration."""
    storage = InMemoryStorage()
    doc = KnowledgeDocument(
        identifier="doc_nlp",
        title="NLP",
        content="Natural language processing and transformer models",
    )
    storage.save_document(doc, collection_name="docs")
    chunk = Chunk(
        content="Natural language processing and transformer models",
        document_id=doc.identifier,
        identifier="chunk_nlp_1",
    )
    storage.save_chunk(chunk, collection_name="docs")

    vstore = InMemoryVectorStore()
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider=provider)

    emb = generator.generate("Attention mechanisms in transformers")
    emb.metadata["chunk_id"] = "chunk_attn"
    emb.metadata["collection"] = "docs"
    vstore.add(emb)

    manager = RetrievalManager(
        storage=storage,
        vector_store=vstore,
        embedding_generator=generator,
        config=RetrievalConfiguration(default_strategy="hybrid"),
    )

    assert manager.hybrid_retriever is not None

    query = RetrievalQuery(text="transformer attention", strategy="hybrid", limit=5)
    results = manager.retrieve(query)

    assert len(results) > 0
    # Top result should have hybrid provenance
    assert "provenance" in results[0].metadata


# ---------------------------------------------------------------------------
# 10C.7: DI Container Registration
# ---------------------------------------------------------------------------

def test_hybrid_retriever_di_container_registration():
    """Verify RetrievalService registers HybridRetriever in DI container."""
    container = Container()
    vstore = InMemoryVectorStore()
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider=provider)

    service = RetrievalService.configure_container(
        container=container,
        vector_store=vstore,
        embedding_generator=generator,
    )

    assert container.registry.contains(RetrievalService)
    assert container.registry.contains(HybridRetriever)
    resolved_hybrid = container.resolve(HybridRetriever)
    assert isinstance(resolved_hybrid, HybridRetriever)
    assert resolved_hybrid is service.manager.hybrid_retriever
