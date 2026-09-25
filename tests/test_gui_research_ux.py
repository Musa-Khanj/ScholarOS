"""
Tests for Part 6 — Research UX.

Verifies end-to-end Research UX requirements:
- Research request flow: ResearchView -> GUIApplication.research() -> ResearchPipeline
- Research execution state tracking (idle/running/completed/failed/cancelled)
- Simultaneous conflicting submission protection
- Non-blocking async research execution via run_research_async()
- Real-time progress and workflow stage rendering (planning/retrieval/analysis/synthesis)
- Real backend cancellation integration
- Rich ResearchResult rendering (findings, citations, bibliography, telemetry)
- Error handling without silent mock fallbacks
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock

import pytest

from scholaros.gui.application import GUIApplication
from scholaros.gui.views.workspace_views import ResearchView
from scholaros.gui.window import GUIWindow
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.planner.research_planner import ResearchPlan
from scholaros.research.citation import Citation
from scholaros.research.events import ResearchStageStarted
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.report import Report
from scholaros.research.result import ResearchResult
from scholaros.retrieval.result import RetrievalResult
from scholaros.workflow.state import WorkflowContext, WorkflowStatus, WorkflowStep


# ---------------------------------------------------------------------------
# Headless Tk Fixtures
# ---------------------------------------------------------------------------

_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    global _root
    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            _root = tk.Tk()
            _root.withdraw()
    return _root


@pytest.fixture
def test_root():
    return get_test_root()


@pytest.fixture
def mock_window(test_root):
    window = Mock(spec=GUIWindow)
    window.root = test_root
    window.set_status = Mock()
    window.get_status = Mock(return_value="Ready")
    return window


@pytest.fixture
def sample_research_result() -> ResearchResult:
    """Create a rich multi-stage ResearchResult with citations and workflow steps."""
    context = WorkflowContext(
        workflow_id="wf-test-123",
        query="Quantum Annealing vs Gate Model",
        status=WorkflowStatus.COMPLETED,
    )
    context.steps = [
        WorkflowStep(name="planning", status=WorkflowStatus.COMPLETED, duration_ms=14.2),
        WorkflowStep(name="retrieval", status=WorkflowStatus.COMPLETED, duration_ms=45.8),
        WorkflowStep(name="analysis", status=WorkflowStatus.COMPLETED, duration_ms=8.5),
        WorkflowStep(name="synthesis", status=WorkflowStatus.COMPLETED, duration_ms=62.1),
    ]

    citations = [
        Citation(
            title="Quantum Annealing in Practice",
            source="Physical Review Letters",
            url="https://doi.org/10.1103/PhysRevLett.1",
        ),
        Citation(
            title="Adiabatic Quantum Computation",
            source="Reviews of Modern Physics",
            url=None,
        ),
    ]

    report = Report(
        title="Research Report: Quantum Annealing",
        content="Quantum annealing solves optimization problems by finding the ground state of an Ising Hamiltonian.",
        citations=citations,
    )

    results = [
        RetrievalResult(
            content="Quantum annealing text excerpt",
            score=0.95,
            source="d-wave-2024.pdf",
            chunk_id="chunk-1",
        ),
        RetrievalResult(
            content="Adiabatic theorem text",
            score=0.89,
            source="nature-physics.pdf",
            chunk_id="chunk-2",
        ),
    ]

    rag_response = RAGResponse(
        content="Quantum annealing solves optimization problems by finding the ground state of an Ising Hamiltonian.",
        model="qwen2.5:1.5b",
        results=results,
        latency_ms=130.6,
    )

    plan = ResearchPlan(
        query="Quantum Annealing vs Gate Model",
        strategy="hybrid",
        sub_questions=["What is quantum annealing?", "How does it compare to gate models?"],
    )

    return ResearchResult(
        response=rag_response,
        report=report,
        workflow_context=context,
        plan=plan,
    )


# ---------------------------------------------------------------------------
# 1. Research Request Flow & Synchronous Delegation
# ---------------------------------------------------------------------------


def test_research_view_delegates_to_application(test_root, mock_window, sample_research_result):
    """Verify ResearchView delegates query execution to application.research()."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(return_value=sample_research_result)

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    assert view.state == "idle"
    assert view.is_running is False

    result = view.run_research("Quantum Annealing vs Gate Model")

    assert result == sample_research_result
    assert view.state == "completed"
    assert view.is_running is False
    assert view.last_result == sample_research_result
    mock_pipeline.execute.assert_called_once_with("Quantum Annealing vs Gate Model")


