"""
ScholarOS Research Workflow.

Coordinates a multi-stage research process (Plan -> Retrieve -> Analyze -> Synthesize).
Maintains backward compatibility with base Workflow.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

from scholaros.workflow.state import WorkflowContext, WorkflowStatus, WorkflowStep
from scholaros.workflow.workflow import Workflow

if TYPE_CHECKING:
    from scholaros.agents import BaseAgent
    from scholaros.events.bus import EventBus


class ResearchWorkflow(Workflow):
    """
    Coordinates multi-step research execution with step tracking and cancellation.
    """

    def __init__(
        self,
        agent: BaseAgent | None = None,
        event_bus: EventBus | None = None,
        stages: list[Callable[[WorkflowContext], Any]] | None = None,
    ) -> None:
        if agent is None:
            # Use dummy or lazy agent if none provided
            from unittest.mock import MagicMock
            super().__init__(agent=MagicMock())
        else:
            super().__init__(agent=agent)

        self._event_bus = event_bus
        self._stages = stages or []

    @property
    def stages(self) -> list[Callable[[WorkflowContext], Any]]:
        """Return the configured pipeline stages."""
        return self._stages

    def add_stage(self, stage: Callable[[WorkflowContext], Any]) -> None:
        """Add an execution stage to the workflow."""
        self._stages.append(stage)

    def execute_workflow(
        self,
        query: str,
        initial_data: dict[str, Any] | None = None,
    ) -> WorkflowContext:
        """
        Execute the configured stages sequentially with step tracking and cancellation checks.
        """
        context = WorkflowContext(
            workflow_id=str(uuid4()),
            query=query,
            data=initial_data.copy() if initial_data else {},
            status=WorkflowStatus.EXECUTING,
        )

        for stage in self._stages:
            if context.is_cancelled:
                break

            stage_name = getattr(stage, "__name__", stage.__class__.__name__)
            step = WorkflowStep(name=stage_name, status=WorkflowStatus.EXECUTING)
            context.add_step(step)

            start_t = time.perf_counter()
            try:
                result = stage(context)
                step.duration_ms = (time.perf_counter() - start_t) * 1000.0
                step.status = WorkflowStatus.COMPLETED
                if isinstance(result, dict):
                    step.output_data.update(result)
                    context.data.update(result)
            except Exception as e:
                step.duration_ms = (time.perf_counter() - start_t) * 1000.0
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
                context.status = WorkflowStatus.FAILED
                raise

        if not context.is_cancelled and context.status != WorkflowStatus.FAILED:
            context.status = WorkflowStatus.COMPLETED

        return context


__all__ = [
    "ResearchWorkflow",
]
