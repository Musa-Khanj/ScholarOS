"""
ScholarOS Observability - Diagnostics Registry.

Stores execution traces in an in-memory bounded ring buffer for quick inspection,
error diagnosis, and operational auditing.
"""

from __future__ import annotations

from collections import deque
from threading import Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scholaros.observability.trace import RAGTrace


class DiagnosticsRegistry:
    """
    Bounded thread-safe ring-buffer registry for execution traces.
    """

    _default_instance: DiagnosticsRegistry | None = None
    _default_lock: Lock = Lock()

    def __init__(self, capacity: int = 100) -> None:
        if capacity <= 0:
            raise ValueError(f"Capacity must be positive, got {capacity}")
        self._capacity = capacity
        self._traces: deque[RAGTrace] = deque(maxlen=capacity)
        self._by_id: dict[str, RAGTrace] = {}
        self._lock = Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        with self._lock:
            return len(self._traces)

    def record(self, trace: RAGTrace) -> None:
        """Record an execution trace into the ring buffer."""
        with self._lock:
            # If at capacity and oldest element will be evicted, remove from index
            if len(self._traces) == self._capacity and self._traces:
                evicted = self._traces[0]
                self._by_id.pop(evicted.trace_id, None)

            self._traces.append(trace)
            self._by_id[trace.trace_id] = trace

    def get(self, trace_id: str) -> RAGTrace | None:
        """Retrieve trace by unique identifier."""
        with self._lock:
            return self._by_id.get(trace_id)

    def get_recent(self, limit: int = 10) -> list[RAGTrace]:
        """Return the most recent traces in reverse chronological order."""
        with self._lock:
            recent = list(self._traces)
            recent.reverse()
            return recent[:limit]

    def find(
        self,
        query: str | None = None,
        failed_only: bool = False,
        strategy: str | None = None,
        limit: int = 20,
    ) -> list[RAGTrace]:
        """Search traces by query substring, failure status, or strategy."""
        with self._lock:
            matches: list[RAGTrace] = []
            for t in reversed(self._traces):
                if failed_only and t.is_success:
                    continue
                if strategy and t.strategy != strategy:
                    continue
                if query and query.lower() not in t.query.lower():
                    continue
                matches.append(t)
                if len(matches) >= limit:
                    break
            return matches

    def clear(self) -> None:
        """Clear all stored traces."""
        with self._lock:
            self._traces.clear()
            self._by_id.clear()

    @classmethod
    def get_default(cls, capacity: int = 100) -> DiagnosticsRegistry:
        """Obtain the process-wide default diagnostics registry."""
        with cls._default_lock:
            if cls._default_instance is None:
                cls._default_instance = cls(capacity=capacity)
            return cls._default_instance

    @classmethod
    def reset_default(cls) -> None:
        """Reset the default registry instance."""
        with cls._default_lock:
            cls._default_instance = None


__all__ = [
    "DiagnosticsRegistry",
]
