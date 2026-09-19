"""
ScholarOS AI Response Cache.

Provides in-memory caching with TTL expiration for deterministic AI queries.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.ai.request import AIRequest


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float | None


class ResponseCache:
    """
    Thread-safe in-memory cache for AI responses.
    """

    def __init__(self, default_ttl_seconds: float | None = 3600.0, max_entries: int = 1000) -> None:
        self.default_ttl = default_ttl_seconds
        self.max_entries = max_entries
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits: int = 0
        self._misses: int = 0

    def make_key(self, request: AIRequest) -> str:
        """Generate a deterministic MD5 hash key from an AIRequest."""
        data = {
            "model": request.model or "",
            "prompt": request.prompt or "",
            "messages": [m.to_dict() for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stop": request.stop,
        }
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def get(self, key: str) -> Any | None:
        """Retrieve cached response if present and not expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            now = time.time()
            if entry.expires_at is not None and now > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        """Store a value in cache with optional TTL."""
        with self._lock:
            # Evict if capacity reached
            if len(self._cache) >= self.max_entries:
                first_key = next(iter(self._cache))
                del self._cache[first_key]

            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            expires_at = (time.time() + ttl) if ttl is not None else None
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)


__all__ = [
    "ResponseCache",
]
