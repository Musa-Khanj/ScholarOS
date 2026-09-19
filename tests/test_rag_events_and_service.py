"""
Unit tests for ScholarOS RAG Events, Diagnostics, and RAGService (Milestone 10E).
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse
from scholaros.events.bus import EventBus
from scholaros.knowledge.rag.configuration import RAGConfiguration
from scholaros.knowledge.rag.events import (
    RAGCompleted,
    RAGEvent,
    RAGFailed,
    RAGFallbackTriggered,
    RAGStarted,
)
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.knowledge.rag.service import RAGService
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult
from scholaros.services.health import HealthStatus


class DummyLLM(LLM):
    def __init__(self, answer: str = "Mock answer") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "dummy-model"

    def generate(self, messages: list[Message] | str, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )


class TestRAGEvents:
    """Test event emission through RAGPipeline execution."""

    def test_events_published_on_successful_run(self) -> None:
        event_bus = EventBus()
        events_received: list[RAGEvent] = []

        event_bus.subscribe("RAGStarted", lambda e: events_received.append(e))
        event_bus.subscribe("RAGCompleted", lambda e: events_received.append(e))

        retriever = MagicMock()
        retriever.search.return_value = [
            RetrievalResult(content="ScholarOS architecture", score=0.9, source="arch-doc")
        ]
        mock_retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM("Architecture explained.")

        pipeline = RAGPipeline(
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
            event_bus=event_bus,
        )

        req = RAGRequest(query="What is ScholarOS?")
        response = pipeline.run(req)

        assert response.content == "Architecture explained."
        assert len(events_received) == 2
        assert isinstance(events_received[0], RAGStarted)
        assert events_received[0].payload["query"] == "What is ScholarOS?"
        assert isinstance(events_received[1], RAGCompleted)
        assert events_received[1].payload["model"] == "dummy-model"
        assert events_received[1].payload["results_count"] == 1

    def test_events_published_on_fallback(self) -> None:
        event_bus = EventBus()
        events_received: list[RAGEvent] = []

        event_bus.subscribe("RAGStarted", lambda e: events_received.append(e))
        event_bus.subscribe("RAGFallbackTriggered", lambda e: events_received.append(e))
        event_bus.subscribe("RAGCompleted", lambda e: events_received.append(e))

        retriever = MagicMock()
        retriever.search.return_value = []
        mock_retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM()

        pipeline = RAGPipeline(
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
            fallback_on_empty=True,
            empty_fallback_message="No facts available.",
            event_bus=event_bus,
        )

        req = RAGRequest(query="Quantum computation")
        response = pipeline.run(req)

        assert response.content == "No facts available."
        assert response.model == "fallback"
        assert len(events_received) == 3
        assert isinstance(events_received[0], RAGStarted)
        assert isinstance(events_received[1], RAGFallbackTriggered)
        assert isinstance(events_received[2], RAGCompleted)
        assert events_received[2].payload["model"] == "fallback"
        assert events_received[2].payload["results_count"] == 0

    def test_events_published_on_failure(self) -> None:
        event_bus = EventBus()
        failed_events: list[RAGFailed] = []
        event_bus.subscribe("RAGFailed", lambda e: failed_events.append(e))

        retriever = MagicMock()
        retriever.search.side_effect = RuntimeError("Storage connection failed")
        mock_retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM()

        pipeline = RAGPipeline(
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
            event_bus=event_bus,
        )

        with pytest.raises(RuntimeError, match="Storage connection failed"):
            pipeline.run(RAGRequest(query="Test query"))

        assert len(failed_events) == 1
        assert failed_events[0].payload["query"] == "Test query"
        assert "Storage connection failed" in failed_events[0].payload["error"]


class TestRAGService:
    """Test RAGService lifecycle, health status, and convenience execution."""

    def test_rag_service_initialization_and_health(self) -> None:
        retriever = MagicMock()
        retriever.search.return_value = []
        mock_retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM("Answer from LLM")
        config = RAGConfiguration(default_strategy="semantic", default_limit=5)

        service = RAGService(
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
            config=config,
        )

        assert service.name == "RAGService"
        assert service.config.default_strategy == "semantic"
        assert service.config.default_limit == 5

        health = service.health()
        assert health.status == HealthStatus.HEALTHY
        assert health.is_healthy
        assert health.metrics["has_pipeline"] is True
        assert health.metrics["has_llm"] is True
        assert health.metrics["has_retrieval"] is True

    def test_rag_service_ask_and_generate(self) -> None:
        retriever = MagicMock()
        retriever.search.return_value = [
            RetrievalResult(content="Doc about AI", score=0.95, source="ai-doc")
        ]
        retriever.retrieve.return_value = [
            RetrievalResult(content="Doc about AI", score=0.95, source="ai-doc")
        ]
        mock_retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM("AI is the study of intelligent agents.")

        service = RAGService(
            retrieval_pipeline=mock_retrieval_pipeline,
            llm=llm,
        )

        # Convenience method .ask()
        answer = service.ask("What is AI?")
        assert answer == "AI is the study of intelligent agents."

        # Convenience method .generate()
        resp = service.generate("What is AI?")
        assert isinstance(resp, RAGResponse)
        assert resp.content == "AI is the study of intelligent agents."
        assert resp.has_context is True
        assert resp.diagnostics["results_count"] == 1
