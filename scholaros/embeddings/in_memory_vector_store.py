"""
ScholarOS
In-Memory Vector Store

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores embeddings
in memory.
"""

from __future__ import annotations

from collections.abc import Sequence
import heapq
from threading import RLock

from scholaros.embeddings.cosine_similarity import (
    CosineSimilarity,
)
from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.similarity_metric import (
    SimilarityMetric,
)
from scholaros.embeddings.vector_store import (
    VectorStore,
)


class InMemoryVectorStore(
    VectorStore,
):
    """
    Stores embeddings in memory with thread safety and optimized top-k search.
    """

    def __init__(
        self,
        metric: SimilarityMetric | None = None,
    ) -> None:
        """
        Initialize the vector store.
        """
        self._embeddings: list[Embedding] = []
        self._metric = (
            metric
            if metric is not None
            else CosineSimilarity()
        )
        self._lock = RLock()

    @property
    def name(self) -> str:
        """Return the vector store name."""
        return "InMemoryVectorStore"

    @property
    def description(self) -> str:
        """Return the vector store description."""
        return "Stores embeddings in memory."

    @property
    def version(self) -> str:
        """Return the vector store version."""
        return "1.0.0"

    @property
    def metric(self) -> SimilarityMetric:
        """Return the similarity metric."""
        return self._metric

    def add(
        self,
        embedding: Embedding,
    ) -> None:
        """Store an embedding with cached norm and reciprocal."""
        with self._lock:
            _ = getattr(embedding, "inv_norm", None)
            self._embeddings.append(embedding)

    def add_batch(
        self,
        embeddings: Sequence[Embedding],
    ) -> None:
        """Store multiple embeddings efficiently in batch."""
        with self._lock:
            for emb in embeddings:
                _ = getattr(emb, "inv_norm", None)
                self._embeddings.append(emb)

    def remove(
        self,
        embedding: Embedding,
    ) -> None:
        """Remove an embedding."""
        with self._lock:
            self._embeddings.remove(embedding)

    def clear(self) -> None:
        """Remove all stored embeddings."""
        with self._lock:
            self._embeddings.clear()

    def embeddings(self) -> list[Embedding]:
        """Return a snapshot of all stored embeddings."""
        with self._lock:
            return list(self._embeddings)

    def __len__(self) -> int:
        """Return the total number of stored embeddings."""
        with self._lock:
            return len(self._embeddings)

    def search(
        self,
        query: Embedding,
        limit: int = 5,
    ) -> list[Embedding]:
        """
        Return the top-k most similar embeddings using O(N log k) priority heap.
        """
        if limit <= 0:
            return []

        with self._lock:
            if not self._embeddings:
                return []

            if isinstance(self._metric, CosineSimilarity):
                q_vec = getattr(query, "_vector", query.vector)
                from operator import mul

                return heapq.nlargest(
                    limit,
                    self._embeddings,
                    key=lambda emb: sum(map(mul, q_vec, getattr(emb, "_vector", emb.vector)))
                    * getattr(emb, "inv_norm", 0.0),
                )

            return heapq.nlargest(
                limit,
                self._embeddings,
                key=lambda emb: self._metric.calculate(query, emb),
            )
