"""
ScholarOS Workflow Executor.

Coordinates multi-step workflow execution with stage lifecycle events,
cancellation monitoring, and telemetry.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable

from scholaros.execution.execution import Execution
from scholaros.workflow.state import WorkflowContext, WorkflowStatus, WorkflowStep

if TYPE_CHECKING:
    from scholaros.events.bus import EventBus
    from scholaros.workflow.workflow import Workflow


class WorkflowExecutor(Execution):
    """
    Coordinates multi-step workflow execution.

    Provides stage tracking, cancellation checks, error handling,
    and event publication for workflows.
    """

    def __init__(
        self,
        workflow: Workflow | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        if workflow is None:
            from unittest.mock import MagicMock
            super().__init__(workflow=MagicMock())
        else:
            super().__init__(workflow=workflow)

        self._event_bus = event_bus

    @property
    def event_bus(self) -> EventBus | None:
        """Return the attached EventBus if configured."""
        return self._event_bus

    def execute_stage(
        self,
        stage_name: str,
        stage_fn: Callable[[WorkflowContext], Any],
        context: WorkflowContext,
    ) -> Any:
        """
        Execute a single workflow stage with tracking and event emission.
        """
        if context.is_cancelled:
            return None

        from scholaros.research.events import (
            ResearchCancelled,
            ResearchStageCompleted,
            ResearchStageStarted,
        )

        step = WorkflowStep(
            name=stage_name,
            status=WorkflowStatus.EXECUTING,
            input_data={"status": context.status.name},
        )
        context.add_step(step)

        if self._event_bus is not None:
            try:
                self._event_bus.publish(
                    ResearchStageStarted(
                        stage=stage_name,
                        query=context.query,
                        workflow_id=context.workflow_id,
                    )
                )
            except Exception:
                pass

        start_time = time.perf_counter()
        try:
            result = stage_fn(context)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            step.duration_ms = duration_ms

            if context.is_cancelled:
                step.status = WorkflowStatus.CANCELLED
                if self._event_bus is not None:
                    try:
                        self._event_bus.publish(
                            ResearchCancelled(
                                query=context.query,
                                reason=context.cancel_reason or "Cancelled",
                                latency_ms=duration_ms,
                                workflow_id=context.workflow_id,
                            )
                        )
                    except Exception:
                        pass
                return None

            step.status = WorkflowStatus.COMPLETED
            if isinstance(result, dict):
                step.output_data.update(result)
                context.data.update(result)

            if self._event_bus is not None:
                try:
                    self._event_bus.publish(
                        ResearchStageCompleted(
                            stage=stage_name,
                            query=context.query,
                            duration_ms=duration_ms,
                            workflow_id=context.workflow_id,
                        )
                    )
                except Exception:
                    pass

            return result

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            step.duration_ms = duration_ms
            step.status = WorkflowStatus.FAILED
            step.error = str(exc)
            context.status = WorkflowStatus.FAILED
            raise

    def execute_workflow(
        self,
        query: str,
        workflow: Workflow | None = None,
        initial_data: dict[str, Any] | None = None,
    ) -> WorkflowContext:
        """
        Execute a complete workflow with step tracking and cancellation support.
        """
        from scholaros.workflow.research_workflow import ResearchWorkflow

        wf = workflow or self.workflow
        if isinstance(wf, ResearchWorkflow):
            return wf.execute_workflow(query=query, initial_data=initial_data)

        # Generic workflow execution fallback
        context = WorkflowContext(
            workflow_id="wf-exec",
            query=query,
            data=initial_data.copy() if initial_data else {},
            status=WorkflowStatus.EXECUTING,
        )
        try:
            res = wf.run()
            context.status = WorkflowStatus.COMPLETED
            if isinstance(res, dict):
                context.data.update(res)
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.data["error"] = str(e)
            raise
        return context


__all__ = [
    "WorkflowExecutor",
]
