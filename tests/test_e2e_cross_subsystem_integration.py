"""
ScholarOS Cross-Subsystem End-to-End Integration Test Suite (Milestone 10P).

Validates the full vertical architecture from Presentation to AI Provider:
GUI -> Application -> Services -> Research -> RAG -> Retrieval -> Knowledge -> LLM
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.manager import AIManager
from scholaros.ai.provider import AIProvider
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.gui.application import GUIApplication
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.service import RAGService
from scholaros.knowledge.storage import InMemoryStorage
from scholaros.observability import (
    DiagnosticsRegistry,
    RAGTrace,
    TelemetryCollector,
    TelemetryEventSubscriber,
)
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.result import ResearchResult
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.services.health import HealthStatus, ServiceHealth


class MockE2ELLM(LLM):
    """Deterministic LLM simulating generation over retrieved research context."""

    def __init__(self, model_name: str = "mock-scholar-llm") -> None:
        self._model_name = model_name
        self.last_messages: list[Any] = []

    @property
    def model(self) -> str:
        return self._model_name

    def generate(self, messages: list[Message] | str) -> LLMResponse:
        if isinstance(messages, str):
            msgs: list[Any] = [messages]
        else:
            msgs = list(messages)
        self.last_messages = msgs
        # Check that retrieved knowledge context was actually passed to the LLM
        combined_text = " ".join(getattr(m, "content", str(m)) for m in msgs)
        if "Quantum Supremacy" in combined_text or "Sycamore" in combined_text:
            content = (
                "Quantum supremacy was demonstrated using the Sycamore processor, "
                "sampling random circuits in 200 seconds [Source: nature-2019]."
            )
        else:
            content = "General research answer without specific knowledge context."

        return LLMResponse(
            content=content,
            model=self.model,
            prompt_tokens=85,
            completion_tokens=28,
            total_tokens=113,
        )


class MockE2EAIProvider(AIProvider):
    """AI Provider for health checks and service integration."""

    def __init__(self, name: str = "mock-e2e-provider") -> None:
        super().__init__(name=name)

    def is_available(self) -> bool:
        return True

    def generate(self, request: Any) -> Any:
        from scholaros.ai.response import AIResponse

        return AIResponse(content="mock", model="mock-model")

    def stream(self, request: Any) -> Any:
        return iter(["mock"])

    def embed(self, request: Any) -> Any:
        from scholaros.ai.embedding import EmbeddingResponse

        return EmbeddingResponse(
            embeddings=[[0.1, 0.2]],
            model="mock-embedder",
            dimensions=2,
        )

    def health(self) -> ServiceHealth:
        return ServiceHealth(
            service_name="MockE2EAIProvider",
            status=HealthStatus.HEALTHY,
            details="Operating normally",
        )


class TestCrossSubsystemEndToEndIntegration:
    """
    Tests cross-subsystem interaction across all 8 architectural layers:
    GUI -> Application -> Services -> Research -> RAG -> Retrieval -> Knowledge -> LLM
    """

    @pytest.fixture
    def wired_system(self) -> dict[str, Any]:
        """Wire up the full vertical stack from storage up to GUIApplication."""
        # 1. EventBus & Observability
        event_bus = EventBus()
        telemetry = TelemetryCollector.get_default()
        telemetry.reset()
        subscriber = TelemetryEventSubscriber(event_bus=event_bus, telemetry=telemetry)
        subscriber.subscribe()
        DiagnosticsRegistry.get_default().clear()

        # 2. Knowledge Storage & Ingestion
        storage = InMemoryStorage()
        collection = KnowledgeCollection(name="quantum-physics", description="Quantum papers")
        storage.save_collection(collection)

        from scholaros.knowledge.source import KnowledgeSource

        k_source = KnowledgeSource(uri="nature-2019", source_type="paper")
        chunk = Chunk(
            identifier="chunk_sycamore_01",
            document_id="doc_nature_quantum",
            content="Sycamore processor achieved quantum supremacy in 200 seconds over 53 qubits.",
            metadata={"year": 2019, "source": "nature-2019"},
        )
        doc = KnowledgeDocument(
            identifier="doc_nature_quantum",
            title="Quantum Supremacy Using a Programmable Superconducting Processor",
            content="Quantum supremacy demonstrated on Sycamore processor sampling random circuits.",
            source=k_source,
            chunks=[chunk],
        )
        storage.save_document(doc, collection_name="quantum-physics")
        storage.save_chunk(chunk)

        from scholaros.retrieval.keyword import KeywordRetriever

        retriever = KeywordRetriever(storage=storage)
        retrieval_pipeline = RetrievalPipeline(retriever=retriever)

        # 4. LLM & AI Layer
        llm = MockE2ELLM(model_name="scholar-alpha")
        ai_provider = MockE2EAIProvider()
        ai_mgr = AIManager()
        ai_mgr.register_provider(ai_provider, default=True)

        # 5. RAG Pipeline & Service
        rag_pipeline = RAGPipeline(
            retrieval_pipeline=retrieval_pipeline,
            llm=llm,
            event_bus=event_bus,
        )
        rag_service = RAGService(pipeline=rag_pipeline)

        # 6. Research Layer (ResearchAgent & ResearchPipeline)
        research_pipeline = ResearchPipeline.from_rag(rag_service)
        research_agent = ResearchAgent(
            pipeline=research_pipeline,
        )

        # 7. Services & Dependency Injection Container
        container = Container()
        container.add_instance(EventBus, event_bus)
        container.add_instance(InMemoryStorage, storage)
        container.add_instance(RetrievalPipeline, retrieval_pipeline)
        container.add_instance(RAGPipeline, rag_pipeline)
        container.add_instance(ResearchPipeline, research_pipeline)
        container.add_instance(ResearchAgent, research_agent)
        container.add_instance(AIManager, ai_mgr)

        # 8. GUI Window & GUIApplication Orchestration
        mock_window = MagicMock()
        app = GUIApplication(
            window=mock_window,
            rag_pipeline=rag_pipeline,
            research_pipeline=research_pipeline,
            ai_manager=ai_mgr,
            event_bus=event_bus,
            container=container,
        )

        return {
            "app": app,
            "research_agent": research_agent,
            "research_pipeline": research_pipeline,
            "rag_pipeline": rag_pipeline,
            "storage": storage,
            "llm": llm,
            "event_bus": event_bus,
            "telemetry": telemetry,
            "subscriber": subscriber,
        }

    def test_e2e_full_chain_query_and_result_provenance(
        self, wired_system: dict[str, Any]
    ) -> None:
        """
        Verify: GUIApplication -> ResearchPipeline -> RAGPipeline -> Retrieval -> Knowledge -> LLM
        delivers an accurate research synthesis with complete provenance and citations.
        """
        app: GUIApplication = wired_system["app"]
        research_pipeline: ResearchPipeline = wired_system["research_pipeline"]

        # 1. User executes research task via ResearchPipeline
        query = "What processor achieved Quantum Supremacy and in what time?"
        result = research_pipeline.execute(query)

        # Verify Result structure
        assert isinstance(result, ResearchResult)
        assert "Sycamore processor" in result.content
        assert "200 seconds" in result.content
        assert result.model == "scholar-alpha"
        assert result.sources == ("chunk:chunk_sycamore_01",)

        # Verify trace_id propagation
        trace_id = getattr(result.response, "metadata", {}).get("trace_id")
        assert trace_id is not None

        # 2. Inspect trace from Application layer (answering: 'The research answer is wrong')
        trace = app.get_trace(trace_id)
        assert trace is not None
        assert isinstance(trace, RAGTrace)
        assert trace.query == query
        assert trace.model == "scholar-alpha"
        assert trace.is_success is True
        assert trace.total_tokens == 113

        # 3. Verify markdown diagnostic generation
        markdown_report = trace.to_markdown()
        assert f"# RAG Diagnostic Trace: `{trace_id}`" in markdown_report
        assert "Sycamore processor achieved quantum supremacy" in markdown_report
        assert "scholar-alpha" in markdown_report
        assert "Retrieval" in markdown_report
        assert "LLM Generation" in markdown_report

    def test_e2e_agent_execution_with_citations_and_diagnostics(
        self, wired_system: dict[str, Any]
    ) -> None:
        """
        Verify ResearchAgent execution dispatches through pipeline and yields citations.
        """
        agent: ResearchAgent = wired_system["research_agent"]
        query = "Detail the Sycamore experiment"
        res = agent.execute(query)

        assert isinstance(res, ResearchResult)
        assert "Sycamore" in res.content
        assert res.model == "scholar-alpha"

    def test_e2e_event_propagation_and_telemetry_capture(
        self, wired_system: dict[str, Any]
    ) -> None:
        """
        Verify that multi-layer execution emits events through EventBus and
        automatically populates telemetry percentiles and counters.
        """
        app: GUIApplication = wired_system["app"]
        rag_pipeline: RAGPipeline = wired_system["rag_pipeline"]

        # Run 3 queries through RAGPipeline
        for i in range(3):
            req = RAGRequest(query=f"Quantum query {i}")
            rag_pipeline.run(req)

        # Inspect telemetry snapshot via GUIApplication
        telemetry = app.get_telemetry()
        assert telemetry["queries"]["total"] >= 3
        assert telemetry["queries"]["successful"] >= 3
        assert telemetry["queries"]["success_rate_percent"] == 100.0
        assert "p50" in telemetry["latencies_ms"]["rag"]
        assert "p90" in telemetry["latencies_ms"]["rag"]

    def test_e2e_system_health_audit_across_wired_subsystems(
        self, wired_system: dict[str, Any]
    ) -> None:
        """
        Verify that GUIApplication.check_system_health() inspects all connected
        subsystems (AI, Retrieval, Knowledge, Services) and reports HEALTHY.
        """
        app: GUIApplication = wired_system["app"]
        health = app.check_system_health()

        assert isinstance(health, ServiceHealth)
        assert health.status == HealthStatus.HEALTHY
        assert "All monitored subsystems operational" in health.details
        assert "ai" in health.metrics["subsystems"]
