"""
ScholarOS AI Metrics Tracking.

Collects telemetry and performance metrics: latency, token usage, cost, and failures.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass(slots=True)
class AIMetrics:
    """
    Performance and utilization metrics for AI operations.
    """

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    total_latency_ms: float = 0.0
    _start_time: float = field(default_factory=time.time)
    _lock: Lock = field(default_factory=Lock)

    def record_request(
        self,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
        success: bool = True,
    ) -> None:
        """Record an executed AI request."""
        with self._lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1

            self.total_latency_ms += max(0.0, latency_ms)
            self.total_prompt_tokens += max(0, prompt_tokens)
            self.total_completion_tokens += max(0, completion_tokens)
            self.total_cost += max(0.0, cost)

    @property
    def total_tokens(self) -> int:
        """Return total tokens consumed across prompt and completion."""
        return self.total_prompt_tokens + self.total_completion_tokens

    @property
    def average_latency_ms(self) -> float:
        """Return mean request latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def throughput_tokens_per_sec(self) -> float:
        """Calculate token processing throughput per second."""
        elapsed = max(0.001, time.time() - self._start_time)
        return self.total_tokens / elapsed

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation of current metrics."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "throughput_tokens_per_sec": round(self.throughput_tokens_per_sec, 2),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.total_prompt_tokens = 0
            self.total_completion_tokens = 0
            self.total_cost = 0.0
            self.total_latency_ms = 0.0
            self._start_time = time.time()


__all__ = [
    "AIMetrics",
]
