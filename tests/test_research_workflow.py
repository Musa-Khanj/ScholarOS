"""
Integration tests for ScholarOS Research Workflow, Planner, and Execution (Milestone 10G).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.execution.workflow_executor import WorkflowExecutor
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.memory.manager import MemoryManager
from scholaros.memory.registry import MemoryRegistry
from scholaros.planner.research_planner import ResearchPlanner
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.report import Report
from scholaros.research.result import ResearchResult
from scholaros.research.workflow_engine import ResearchWorkflowEngine
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult
from scholaros.services.builtin.research import ResearchService
from scholaros.workflow.state import WorkflowStatus


class DummyWorkflowLLM(LLM):
    def __init__(self, answer: str = "Synthesized multi-stage research findings.") -> None:
        self._answer = answer

    @property
    def model(self) -> str:
        return "dummy-workflow-model"

    def generate(self, messages: Any, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            content=self._answer,
            model=self.model,
            prompt_tokens=20,
            completion_tokens=15,
            total_tokens=35,
        )


@pytest.fixture
def rag_service() -> RAGService:
    retriever = MagicMock()
    results = [
        RetrievalResult(
            content="Transformers utilize self-attention mechanisms for sequence modeling.",
            score=0.92,
            source="vaswani-2017",
            chunk_id="chunk-1",
        ),
        RetrievalResult(
            content="BERT uses bidirectional representations from transformers.",
            score=0.88,
            source="devlin-2018",
            chunk_id="chunk-2",
        ),
    ]
    retriever.search.return_value = results
    retriever.retrieve.return_value = results
    retrieval_pipeline = RetrievalPipeline(retriever=retriever)
    llm = DummyWorkflowLLM()
    rag_pipeline = RAGPipeline(retrieval_pipeline=retrieval_pipeline, llm=llm)
    return RAGService(pipeline=rag_pipeline)


@pytest.fixture
def memory_manager() -> MemoryManager:
    return MemoryManager(registry=MemoryRegistry())


class TestResearchWorkflow:
    """Tests for ResearchWorkflowEngine and end-to-end multi-stage research workflows."""

    def test_workflow_engine_full_execution(
        self, rag_service: RAGService, memory_manager: MemoryManager
    ) -> None:
        event_bus = EventBus()
        events = []
        event_bus.subscribe("*", lambda e: events.append(e))

        engine = ResearchWorkflowEngine(
            rag=rag_service,
            memory=memory_manager,
            event_bus=event_bus,
        )

        result = engine.execute(
            query="Transformers in NLP",
            strategy="hybrid",
            limit_per_query=3,
        )

        # 1. Result content and status
        assert isinstance(result, ResearchResult)
        assert result.has_content()
        assert "Synthesized multi-stage research findings." in result.content
        assert result.has_workflow

        # 2. Workflow context and steps
        ctx = result.workflow_context
        assert ctx is not None
        assert ctx.status == WorkflowStatus.COMPLETED
        step_names = [s.name for s in ctx.steps]
        assert "planning" in step_names
        assert "retrieval" in step_names
        assert "analysis" in step_names
        assert "synthesis" in step_names
        for s in ctx.steps:
            assert s.status == WorkflowStatus.COMPLETED
            assert s.duration_ms >= 0.0

        # 3. Plan inspection
        plan = result.plan
        assert plan is not None
        assert plan.query == "Transformers in NLP"
        assert len(plan.sub_questions) >= 3

        # 4. Report and citations
        report = result.report
        assert report is not None
        assert isinstance(report, Report)
        assert "Transformers in NLP" in report.title
        assert len(report.citations) >= 1

        # 5. Memory recording
        history_col = memory_manager.get("research_history")
        assert history_col is not None
        assert len(history_col) == 1

        # 6. Event verification
        event_names = [e.name for e in events]
        assert "ResearchStarted" in event_names
        assert "ResearchStageStarted" in event_names
        assert "ResearchStageCompleted" in event_names
        assert "ResearchCompleted" in event_names

    def test_workflow_engine_cancellation(self, rag_service: RAGService) -> None:
        event_bus = EventBus()
        events = []
        event_bus.subscribe("*", lambda e: events.append(e))

        engine = ResearchWorkflowEngine(
            rag=rag_service,
            event_bus=event_bus,
        )

        real_execute_stage = engine.executor.execute_stage

        def hook(stage_name: str, stage_fn: Any, ctx: Any) -> Any:
            if stage_name == "retrieval":
                ctx.cancel("Aborted by user")
            return real_execute_stage(stage_name, stage_fn, ctx)

        engine.executor.execute_stage = hook  # type: ignore[method-assign]


        result = engine.execute(query="Interrupted Research")
        assert result.workflow_context is not None
        assert result.workflow_context.is_cancelled
        assert result.workflow_context.status == WorkflowStatus.CANCELLED
        assert "[Workflow Cancelled]" in result.content
        assert any(e.name == "ResearchCancelled" for e in events)

    def test_pipeline_execute_workflow(self, rag_service: RAGService) -> None:
        pipeline = ResearchPipeline.from_rag(rag_service)
        result = pipeline.execute_workflow(
            query="Self-attention mechanisms",
            limit_per_query=2,
        )
        assert isinstance(result, ResearchResult)
        assert result.has_workflow
        assert result.workflow_context.status == WorkflowStatus.COMPLETED
        assert result.report is not None

    def test_agent_run_workflow(self, rag_service: RAGService) -> None:
        agent = ResearchAgent.from_rag(rag_service)
        result = agent.run_workflow("Bidirectional Transformers")
        assert isinstance(result, ResearchResult)
        assert result.has_workflow
        assert len(result.steps) == 4
        assert result.report is not None

    def test_service_run_workflow_and_di_container(
        self, rag_service: RAGService, memory_manager: MemoryManager
    ) -> None:
        container = Container()
        pipeline = ResearchPipeline.from_rag(rag_service)
        service = ResearchService.configure_container(container=container, pipeline=pipeline)

        # Verify service can run workflow
        result = service.run_workflow("Vision Transformers")
        assert isinstance(result, ResearchResult)
        assert result.has_workflow

        # Verify DI resolution
        resolved_service = container.resolve(ResearchService)
        assert resolved_service is service
        resolved_engine = container.resolve(ResearchWorkflowEngine)
        assert resolved_engine is not None
        resolved_planner = container.resolve(ResearchPlanner)
        assert resolved_planner is not None
        resolved_executor = container.resolve(WorkflowExecutor)
        assert resolved_executor is not None
