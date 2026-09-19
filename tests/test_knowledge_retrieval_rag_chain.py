"""Tests for End-to-End Chain: Knowledge Ingestion -> Embedding -> VectorStore -> RetrievalManager -> RAGService -> ResearchAgent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.knowledge import (
    KnowledgeLoader,
    KnowledgeManager,
)
from scholaros.knowledge.rag.service import RAGService
from scholaros.retrieval.query import RetrievalQuery
from scholaros.services.health import HealthStatus, ServiceHealth


class MockAIProvider(AIProvider):
    """Deterministic mock provider for testing."""

    def __init__(self, response: str = "Mock generation response") -> None:
        super().__init__(name="mock-ai")
        self._response = response

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        embeddings = [[0.1, 0.2, 0.3, 0.4] for _ in request.input]
        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model or "mock-embed",
            dimensions=4,
        )

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self._response,
            model=request.model or "mock-gen",
        )

    def stream(self, request: AIRequest):
        raise NotImplementedError

    def health(self) -> ServiceHealth:
        return ServiceHealth(
            service_name="MockAIProvider",
            status=HealthStatus.HEALTHY,
        )


class MockLLM(LLM):
    """Mock LLM for RAG generation."""

    def __init__(self, answer: str = "Grounded quantum computing response") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "mock-llm-chain"

    def generate(self, messages: list[Any] | str, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
        )


class SimpleEmbeddingGenerator:
    """Mock generator that produces 4D vectors for testing."""

    def generate(self, text: str):
        class DummyEmb:
            def __init__(self, t: str):
                self.text = t
                val = float(len(t) % 5) / 5.0
                self.vector = [val, 0.5, 0.2, 0.1]

        return DummyEmb(text)


class TestKnowledgeRetrievalRAGChain:
    """Verifies end-to-end integration across knowledge, retrieval, RAG, and research agent."""

    def test_end_to_end_knowledge_to_retrieval_and_rag(self, tmp_path: Path):
        # 1. Setup mock AI & vector store & knowledge manager
        ai_provider = MockAIProvider(response="Quantum computing enables exponential speedup for specific algorithms.")
        llm = MockLLM(answer="Quantum computing enables exponential speedup for factorization algorithms.")
        vector_store = InMemoryVectorStore()
        generator = SimpleEmbeddingGenerator()

        knowledge_mgr = KnowledgeManager(
            vector_store=vector_store,
            embedding_generator=generator,  # type: ignore
            ai_provider=ai_provider,
        )
        loader = KnowledgeLoader(manager=knowledge_mgr)

        # 2. Ingest document via loader
        doc_file = tmp_path / "quantum.txt"
        doc_file.write_text(
            "Quantum algorithms like Shor's algorithm find prime factors exponentially faster than classical algorithms.",
            encoding="utf-8",
        )

        ingestion_res = loader.ingest_file(doc_file, collection_name="physics")
        assert ingestion_res.is_success
        assert ingestion_res.chunks_count > 0
        assert len(vector_store.embeddings()) > 0

        # 3. Create retrieval manager directly from KnowledgeManager factory
        retrieval_mgr = knowledge_mgr.create_retrieval_manager(ai_provider=ai_provider)

        # Verify keyword retrieval
        kw_results = retrieval_mgr.retrieve(
            RetrievalQuery(text="Shor algorithm prime factors", strategy="keyword", collections=["physics"])
        )
        assert len(kw_results) > 0
        assert "Shor" in kw_results[0].content

        # Verify semantic / vector retrieval
        sem_results = retrieval_mgr.retrieve(
            RetrievalQuery(text="quantum speedup algorithms", strategy="semantic", collections=["physics"])
        )
        assert len(sem_results) > 0

        # Verify hybrid retrieval
        hybrid_results = retrieval_mgr.retrieve(
            RetrievalQuery(text="quantum algorithms prime factors", strategy="hybrid", collections=["physics"])
        )
        assert len(hybrid_results) > 0

        # 4. Connect to RAGService
        rag_service = RAGService(
            retrieval_pipeline=knowledge_mgr.create_retrieval_pipeline(strategy_name="hybrid"),
            llm=llm,
        )

        rag_response = rag_service.generate("How does quantum computing improve factorization?")
        assert rag_response.content != ""
        assert len(rag_response.sources) > 0

        # 5. Connect to ResearchAgent via from_rag
        agent = ResearchAgent.from_rag(rag_service)
        research_result = agent.research("How does quantum computing improve factorization?")

        assert research_result.has_content()
        assert "exponential" in research_result.content.lower()
        assert len(research_result.sources) > 0
        assert research_result.is_rag is True


