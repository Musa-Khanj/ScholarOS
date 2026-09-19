"""
ScholarOS Observability - Telemetry & Metrics.

Tracks runtime performance metrics, latency percentiles (p50, p90, p99) across
retrieval, RAG, and LLM generation, as well as token consumption statistics.
"""

from __future__ import annotations

from collections import deque
import math
from threading import Lock
from typing import Any


def _calculate_percentile(data: list[float], p: float) -> float:
    """Calculate the p-th percentile of a list of floats (0 <= p <= 100)."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1


class TelemetryCollector:
    """
    Thread-safe collector for runtime operational metrics and latency percentiles.
    """

    _default_instance: TelemetryCollector | None = None
    _default_lock: Lock = Lock()

    def __init__(self, sample_window: int = 1000) -> None:
        self._sample_window = sample_window
        self._lock = Lock()

        # Query counters
        self._total_queries: int = 0
        self._successful_queries: int = 0
        self._failed_queries: int = 0
        self._fallback_queries: int = 0

        # Latency samples (bounded deque for percentile estimation)
        self._rag_latencies: deque[float] = deque(maxlen=sample_window)
        self._retrieval_latencies: deque[float] = deque(maxlen=sample_window)
        self._llm_latencies: deque[float] = deque(maxlen=sample_window)

        # Token counters
        self._total_prompt_tokens: int = 0
        self._total_completion_tokens: int = 0

    def record_query(
        self,
        latency_ms: float,
        retrieval_ms: float = 0.0,
        llm_ms: float = 0.0,
        success: bool = True,
        fallback: bool = False,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Record an executed query with timing and token usage."""
        with self._lock:
            self._total_queries += 1
            if success:
                self._successful_queries += 1
            else:
                self._failed_queries += 1

            if fallback:
                self._fallback_queries += 1

            if latency_ms >= 0:
                self._rag_latencies.append(latency_ms)
            if retrieval_ms > 0:
                self._retrieval_latencies.append(retrieval_ms)
            if llm_ms > 0:
                self._llm_latencies.append(llm_ms)

            self._total_prompt_tokens += max(0, prompt_tokens)
            self._total_completion_tokens += max(0, completion_tokens)

    def snapshot(self) -> dict[str, Any]:
        """Return a point-in-time dictionary of current operational metrics."""
        with self._lock:
            rag_list = list(self._rag_latencies)
            ret_list = list(self._retrieval_latencies)
            llm_list = list(self._llm_latencies)

            avg_rag = sum(rag_list) / len(rag_list) if rag_list else 0.0
            avg_ret = sum(ret_list) / len(ret_list) if ret_list else 0.0
            avg_llm = sum(llm_list) / len(llm_list) if llm_list else 0.0

            total_tokens = self._total_prompt_tokens + self._total_completion_tokens
            avg_tokens = (
                total_tokens / self._total_queries if self._total_queries > 0 else 0.0
            )

            success_rate = (
                (self._successful_queries / self._total_queries) * 100.0
                if self._total_queries > 0
                else 100.0
            )

            return {
                "queries": {
                    "total": self._total_queries,
                    "successful": self._successful_queries,
                    "failed": self._failed_queries,
                    "fallback": self._fallback_queries,
                    "success_rate_percent": round(success_rate, 2),
                },
                "latencies_ms": {
                    "rag": {
                        "avg": round(avg_rag, 2),
                        "p50": round(_calculate_percentile(rag_list, 50), 2),
                        "p90": round(_calculate_percentile(rag_list, 90), 2),
                        "p99": round(_calculate_percentile(rag_list, 99), 2),
                    },
                    "retrieval": {
                        "avg": round(avg_ret, 2),
                        "p50": round(_calculate_percentile(ret_list, 50), 2),
                        "p90": round(_calculate_percentile(ret_list, 90), 2),
                        "p99": round(_calculate_percentile(ret_list, 99), 2),
                    },
                    "llm": {
                        "avg": round(avg_llm, 2),
                        "p50": round(_calculate_percentile(llm_list, 50), 2),
                        "p90": round(_calculate_percentile(llm_list, 90), 2),
                        "p99": round(_calculate_percentile(llm_list, 99), 2),
                    },
                },
                "tokens": {
                    "prompt_tokens": self._total_prompt_tokens,
                    "completion_tokens": self._total_completion_tokens,
                    "total_tokens": total_tokens,
                    "avg_tokens_per_query": round(avg_tokens, 1),
                },
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._total_queries = 0
            self._successful_queries = 0
            self._failed_queries = 0
            self._fallback_queries = 0
            self._rag_latencies.clear()
            self._retrieval_latencies.clear()
            self._llm_latencies.clear()
            self._total_prompt_tokens = 0
            self._total_completion_tokens = 0

    @classmethod
    def get_default(cls) -> TelemetryCollector:
        """Obtain the process-wide default telemetry collector."""
        with cls._default_lock:
            if cls._default_instance is None:
                cls._default_instance = cls()
            return cls._default_instance

    @classmethod
    def reset_default(cls) -> None:
        """Reset the default telemetry collector."""
        with cls._default_lock:
            cls._default_instance = None


__all__ = [
    "TelemetryCollector",
]
