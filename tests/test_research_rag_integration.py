"""
Integration tests for ScholarOS ResearchAgent and ResearchPipeline RAG integration (Milestone 10F).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from scholaros.agents import ResearchAgent
from scholaros.ai.ai_service import AIService
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.prompt_builder import PromptBuilder
from scholaros.ai.prompt_registry import PromptRegistry, PromptTemplate
from scholaros.ai.prompt_session import PromptSession
from scholaros.ai.response import AIResponse
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.research.exceptions import ResearchExecutionError
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.result import ResearchResult
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult


class DummyResearchLLM(LLM):
    def __init__(self, answer: str = "Research synthesis") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "dummy-research-model"

    def generate(self, messages: Any, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=15,
            completion_tokens=10,
            total_tokens=25,
        )


class TestResearchAgentAndPipelineRAG:
    """Test ResearchPipeline and ResearchAgent with RAG integration and backward compatibility."""

    def test_pipeline_with_rag_service(self) -> None:
        retriever = MagicMock()
        results = [
            RetrievalResult(
                content="Attention mechanisms allow modeling dependencies.",
                score=0.95,
                source="vaswani-2017",
                chunk_id="c_attn",
            )
        ]
        retriever.search.return_value = results
        retriever.retrieve.return_value = results
        retrieval_pipeline = RetrievalPipeline(retriever=retriever)
        llm = DummyResearchLLM("Attention mechanisms form the core of transformers.")
        rag_pipeline = RAGPipeline(retrieval_pipeline=retrieval_pipeline, llm=llm)
        rag_service = RAGService(pipeline=rag_pipeline)

        # Initialize ResearchPipeline with RAGService
        research_pipeline = ResearchPipeline.from_rag(rag_service)

        assert research_pipeline.has_rag is True
        assert research_pipeline.has_ai is False

        # Execute grounded research
        result = research_pipeline.execute_rag("What are attention mechanisms?")
        assert isinstance(result, ResearchResult)
        assert result.content == "Attention mechanisms form the core of transformers."
        assert result.has_context is True
        assert result.sources == ("vaswani-2017",)
        assert len(result.attributions) == 1
        assert result.attributions[0]["chunk_id"] == "c_attn"

    def test_pipeline_dual_ai_and_rag_routing(self) -> None:
        # 1. Setup legacy AIService with prompt template
        registry = PromptRegistry()
        registry.register(PromptTemplate(name="summarize", template="Summary of {topic}"))
        builder = PromptBuilder(registry)
        mock_ai_llm = MagicMock()
        mock_ai_llm.model = "legacy-ai"
        mock_ai_llm.generate.return_value = AIResponse(content="Legacy template summary", model="legacy-ai")
        session = PromptSession(builder, mock_ai_llm)
        ai_service = AIService(session)

        # 2. Setup RAGService
        retriever = MagicMock()
        res_list = [
            RetrievalResult(content="RAG knowledge", score=0.9, source="rag-source")
        ]
        retriever.search.return_value = res_list
        retriever.retrieve.return_value = res_list
        rag_pipeline = RAGPipeline(
            retrieval_pipeline=RetrievalPipeline(retriever=retriever),
            llm=DummyResearchLLM("RAG grounded answer"),
        )
        rag_service = RAGService(pipeline=rag_pipeline)

        # Initialize dual pipeline
        pipeline = ResearchPipeline(ai=ai_service, rag=rag_service)
        assert pipeline.has_ai is True
        assert pipeline.has_rag is True

        # When calling execute with known template -> runs AI template
        legacy_res = pipeline.execute("summarize", topic="Quantum")
        assert legacy_res.content == "Legacy template summary"

        # When calling execute with unknown template -> routes to RAG
        rag_res = pipeline.execute("Explain quantum superposition")
        assert isinstance(rag_res, ResearchResult)
        assert rag_res.content == "RAG grounded answer"
        assert rag_res.sources == ("rag-source",)

    def test_research_agent_with_rag(self) -> None:
        retriever = MagicMock()
        diff_res = [
            RetrievalResult(content="Diffusion models generate images.", score=0.88, source="diff-paper")
        ]
        retriever.search.return_value = diff_res
        retriever.retrieve.return_value = diff_res
        rag_pipeline = RAGPipeline(
            retrieval_pipeline=RetrievalPipeline(retriever=retriever),
            llm=DummyResearchLLM("Diffusion models reverse a noising process."),
        )

        agent = ResearchAgent.from_rag(rag_pipeline)

        assert agent.name == "Research Agent"
        assert agent.pipeline.has_rag is True

        # Using direct .research()
        res1 = agent.research("Explain diffusion models")
        assert res1.content == "Diffusion models reverse a noising process."
        assert res1.sources == ("diff-paper",)

        # Using .execute(query=...)
        res2 = agent.execute(query="Explain diffusion models")
        assert isinstance(res2, ResearchResult)
        assert res2.content == "Diffusion models reverse a noising process."

    def test_pipeline_without_rag_raises_error(self) -> None:
        registry = PromptRegistry()
        builder = PromptBuilder(registry)
        mock_llm = MagicMock()
        session = PromptSession(builder, mock_llm)
        ai_service = AIService(session)

        pipeline = ResearchPipeline(ai=ai_service)

        with pytest.raises(ResearchExecutionError, match="has no RAG service or pipeline configured"):
            pipeline.execute_rag("Some research query")

    def test_pipeline_events_emission(self) -> None:
        from scholaros.events.bus import EventBus
        from scholaros.research.events import ResearchCompleted, ResearchEvent, ResearchStarted

        event_bus = EventBus()
        events_received: list[ResearchEvent] = []
        event_bus.subscribe("ResearchStarted", lambda e: events_received.append(e))
        event_bus.subscribe("ResearchCompleted", lambda e: events_received.append(e))

        retriever = MagicMock()
        ret_res = [RetrievalResult(content="RLHF papers", score=0.92, source="rlhf-paper")]
        retriever.search.return_value = ret_res
        retriever.retrieve.return_value = ret_res

        rag_pipeline = RAGPipeline(
            retrieval_pipeline=RetrievalPipeline(retriever=retriever),
            llm=DummyResearchLLM("RLHF aligns models with human preferences."),
        )

        pipeline = ResearchPipeline.from_rag(rag_pipeline, event_bus=event_bus)
        res = pipeline.execute_rag("Explain RLHF")

        assert res.content == "RLHF aligns models with human preferences."
        assert len(events_received) == 2
        assert isinstance(events_received[0], ResearchStarted)
        assert events_received[0].payload["query"] == "Explain RLHF"
        assert isinstance(events_received[1], ResearchCompleted)
        assert events_received[1].payload["sources_count"] == 1
