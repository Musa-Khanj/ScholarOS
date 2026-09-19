"""
ScholarOS Workflow State Models.

Defines status enums, step telemetry structures, and cancellation-aware
workflow execution contexts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
import time
from typing import Any


class WorkflowStatus(Enum):
    """Execution status of a workflow or workflow step."""

    PENDING = auto()
    PLANNING = auto()
    EXECUTING = auto()
    RETRIEVING = auto()
    ANALYZING = auto()
    SYNTHESIZING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

    @property
    def is_terminal(self) -> bool:
        """Return True if status represents a completed, failed, or cancelled state."""
        return self in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        )


@dataclass
class WorkflowStep:
    """
    Represents an individual step or stage in a multi-step workflow.
    """

    name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class WorkflowContext:
    """
    Shared execution context across workflow steps.
    Supports intermediate state storage, step history, and cancellation.
    """

    workflow_id: str
    query: str
    data: dict[str, Any] = field(default_factory=dict)
    steps: list[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    _cancelled: bool = False
    _cancel_reason: str | None = None
    start_time: float = field(default_factory=time.perf_counter)

    @property
    def is_cancelled(self) -> bool:
        """Return True if the workflow has been requested to cancel."""
        return self._cancelled

    @property
    def cancel_reason(self) -> str | None:
        """Return the reason for cancellation if cancelled."""
        return self._cancel_reason

    def cancel(self, reason: str = "User requested cancellation") -> None:
        """Signal cancellation for this workflow execution."""
        self._cancelled = True
        self._cancel_reason = reason
        self.status = WorkflowStatus.CANCELLED

    def add_step(self, step: WorkflowStep) -> None:
        """Append a completed or in-progress step to the execution history."""
        self.steps.append(step)

    def get_elapsed_ms(self) -> float:
        """Return total elapsed time since workflow start in milliseconds."""
        return (time.perf_counter() - self.start_time) * 1000.0


__all__ = [
    "WorkflowContext",
    "WorkflowStatus",
    "WorkflowStep",
]
