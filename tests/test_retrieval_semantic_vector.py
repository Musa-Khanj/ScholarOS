"""
ScholarOS Milestone 10B — Semantic Retrieval Integration Tests.

Tests the end-to-end integration between:
- EmbeddingProvider & EmbeddingGenerator
- VectorStore (InMemoryVectorStore)
- SemanticRetriever & VectorStoreRetriever
- RetrievalResult.from_embedding domain conversion
- Metadata propagation and similarity scoring
- RetrievalManager & DI Container wiring
"""

from __future__ import annotations

import math

from scholaros.container.container import Container
from scholaros.contracts.retrieval import (
    RetrieverProtocol,
    VectorRetrieverContract,
)
from scholaros.embeddings.cosine_similarity import CosineSimilarity
from scholaros.embeddings.embedding import Embedding
from scholaros.embeddings.generator import EmbeddingGenerator
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.embeddings.provider import EmbeddingProvider
from scholaros.embeddings.vector_store import VectorStore
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.semantic import (
    SemanticRetriever,
    VectorStoreRetriever,
)
from scholaros.retrieval.service import RetrievalService


# ---------------------------------------------------------------------------
# Deterministic Mock Embedding Provider
# ---------------------------------------------------------------------------

class DeterministicProvider(EmbeddingProvider):
    """
    Deterministic embedding provider producing normalized 3D vectors
    based on semantic keyword presence.
    """

    @property
    def name(self) -> str:
        return "DeterministicProvider"

    @property
    def description(self) -> str:
        return "Deterministic test provider"

    @property
    def version(self) -> str:
        return "1.0.0"

    def embed(self, text: str) -> Embedding:
        t = text.lower()
        v0 = 1.0 if "transformer" in t or "attention" in t else 0.1
        v1 = 1.0 if "vision" in t or "image" in t else 0.1
        v2 = 1.0 if "graph" in t or "network" in t else 0.1

        norm = math.sqrt(v0 * v0 + v1 * v1 + v2 * v2)
        norm_vec = [v0 / norm, v1 / norm, v2 / norm]
        return Embedding(text=text, vector=norm_vec)


# ---------------------------------------------------------------------------
# Test 10B.1 & 10B.3: RetrievalResult.from_embedding Factory & Metadata Propagation
# ---------------------------------------------------------------------------

def test_retrieval_result_from_embedding():
    emb = Embedding(
        text="Self-attention mechanisms across sequences.",
        vector=[0.8, 0.5, 0.3],
        metadata={
            "source": "arxiv:1706.03762",
            "chunk_id": "chunk-99",
            "document_id": "doc-vaswani",
            "collection": "nlp_papers",
            "year": 2017,
        },
    )

    result = RetrievalResult.from_embedding(emb, score=0.942)

    assert result.content == "Self-attention mechanisms across sequences."
    assert result.source == "arxiv:1706.03762"
    assert result.score == 0.942
    assert result.chunk_id == "chunk-99"
    assert result.document_id == "doc-vaswani"
    assert result.collection == "nlp_papers"
    assert result.metadata["year"] == 2017


# ---------------------------------------------------------------------------
# Test 10B.2 & 10B.4: SemanticRetriever with VectorStore & EmbeddingGenerator
# ---------------------------------------------------------------------------

