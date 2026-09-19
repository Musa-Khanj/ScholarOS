"""
Integration tests for ScholarOS RAG Dependency Injection & Container Registration (Milestone 10E).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.container.container import Container
import math
from scholaros.embeddings.cosine_similarity import CosineSimilarity
from scholaros.embeddings.embedding import Embedding
from scholaros.embeddings.generator import EmbeddingGenerator
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.embeddings.provider import EmbeddingProvider
from scholaros.embeddings.vector_store import VectorStore
from scholaros.knowledge.rag.configuration import RAGConfiguration
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.service import RetrievalService


class DeterministicProvider(EmbeddingProvider):
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
        v0 = 1.0 if "graph" in t or "relational" in t else 0.1
        v1 = 1.0 if "vision" in t else 0.1
        v2 = 1.0 if "nlp" in t else 0.1
        norm = math.sqrt(v0 * v0 + v1 * v1 + v2 * v2)
        return Embedding(text=text, vector=[v0 / norm, v1 / norm, v2 / norm])


class MockLLM(LLM):
    def __init__(self, answer: str = "Grounded response") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "mock-llm-10e"

    def generate(self, messages: list[Any] | str, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=12,
            completion_tokens=6,
            total_tokens=18,
        )


class TestRAGContainerIntegration:
    """Test RAG subsystem integration with ScholarOS DI Container."""

    def test_rag_service_configure_container_and_resolution(self) -> None:
        container = Container()
        mock_retriever = MagicMock()
        mock_retrieval_pipeline = RetrievalPipeline(retriever=mock_retriever)
        llm = MockLLM()
        config = RAGConfiguration(
            default_strategy="hybrid",
            default_limit=5,
            fallback_on_empty=True,
        )

        service = RAGService.configure_container(
            container=container,
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
            config=config,
        )

        # Verify container resolution
        resolved_service = container.resolve(RAGService)
        assert resolved_service is service

        resolved_pipeline = container.resolve(RAGPipeline)
        assert resolved_pipeline is service.pipeline

        resolved_config = container.resolve(RAGConfiguration)
        assert resolved_config is config
        assert resolved_config.default_strategy == "hybrid"
        assert resolved_config.default_limit == 5

    def test_rag_service_with_retrieval_manager_container_wiring(self) -> None:
        container = Container()
        provider = DeterministicProvider()
        generator = EmbeddingGenerator(provider)
        vector_store = InMemoryVectorStore(metric=CosineSimilarity())

        # Populate vector store with knowledge chunk
        e1 = provider.embed("Graph neural networks represent relational data.")
        e1._metadata = {"source": "gnn-paper", "collection": "ml", "chunk_id": "c1"}
        vector_store.add(e1)

        # Wire RetrievalService into container
        retrieval_service = RetrievalService.configure_container(
            container=container,
            vector_store=vector_store,
            embedding_generator=generator,
        )

        llm = MockLLM("Graph neural networks excel at relational learning.")
        rag_config = RAGConfiguration(default_strategy="semantic", default_limit=3)

        # Wire RAGService using RetrievalService.manager
        rag_service = RAGService.configure_container(
            container=container,
            retrieval_manager=retrieval_service.manager,
            llm=llm,
            config=rag_config,
        )

        # Validate DI container state
        assert container.resolve(RetrievalService) is retrieval_service
        assert container.resolve(RetrievalManager) is retrieval_service.manager
        assert container.resolve(VectorStore) is vector_store
        assert container.resolve(EmbeddingGenerator) is generator
        assert container.resolve(RAGService) is rag_service
        assert container.resolve(RAGPipeline) is rag_service.pipeline
        assert container.resolve(RAGConfiguration) is rag_config

        # Execute end-to-end query through resolved RAGService
        answer = rag_service.ask("Explain relational data learning")
        assert answer == "Graph neural networks excel at relational learning."

        response = rag_service.generate("Explain relational data learning")
        assert response.content == "Graph neural networks excel at relational learning."
        assert response.has_context is True
        assert len(response.results) == 1
        assert response.results[0].source == "gnn-paper"
        assert response.diagnostics["strategy"] == "semantic"
        assert response.diagnostics["results_count"] == 1
