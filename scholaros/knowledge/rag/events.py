"""
ScholarOS RAG Events.

Defines events emitted by the RAG subsystem into the EventBus.
"""

from __future__ import annotations

from typing import Any

from scholaros.events.event import Event


class RAGEvent(Event):
    """Base event for RAG subsystem occurrences."""

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


class RAGStarted(RAGEvent):
    """Emitted when a RAG pipeline execution begins."""

    def __init__(
        self,
        query: str,
        strategy: str = "default",
        limit: int | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "limit": limit,
                "max_tokens": max_tokens,
            },
            **kwargs,
        )


class RAGCompleted(RAGEvent):
    """Emitted when a RAG pipeline execution successfully completes."""

    def __init__(
        self,
        query: str,
        strategy: str,
        model: str,
        results_count: int,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "model": model,
                "results_count": results_count,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class RAGFailed(RAGEvent):
    """Emitted when a RAG pipeline execution fails."""

    def __init__(
        self,
        query: str,
        strategy: str,
        error: str,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "error": error,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class RAGFallbackTriggered(RAGEvent):
    """Emitted when empty-context fallback is triggered."""

    def __init__(
        self,
        query: str,
        reason: str = "empty_context",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "reason": reason,
            },
            **kwargs,
        )


__all__ = [
    "RAGCompleted",
    "RAGEvent",
    "RAGFailed",
    "RAGFallbackTriggered",
    "RAGStarted",
]
