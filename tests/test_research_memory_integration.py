"""
Integration tests for ScholarOS Milestone 10H — Memory & Research Knowledge Integration.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.container.container import Container
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.memory.manager import MemoryManager
from scholaros.memory.registry import MemoryRegistry
from scholaros.research.manager import ResearchSessionManager
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.result import ResearchResult
from scholaros.research.session import ResearchSession
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult
from scholaros.services.builtin.research import ResearchService


class DummyMemoryLLM(LLM):
    def __init__(self, answer: str = "Research synthesis grounded in memory and knowledge.") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "dummy-memory-model"

    def generate(self, messages: Any, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=25,
            completion_tokens=15,
            total_tokens=40,
        )


@pytest.fixture
def rag_service() -> RAGService:
    retriever = MagicMock()
    results = [
        RetrievalResult(
            content="Attention mechanisms model dependencies regardless of distance.",
            score=0.95,
            source="vaswani-2017",
            chunk_id="chunk-attn-1",
        ),
        RetrievalResult(
            content="Recurrent neural networks compute hidden states sequentially.",
            score=0.85,
            source="elman-1990",
            chunk_id="chunk-rnn-1",
        ),
    ]
    retriever.search.return_value = results
    retriever.retrieve.return_value = results
    retrieval_pipeline = RetrievalPipeline(retriever=retriever)
    llm = DummyMemoryLLM()
    rag_pipeline = RAGPipeline(retrieval_pipeline=retrieval_pipeline, llm=llm)
    return RAGService(pipeline=rag_pipeline)


@pytest.fixture
def memory_manager() -> MemoryManager:
    return MemoryManager(registry=MemoryRegistry())


@pytest.fixture
def knowledge_manager() -> KnowledgeManager:
    return KnowledgeManager()


class TestResearchMemoryKnowledgeIntegration:
    """Tests establishing the relationship between Session, Memory, Knowledge Library, RAG, and Agent."""

    def test_session_manager_lifecycle(self) -> None:
        manager = ResearchSessionManager()
        session1 = manager.create(title="Quantum Algorithms", query="What is Shor's algorithm?")
        assert session1.title == "Quantum Algorithms"
        assert session1.id is not None
        assert manager.active_session_id == session1.id
        assert manager.active_session is session1

        session2 = manager.create(title="GNN Survey", query="Graph neural network message passing")
        assert manager.active_session_id == session2.id
        assert manager.get(session1.id) is session1
        assert manager.get(session2.id) is session2
        assert len(manager) == 2

    def test_multi_turn_research_session_with_memory(
        self,
        rag_service: RAGService,
        memory_manager: MemoryManager,
        knowledge_manager: KnowledgeManager,
    ) -> None:
        pipeline = ResearchPipeline.from_rag(rag_service)
        session_manager = ResearchSessionManager(
            memory_manager=memory_manager,
            knowledge_manager=knowledge_manager,
            pipeline=pipeline,
        )

        session = session_manager.create(
            title="Transformer vs RNN Architecture Study",
            query="Transformers in NLP",
        )
        session.add_context("Focus on computational complexity")
        session.add_note("Check training parallelization advantages")

        # Turn 1: Initial research query
        res1 = session_manager.run_research(
            query="Explain self-attention parallelization",
            session_id=session.id,
            use_workflow=True,
            notes=["Self-attention allows O(1) sequential operations"],
        )
        assert isinstance(res1, ResearchResult)
        assert res1.has_workflow
        assert len(session.history) == 1
        assert session.result is res1

        # Turn 2: Follow-up query leveraging prior conversation context
        res2 = session_manager.run_research(
            query="Compare sequential operations in RNNs",
            session_id=session.id,
            use_workflow=True,
        )
        assert len(session.history) == 2
        assert session.result is res2

        # Verify MemoryManager persistence
        session_history = memory_manager.get("session_history")
        assert session_history is not None
        assert len(session_history) == 2

        research_history = memory_manager.get("research_history")
        assert research_history is not None
        assert len(research_history) == 2

    def test_publish_session_to_knowledge_library(
        self,
        rag_service: RAGService,
        memory_manager: MemoryManager,
        knowledge_manager: KnowledgeManager,
    ) -> None:
        pipeline = ResearchPipeline.from_rag(rag_service)
        session_manager = ResearchSessionManager(
            memory_manager=memory_manager,
            knowledge_manager=knowledge_manager,
            pipeline=pipeline,
        )

        session = session_manager.create(
            title="Scalable Self-Attention Survey",
            query="Efficient Transformers",
        )
        session.add_note("Linear attention reduces complexity from O(N^2) to O(N)")

        # Run research with publish_to_knowledge=True
        result = session_manager.run_research(
            query="Linear attention mechanisms",
            session_id=session.id,
            publish_to_knowledge=True,
        )
        assert result.has_content()

        # Verify KnowledgeManager has the published session document
        coll = knowledge_manager.get_or_create_collection("research_notes")
        assert len(coll) == 1
        doc = coll.get(f"session-{session.id}")
        assert doc is not None
        assert doc.title == "Scalable Self-Attention Survey"
        assert "Linear attention reduces complexity" in doc.content
        assert "Linear attention mechanisms" in doc.content
        assert doc.metadata.custom["session_id"] == session.id

    def test_agent_with_session(self, rag_service: RAGService) -> None:
        agent = ResearchAgent.from_rag(rag_service)
        session = ResearchSession(title="Agent Session", query="Language modeling")
        session.add_note("Agent working note")

        # Run workflow via agent with session
        result = agent.run_workflow(
            query="Autoregressive language models",
            session=session,
        )
        assert isinstance(result, ResearchResult)
        assert len(session.history) == 1
        assert session.history[0]["query"] == "Autoregressive language models"
        assert session.result is result

    def test_service_and_container_di(
        self,
        rag_service: RAGService,
        memory_manager: MemoryManager,
        knowledge_manager: KnowledgeManager,
    ) -> None:
        container = Container()
        container.add_instance(MemoryManager, memory_manager)
        container.add_instance(KnowledgeManager, knowledge_manager)

        pipeline = ResearchPipeline.from_rag(rag_service)
        service = ResearchService.configure_container(
            container=container,
            pipeline=pipeline,
        )

        # Verify session manager is attached and resolved
        assert service.session_manager is not None
        assert service.session_manager.memory_manager is memory_manager
        assert service.session_manager.knowledge_manager is knowledge_manager

        resolved_sm = container.resolve(ResearchSessionManager)
        assert resolved_sm is service.session_manager

        # Test session creation via service
        session = service.create_session(title="DI Session", query="Neural scaling laws")
        assert session.title == "DI Session"
        assert service.session_manager.get(session.id) is session
