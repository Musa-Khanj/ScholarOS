"""
ScholarOS Research Events.

Defines events emitted by the Research subsystem into the EventBus.
"""

from __future__ import annotations

from typing import Any

from scholaros.events.event import Event


class ResearchEvent(Event):
    """Base event for research subsystem occurrences."""

    def __init__(
        self,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name or self.__class__.__name__,
            payload=payload if payload is not None else {},
            metadata=metadata if metadata is not None else {},
            **kwargs,
        )


class ResearchStarted(ResearchEvent):
    """Emitted when a research task begins."""

    def __init__(
        self,
        query: str,
        strategy: str = "default",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
            },
            **kwargs,
        )


class ResearchCompleted(ResearchEvent):
    """Emitted when a research task successfully completes."""

    def __init__(
        self,
        query: str,
        model: str,
        sources_count: int,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "model": model,
                "sources_count": sources_count,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class ResearchFailed(ResearchEvent):
    """Emitted when a research task fails."""

    def __init__(
        self,
        query: str,
        error: str,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "error": error,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class ResearchStageStarted(ResearchEvent):
    """Emitted when a workflow stage starts execution."""

    def __init__(
        self,
        stage: str,
        query: str = "",
        workflow_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "stage": stage,
                "query": query,
                "workflow_id": workflow_id,
            },
            **kwargs,
        )


class ResearchStageCompleted(ResearchEvent):
    """Emitted when a workflow stage finishes execution."""

    def __init__(
        self,
        stage: str,
        query: str = "",
        duration_ms: float = 0.0,
        workflow_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "stage": stage,
                "query": query,
                "duration_ms": duration_ms,
                "workflow_id": workflow_id,
            },
            **kwargs,
        )


class ResearchCancelled(ResearchEvent):
    """Emitted when a research workflow is cancelled."""

    def __init__(
        self,
        query: str,
        reason: str = "User cancelled",
        latency_ms: float = 0.0,
        workflow_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "reason": reason,
                "latency_ms": latency_ms,
                "workflow_id": workflow_id,
            },
            **kwargs,
        )


__all__ = [
    "ResearchCancelled",
    "ResearchCompleted",
    "ResearchEvent",
    "ResearchFailed",
    "ResearchStageCompleted",
    "ResearchStageStarted",
    "ResearchStarted",
]

