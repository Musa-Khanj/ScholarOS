"""
ScholarOS Retrieval Metrics.

Records and calculates operational metrics for retrieval and reranking operations:
latencies, throughput, failure rates, and strategy distributions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class RetrievalMetrics:
    """
    Thread-safe operational telemetry recorder for the retrieval subsystem.
    """

    query_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    results_returned_total: int = 0
    strategy_counts: dict[str, int] = field(default_factory=dict)
    reranker_counts: dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average retrieval latency in milliseconds."""
        with self._lock:
            if self.success_count == 0:
                return 0.0
            return round(self.total_latency_ms / self.success_count, 2)

    @property
    def error_rate(self) -> float:
        """Calculate failure rate as a fraction between 0.0 and 1.0."""
        with self._lock:
            if self.query_count == 0:
                return 0.0
            return round(self.failure_count / self.query_count, 4)

    def record_query(
        self,
        strategy: str,
        results_count: int,
        latency_ms: float,
        success: bool = True,
    ) -> None:
        """Record a completed or failed retrieval query."""
        with self._lock:
            self.query_count += 1
            strat_key = strategy.lower()
            self.strategy_counts[strat_key] = self.strategy_counts.get(strat_key, 0) + 1

            if success:
                self.success_count += 1
                self.total_latency_ms += latency_ms
                self.results_returned_total += results_count
            else:
                self.failure_count += 1

    def record_rerank(
        self,
        reranker: str,
        latency_ms: float,
    ) -> None:
        """Record a reranking invocation."""
        with self._lock:
            key = reranker.lower()
            self.reranker_counts[key] = self.reranker_counts.get(key, 0) + 1

    def reset(self) -> None:
        """Reset all metrics back to zero."""
        with self._lock:
            self.query_count = 0
            self.success_count = 0
            self.failure_count = 0
            self.total_latency_ms = 0.0
            self.results_returned_total = 0
            self.strategy_counts.clear()
            self.reranker_counts.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        with self._lock:
            return {
                "query_count": self.query_count,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "error_rate": self.error_rate,
                "total_latency_ms": round(self.total_latency_ms, 2),
                "avg_latency_ms": self.avg_latency_ms,
                "results_returned_total": self.results_returned_total,
                "strategy_counts": dict(self.strategy_counts),
                "reranker_counts": dict(self.reranker_counts),
            }


__all__ = [
    "RetrievalMetrics",
]
