"""
ScholarOS Retrieval Query Cache.

Provides a thread-safe, high-speed LRU / TTL cache for retrieval query results
and constructed contexts, reducing repeated query latency to sub-millisecond levels.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import json
from threading import RLock
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.retrieval.context import RetrievalContext
    from scholaros.retrieval.query import RetrievalQuery
    from scholaros.retrieval.result import RetrievalResult


@dataclass(slots=True)
class CachedRetrievalItem:
    """Stores cached ranked retrieval results and optional context."""

    results: list[RetrievalResult]
    context: RetrievalContext | None
    created_at: float
    expires_at: float | None


class RetrievalCache:
    """
    Thread-safe LRU & TTL cache for RetrievalPipeline results.
    """

    def __init__(
        self,
        max_size: int = 500,
        default_ttl: float | None = 600.0,
    ) -> None:
        self.max_size = max(1, max_size)
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CachedRetrievalItem] = OrderedDict()
        self._lock = RLock()
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0

    @property
    def hits(self) -> int:
        with self._lock:
            return self._hits

    @property
    def misses(self) -> int:
        with self._lock:
            return self._misses

    @property
    def evictions(self) -> int:
        with self._lock:
            return self._evictions

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def hit_ratio(self) -> float:
        with self._lock:
            total = self._hits + self._misses
            if total == 0:
                return 0.0
            return round(self._hits / total, 4)

    def make_key(
        self,
        query: RetrievalQuery | str,
        build_context: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Create a deterministic hash key from query parameters."""
        if isinstance(query, str):
            q_text = query.strip()
            q_limit = 5
            q_min_score = 0.0
            q_filter: dict[str, Any] = {}
        else:
            q_text = query.text.strip()
            q_limit = query.limit
            q_min_score = getattr(query, "min_score", getattr(query, "minimum_score", 0.0))
            q_filter = getattr(query, "filters", getattr(query, "metadata_filter", {})) or {}

        payload = {
            "text": q_text.lower(),
            "limit": q_limit,
            "min_score": q_min_score,
            "filter": sorted(q_filter.items()) if q_filter else [],
            "build_context": build_context,
            "extra": sorted((extra or {}).items()),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def get(
        self,
        key: str,
    ) -> tuple[list[RetrievalResult], RetrievalContext | None] | None:
        """Retrieve cached results if present and not expired."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            now = time.time()
            if entry.expires_at is not None and now > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end for LRU
            self._cache.move_to_end(key)
            self._hits += 1
            return list(entry.results), entry.context

    def set(
        self,
        key: str,
        results: list[RetrievalResult],
        context: RetrievalContext | None = None,
        ttl: float | None = None,
    ) -> None:
        """Store results and optional context in the cache."""
        with self._lock:
            now = time.time()
            effective_ttl = ttl if ttl is not None else self.default_ttl
            expires_at = (now + effective_ttl) if effective_ttl is not None else None

            # Evict LRU item if at max capacity and inserting new key
            if key not in self._cache and len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
                self._evictions += 1

            self._cache[key] = CachedRetrievalItem(
                results=list(results),
                context=context,
                created_at=now,
                expires_at=expires_at,
            )
            self._cache.move_to_end(key)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def stats(self) -> dict[str, Any]:
        """Return cache health and performance statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_ratio": self.hit_ratio,
            }

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"RetrievalCache(size={self.size}/{self.max_size}, hits={self.hits}, misses={self.misses})"


__all__ = [
    "CachedRetrievalItem",
    "RetrievalCache",
]
