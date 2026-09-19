"""
Integration tests for ScholarOS ResearchService and DI Container Wiring (Milestone 10F).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.container.container import Container
from scholaros.knowledge.rag.service import RAGService
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.result import ResearchResult
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult
from scholaros.services.builtin.research import ResearchService
from scholaros.services.health import HealthStatus


class DummyLLM(LLM):
    @property
    def model(self) -> str:
        return "dummy-10f"

    def generate(self, messages: Any, **kwargs: Any) -> LLMResponse:
        return LLMResponse(content="Integrated research output", model=self.model)


class TestResearchContainerWiring:
    """Test ResearchService, ResearchPipeline, and ResearchAgent DI wiring."""

    def test_research_service_container_wiring_with_rag(self) -> None:
        container = Container()

        # Wire RAGService first
        retriever = MagicMock()
        r_list = [
            RetrievalResult(content="Academic knowledge", score=0.91, source="source-1")
        ]
        retriever.search.return_value = r_list
        retriever.retrieve.return_value = r_list
        retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyLLM()
        _ = RAGService.configure_container(
            container=container,
            retrieval_pipeline=retrieval_pipeline,
            llm=llm,
        )

        # Wire ResearchService into container (it should resolve RAGService automatically)
        research_service = ResearchService.configure_container(container=container)

        # Validate resolution
        resolved_service = container.resolve(ResearchService)
        assert resolved_service is research_service

        resolved_pipeline = container.resolve(ResearchPipeline)
        assert resolved_pipeline is research_service.pipeline
        assert resolved_pipeline.has_rag is True

        resolved_agent = container.resolve(ResearchAgent)
        assert resolved_agent is research_service.agent

        # Validate health
        health = research_service.health()
        assert health.status == HealthStatus.HEALTHY
        assert health.metrics["has_pipeline"] is True
        assert health.metrics["has_rag"] is True

        # Execute research through resolved service and agent
        result = research_service.research("Explain topic")
        assert isinstance(result, ResearchResult)
        assert result.content == "Integrated research output"
        assert result.sources == ("source-1",)

        agent_result = resolved_agent.research("Explain agent research")
        assert agent_result.content == "Integrated research output"
