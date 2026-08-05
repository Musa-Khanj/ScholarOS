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
    Stores embeddings
    in memory.
    """

    def __init__(
        self,
        metric: SimilarityMetric | None = None,
    ) -> None:
        """
        Initialize the
        vector store.
        """

        self._embeddings: list[
            Embedding
        ] = []

        self._metric = (
            metric
            if metric is not None
            else CosineSimilarity()
        )

    @property
    def name(
        self,
    ) -> str:
        """
        Return the vector
        store name.
        """

        return (
            "InMemoryVectorStore"
        )

    @property
    def description(
        self,
    ) -> str:
        """
        Return the vector
        store description.
        """

        return (
            "Stores embeddings "
            "in memory."
        )

    @property
    def version(
        self,
    ) -> str:
        """
        Return the vector
        store version.
        """

        return "1.0.0"

    @property
    def metric(
        self,
    ) -> SimilarityMetric:
        """
        Return the
        similarity metric.
        """

        return self._metric

    def add(
        self,
        embedding: Embedding,
    ) -> None:
        """
        Store an embedding.
        """

        self._embeddings.append(
            embedding,
        )

    def remove(
        self,
        embedding: Embedding,
    ) -> None:
        """
        Remove an embedding.
        """

        self._embeddings.remove(
            embedding,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all stored
        embeddings.
        """

        self._embeddings.clear()

    def embeddings(
        self,
    ) -> list[Embedding]:
        """
        Return all stored
        embeddings.
        """

        return list(
            self._embeddings,
        )

    def search(
        self,
        query: Embedding,
        limit: int = 5,
    ) -> list[Embedding]:
        """
        Return the most
        similar embeddings.
        """

        ranked = sorted(
            self._embeddings,
            key=lambda embedding:
                self._metric.calculate(
                    query,
                    embedding,
                ),
            reverse=True,
        )

        return ranked[:limit]