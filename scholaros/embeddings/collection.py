"""
ScholarOS
Embedding Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores embedding
objects.
"""

from __future__ import annotations

from collections.abc import Iterator

from scholaros.embeddings.embedding import (
    Embedding,
)


class EmbeddingCollection:
    """
    Stores embedding
    objects.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        embedding collection.
        """

        self._embeddings: list[
            Embedding
        ] = []

    def add(
        self,
        embedding: Embedding,
    ) -> None:
        """
        Add an embedding.
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
        Remove all
        embeddings.
        """

        self._embeddings.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of embeddings.
        """

        return len(
            self._embeddings,
        )

    def __iter__(
        self,
    ) -> Iterator[
        Embedding
    ]:
        """
        Iterate over the
        embeddings.
        """

        return iter(
            self._embeddings,
        )

    def __getitem__(
        self,
        index: int,
    ) -> Embedding:
        """
        Return an embedding
        by index.
        """

        return self._embeddings[
            index
        ]

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        collection.
        """

        return (
            f"{self.__class__.__name__}("
            f"embeddings={len(self)}"
            f")"
        )