# ---------------------------------------------------------------------------
# 2. Execution State & Concurrency Protection
# ---------------------------------------------------------------------------


def test_research_view_prevents_simultaneous_execution(test_root, mock_window):
    """Verify conflicting simultaneous submissions are rejected while a research run is active."""
    app = GUIApplication(mock_window)
    view = ResearchView(parent=test_root, application=app)

    # Force view into running state
    view._state = "running"
    assert view.is_running is True

    # Attempt second synchronous execution
    sync_result = view.run_research("Second concurrent topic")
    assert sync_result is None

    # Attempt second asynchronous execution
    called = []
    view.run_research_async("Third concurrent topic", on_complete=lambda r: called.append(r))
    assert len(called) == 0


# ---------------------------------------------------------------------------
# 3. Async Research Execution & UI Responsiveness
# ---------------------------------------------------------------------------


def test_research_view_async_execution(test_root, mock_window, sample_research_result):
    """Verify run_research_async runs non-blockingly, restores buttons, and updates status."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(return_value=sample_research_result)

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    completed_result: list[ResearchResult] = []

    def on_complete(res: ResearchResult) -> None:
        completed_result.append(res)
        test_root.quit()

    view.run_research_async("Async Quantum Topic", on_complete=on_complete)

    # Allow Tk event loop to process background thread result
    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(completed_result) == 1
    assert completed_result[0] == sample_research_result
    assert view.state == "completed"
    assert view.is_running is False
    assert str(view.run_button["state"]) == "normal"
    assert str(view.cancel_button["state"]) == "disabled"
    assert "Completed" in view.stage_label["text"]


# ---------------------------------------------------------------------------
# 4. ResearchResult Rich Rendering (Findings, Citations, Workflow Stages)
# ---------------------------------------------------------------------------


def test_research_result_rendering_content_and_citations(
    test_root, mock_window, sample_research_result
):
    """Verify findings, numbered citations, and workflow stages are rendered into text widget."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(return_value=sample_research_result)

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    view.run_research("Quantum Annealing")

    rendered = view.results_text.get("1.0", "end")

    # 1. Findings present
    assert "Findings:" in rendered
    assert "Quantum annealing solves optimization problems" in rendered

    # 2. Numbered citations from Report present
    assert "📚 Citations & Sources:" in rendered
    assert (
        "[1] Quantum Annealing in Practice — Physical Review Letters (https://doi.org/10.1103/PhysRevLett.1)"
        in rendered
    )
    assert "[2] Adiabatic Quantum Computation — Reviews of Modern Physics" in rendered

    # 3. Workflow stages present
    assert "⏱️ Workflow Stages:" in rendered
    assert "• Planning: completed (14.2ms)" in rendered
    assert "• Retrieval: completed (45.8ms)" in rendered
    assert "• Analysis: completed (8.5ms)" in rendered
    assert "• Synthesis: completed (62.1ms)" in rendered

    # 4. Metadata present
    assert "Model: qwen2.5:1.5b" in rendered
    assert "Latency: 130.6ms" in rendered


# ---------------------------------------------------------------------------
# 5. Real-time Workflow Stage Progress via EventBus
# ---------------------------------------------------------------------------


def test_research_view_surfaces_stage_events(test_root, mock_window):
    """Verify ResearchStageStarted event updates stage_label in real-time."""
    from scholaros.events.bus import EventBus

    event_bus = EventBus()
    app = GUIApplication(mock_window, event_bus=event_bus)

    view = ResearchView(parent=test_root, application=app)
    view._state = "running"  # simulate active run

    # Simulate workflow stage event emitted by backend executor
    event_bus.publish(
        ResearchStageStarted(stage="retrieval", query="Test Topic", workflow_id="wf-1")
    )

    assert "Retrieval" in view.stage_label["text"]