def test_semantic_retriever_with_vector_store():
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider)
    vector_store = InMemoryVectorStore(metric=CosineSimilarity())

    # Populate vector store
    e1 = provider.embed("Transformer architectures for natural language processing")
    e1._metadata = {"source": "nlp-doc", "collection": "nlp", "chunk_id": "c1"}
    vector_store.add(e1)

    e2 = provider.embed("Computer vision and image convolutional features")
    e2._metadata = {"source": "vision-doc", "collection": "vision", "chunk_id": "c2"}
    vector_store.add(e2)

    e3 = provider.embed("Graph neural networks for relational learning")
    e3._metadata = {"source": "graph-doc", "collection": "graph", "chunk_id": "c3"}
    vector_store.add(e3)

    retriever = SemanticRetriever(
        generator=generator,
        vector_store=vector_store,
    )

    assert isinstance(retriever, RetrieverProtocol)
    assert isinstance(retriever, VectorRetrieverContract)

    # Search for transformer/attention
    query = RetrievalQuery(text="transformer attention", limit=2)
    results = retriever.retrieve(query)

    assert len(results) == 2
    # First match should be the NLP document
    assert results[0].source == "nlp-doc"
    assert results[0].score > results[1].score
    assert results[0].chunk_id == "c1"

    # Search with minimum score threshold
    strict_query = RetrievalQuery(text="transformer attention", limit=5, min_score=0.9)
    strict_results = retriever.retrieve(strict_query)
    for r in strict_results:
        assert r.score >= 0.9

    # Search with collection filtering
    col_query = RetrievalQuery(text="vision", limit=5, collections=["vision"])
    col_results = retriever.retrieve(col_query)
    assert len(col_results) == 1
    assert col_results[0].source == "vision-doc"


def test_vector_store_retriever_subclass_and_raw_vectors():
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider)
    vector_store = InMemoryVectorStore(metric=CosineSimilarity())

    e1 = provider.embed("Transformer models with multi-head attention")
    e1._metadata = {"source": "paper-1"}
    vector_store.add(e1)

    retriever = VectorStoreRetriever(
        vector_store=vector_store,
        generator=generator,
    )

    # Test raw vector retrieval contract
    query_vec = provider.embed("attention").vector
    vec_results = retriever.retrieve_vectors(query_vec, limit=5, min_score=0.5)

    assert len(vec_results) == 1
    assert vec_results[0].source == "paper-1"
    assert vec_results[0].score >= 0.5


# ---------------------------------------------------------------------------
# Test 10B.5: RetrievalManager Integration with Vector Store
# ---------------------------------------------------------------------------

def test_retrieval_manager_vector_integration():
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider)
    vector_store = InMemoryVectorStore(metric=CosineSimilarity())

    e1 = provider.embed("Transformers revolutionize research")
    e1._metadata = {"source": "ai-paper"}
    vector_store.add(e1)

    manager = RetrievalManager(
        vector_store=vector_store,
        embedding_generator=generator,
    )

    assert manager.vector_store is vector_store
    assert manager.embedding_generator is generator
    assert manager.strategies.contains("semantic")
    assert manager.strategies.contains("vector")

    # Retrieve through manager with strategy="semantic"
    res_sem = manager.retrieve(RetrievalQuery(text="transformers", strategy="semantic"))
    assert len(res_sem) == 1
    assert res_sem[0].source == "ai-paper"

    # Retrieve through manager with strategy="vector"
    res_vec = manager.retrieve(RetrievalQuery(text="transformers", strategy="vector"))
    assert len(res_vec) == 1
    assert res_vec[0].source == "ai-paper"

    # Metrics recorded
    assert manager.metrics.query_count == 2
    assert manager.metrics.success_count == 2


# ---------------------------------------------------------------------------
# Test 10B.6: DI Container Registration
# ---------------------------------------------------------------------------

def test_retrieval_service_container_wiring_with_vector_store():
    provider = DeterministicProvider()
    generator = EmbeddingGenerator(provider)
    vector_store = InMemoryVectorStore(metric=CosineSimilarity())
    container = Container()

    service = RetrievalService.configure_container(
        container=container,
        vector_store=vector_store,
        embedding_generator=generator,
    )

    assert service.manager.vector_store is vector_store
    assert service.manager.embedding_generator is generator

    # Resolve from container
    resolved_service = container.resolve(RetrievalService)
    assert resolved_service is service

    resolved_store = container.resolve(VectorStore)
    assert resolved_store is vector_store

    resolved_generator = container.resolve(EmbeddingGenerator)
    assert resolved_generator is generator
