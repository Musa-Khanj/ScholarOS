"""
Tests for ScholarOS Workflow State and Execution.
"""

from __future__ import annotations


import pytest

from scholaros.events.bus import EventBus
from scholaros.execution.workflow_executor import WorkflowExecutor
from scholaros.workflow.state import WorkflowContext, WorkflowStatus, WorkflowStep


class TestWorkflowStatus:
    """Tests for WorkflowStatus enum."""

    def test_status_values_exist(self) -> None:
        assert WorkflowStatus.PENDING is not None
        assert WorkflowStatus.PLANNING is not None
        assert WorkflowStatus.EXECUTING is not None
        assert WorkflowStatus.RETRIEVING is not None
        assert WorkflowStatus.ANALYZING is not None
        assert WorkflowStatus.SYNTHESIZING is not None
        assert WorkflowStatus.COMPLETED is not None
        assert WorkflowStatus.FAILED is not None
        assert WorkflowStatus.CANCELLED is not None

    def test_is_terminal(self) -> None:
        assert not WorkflowStatus.PENDING.is_terminal
        assert not WorkflowStatus.PLANNING.is_terminal
        assert not WorkflowStatus.EXECUTING.is_terminal
        assert not WorkflowStatus.RETRIEVING.is_terminal
        assert not WorkflowStatus.ANALYZING.is_terminal
        assert not WorkflowStatus.SYNTHESIZING.is_terminal

        assert WorkflowStatus.COMPLETED.is_terminal
        assert WorkflowStatus.FAILED.is_terminal
        assert WorkflowStatus.CANCELLED.is_terminal


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_step_defaults(self) -> None:
        step = WorkflowStep(name="test_step")
        assert step.name == "test_step"
        assert step.status == WorkflowStatus.PENDING
        assert step.input_data == {}
        assert step.output_data == {}
        assert step.error is None
        assert step.duration_ms == 0.0

    def test_step_custom_attributes(self) -> None:
        step = WorkflowStep(
            name="retrieval",
            status=WorkflowStatus.COMPLETED,
            input_data={"query": "test"},
            output_data={"docs": 3},
            duration_ms=45.2,
        )
        assert step.name == "retrieval"
        assert step.status == WorkflowStatus.COMPLETED
        assert step.input_data["query"] == "test"
        assert step.output_data["docs"] == 3
        assert step.duration_ms == 45.2


class TestWorkflowContext:
    """Tests for WorkflowContext."""

    def test_context_initialization(self) -> None:
        ctx = WorkflowContext(
            workflow_id="wf-123",
            query="Deep learning architectures",
            data={"initial": True},
        )
        assert ctx.workflow_id == "wf-123"
        assert ctx.query == "Deep learning architectures"
        assert ctx.data == {"initial": True}
        assert ctx.status == WorkflowStatus.PENDING
        assert not ctx.is_cancelled
        assert ctx.cancel_reason is None
        assert len(ctx.steps) == 0
        assert ctx.get_elapsed_ms() >= 0.0

    def test_context_cancellation(self) -> None:
        ctx = WorkflowContext(workflow_id="wf-1", query="test")
        assert not ctx.is_cancelled
        ctx.cancel("Timeout exceeded")
        assert ctx.is_cancelled
        assert ctx.cancel_reason == "Timeout exceeded"
        assert ctx.status == WorkflowStatus.CANCELLED

    def test_context_add_step(self) -> None:
        ctx = WorkflowContext(workflow_id="wf-1", query="test")
        step = WorkflowStep(name="step_1")
        ctx.add_step(step)
        assert len(ctx.steps) == 1
        assert ctx.steps[0].name == "step_1"


class TestWorkflowExecutor:
    """Tests for WorkflowExecutor."""

    def test_executor_initialization(self) -> None:
        executor = WorkflowExecutor()
        assert executor is not None
        assert executor.event_bus is None

    def test_execute_stage_success(self) -> None:
        bus = EventBus()
        events_received = []
        bus.subscribe("*", lambda e: events_received.append(e))

        executor = WorkflowExecutor(event_bus=bus)
        ctx = WorkflowContext(workflow_id="wf-test", query="Transformers")

        def sample_stage(c: WorkflowContext) -> dict[str, str]:
            return {"key": "value"}

        result = executor.execute_stage("my_stage", sample_stage, ctx)
        assert result == {"key": "value"}
        assert ctx.data["key"] == "value"
        assert len(ctx.steps) == 1
        assert ctx.steps[0].name == "my_stage"
        assert ctx.steps[0].status == WorkflowStatus.COMPLETED
        assert ctx.steps[0].duration_ms >= 0.0

        # Verify events emitted
        event_names = [e.name for e in events_received]
        assert "ResearchStageStarted" in event_names
        assert "ResearchStageCompleted" in event_names

    def test_execute_stage_cancellation_before(self) -> None:
        executor = WorkflowExecutor()
        ctx = WorkflowContext(workflow_id="wf-test", query="Test")
        ctx.cancel("User cancelled")

        stage_called = False

        def sample_stage(c: WorkflowContext) -> dict[str, str]:
            nonlocal stage_called
            stage_called = True
            return {}

        result = executor.execute_stage("stage", sample_stage, ctx)
        assert result is None
        assert not stage_called

    def test_execute_stage_cancellation_during(self) -> None:
        bus = EventBus()
        events = []
        bus.subscribe("*", lambda e: events.append(e))

        executor = WorkflowExecutor(event_bus=bus)
        ctx = WorkflowContext(workflow_id="wf-test", query="Test")

        def cancelling_stage(c: WorkflowContext) -> dict[str, str]:
            c.cancel("Aborted during stage")
            return {"ignored": "data"}

        result = executor.execute_stage("cancelling_stage", cancelling_stage, ctx)
        assert result is None
        assert ctx.steps[0].status == WorkflowStatus.CANCELLED
        assert any(e.name == "ResearchCancelled" for e in events)

    def test_execute_stage_failure(self) -> None:
        executor = WorkflowExecutor()
        ctx = WorkflowContext(workflow_id="wf-test", query="Test")

        def failing_stage(c: WorkflowContext) -> dict[str, str]:
            raise ValueError("Something broke")

        with pytest.raises(ValueError, match="Something broke"):
            executor.execute_stage("failing_stage", failing_stage, ctx)

        assert ctx.status == WorkflowStatus.FAILED
        assert ctx.steps[0].status == WorkflowStatus.FAILED
        assert "Something broke" in (ctx.steps[0].error or "")