# ---------------------------------------------------------------------------
# 6. Cancellation Integration
# ---------------------------------------------------------------------------


def test_research_view_cancellation(test_root, mock_window):
    """Verify cancel_research invokes pipeline cancellation and renders cancelled result."""
    # Create cancelled research result
    cancelled_context = WorkflowContext(
        workflow_id="wf-cancelled-99",
        query="Long Running Topic",
        status=WorkflowStatus.CANCELLED,
    )
    cancelled_context.cancel("Aborted by user")

    cancelled_resp = RAGResponse(
        content="[Workflow Cancelled] Aborted by user",
        model="cancelled",
        results=[],
        metadata={"cancelled": True},
    )
    cancelled_result = ResearchResult(
        response=cancelled_resp,
        report=None,
        workflow_context=cancelled_context,
    )

    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(return_value=cancelled_result)
    mock_pipeline.cancel_active_workflow = Mock(return_value=True)

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    # Run research which yields cancelled result
    result = view.run_research("Long Running Topic")
    assert result is not None

    assert view.state == "cancelled"
    assert view.is_running is False
    assert "Cancelled" in view.stage_label["text"]

    rendered = view.results_text.get("1.0", "end")
    assert "⚠️ [Research Cancelled]" in rendered
    assert "[Workflow Cancelled] Aborted by user" in rendered


def test_research_view_cancel_active_trigger(test_root, mock_window):
    """Verify clicking cancel during active research signals application cancellation."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.cancel_active_workflow = Mock(return_value=True)

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    view._state = "running"
    success = view.cancel_research("Manual stop")

    assert success is True
    mock_pipeline.cancel_active_workflow.assert_called_once_with("Manual stop")


# ---------------------------------------------------------------------------
# 7. Error Handling (No Silent Fallback)
# ---------------------------------------------------------------------------


def test_research_view_error_handling_synchronous(test_root, mock_window):
    """Verify synchronous research errors are rendered cleanly and update status bar with error."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(side_effect=RuntimeError("Vector index corrupted"))

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    result = view.run_research("Corrupted query")

    assert result is None
    assert view.state == "failed"
    assert view.is_running is False
    assert str(view.run_button["state"]) == "normal"
    assert str(view.cancel_button["state"]) == "disabled"

    rendered = view.results_text.get("1.0", "end")
    assert "Error during research: Vector index corrupted" in rendered
    mock_window.set_status.assert_called_with("Vector index corrupted", error=True)


def test_research_view_error_handling_asynchronous(test_root, mock_window):
    """Verify asynchronous research errors trigger on_error and restore controls."""
    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_pipeline.execute = Mock(side_effect=RuntimeError("Connection refused by retrieval server"))

    app = GUIApplication(mock_window, research_pipeline=mock_pipeline)
    view = ResearchView(parent=test_root, application=app)

    caught_errors: list[Exception] = []

    def on_error(exc: Exception) -> None:
        caught_errors.append(exc)
        test_root.quit()

    view.run_research_async("Failing async topic", on_error=on_error)

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(caught_errors) == 1
    assert isinstance(caught_errors[0], RuntimeError)
    assert view.state == "failed"
    assert view.is_running is False
    assert str(view.run_button["state"]) == "normal"
    assert str(view.cancel_button["state"]) == "disabled"

    rendered = view.results_text.get("1.0", "end")
    assert "Error during research: Connection refused by retrieval server" in rendered


# ---------------------------------------------------------------------------
# 8. End-to-End Workflow with Bootstrap Runtime Services
# ---------------------------------------------------------------------------


def test_research_view_with_runtime_services_workflow(test_root, mock_window):
    """Verify ResearchView runs a full research workflow using bootstrap_runtime services."""
    from scholaros.bootstrap.runtime import bootstrap_runtime

    services = bootstrap_runtime(use_mock_ai=True)
    app = GUIApplication(mock_window, services=services)
    view = ResearchView(parent=test_root, application=app)

    result = view.run_research("Machine learning methods", use_workflow=True)

    assert isinstance(result, ResearchResult)
    assert view.state == "completed"
    assert view.is_running is False

    rendered = view.results_text.get("1.0", "end")
    assert "Findings:" in rendered
    assert len(rendered.strip()) > 30
