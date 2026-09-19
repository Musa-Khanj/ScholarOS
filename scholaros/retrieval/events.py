"""
ScholarOS Retrieval Events.

Defines events emitted by the retrieval subsystem into the EventBus.
"""

from __future__ import annotations

from typing import Any

from scholaros.events.event import Event


class RetrievalEvent(Event):
    """Base event for retrieval subsystem occurrences."""

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


class RetrievalStarted(RetrievalEvent):
    """Emitted when a retrieval query execution begins."""

    def __init__(
        self,
        query: str,
        strategy: str = "default",
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "limit": limit,
            },
            **kwargs,
        )


class RetrievalCompleted(RetrievalEvent):
    """Emitted when a retrieval query successfully returns results."""

    def __init__(
        self,
        query: str,
        strategy: str,
        count: int,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "count": count,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class RetrievalFailed(RetrievalEvent):
    """Emitted when a retrieval query fails."""

    def __init__(
        self,
        query: str,
        strategy: str,
        error: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "strategy": strategy,
                "error": error,
            },
            **kwargs,
        )


class RerankingStarted(RetrievalEvent):
    """Emitted when reranking of candidates begins."""

    def __init__(
        self,
        query: str,
        reranker: str,
        candidate_count: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "reranker": reranker,
                "candidate_count": candidate_count,
            },
            **kwargs,
        )


class RerankingCompleted(RetrievalEvent):
    """Emitted when reranking completes."""

    def __init__(
        self,
        query: str,
        reranker: str,
        output_count: int,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "reranker": reranker,
                "output_count": output_count,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class ContextBuilt(RetrievalEvent):
    """Emitted when a RetrievalContext is constructed for downstream consumers."""

    def __init__(
        self,
        query: str,
        item_count: int,
        total_tokens: int,
        token_budget: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "query": query,
                "item_count": item_count,
                "total_tokens": total_tokens,
                "token_budget": token_budget,
            },
            **kwargs,
        )


__all__ = [
    "RetrievalEvent",
    "RetrievalStarted",
    "RetrievalCompleted",
    "RetrievalFailed",
    "RerankingStarted",
    "RerankingCompleted",
    "ContextBuilt",
]
