"""
ScholarOS
Embedding Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores named embedding
collections.
"""

from __future__ import annotations

from scholaros.embeddings.collection import (
    EmbeddingCollection,
)


class EmbeddingRegistry:
    """
    Stores named
    embedding collections.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        embedding registry.
        """

        self._collections: dict[
            str,
            EmbeddingCollection,
        ] = {}

    def add(
        self,
        name: str,
        collection: EmbeddingCollection,
    ) -> None:
        """
        Register an
        embedding collection.
        """

        self._collections[
            name
        ] = collection

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove an embedding
        collection.
        """

        del self._collections[
            name
        ]

    def get(
        self,
        name: str,
    ) -> EmbeddingCollection | None:
        """
        Return a registered
        embedding collection.
        """

        return self._collections.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether an
        embedding collection
        is registered.
        """

        return (
            name
            in self._collections
        )

    def names(
        self,
    ) -> list[str]:
        """
        Return registered
        collection names.
        """

        return list(
            self._collections.keys(),
        )

    def values(
        self,
    ) -> list[
        EmbeddingCollection
    ]:
        """
        Return registered
        collections.
        """

        return list(
            self._collections.values(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        collections.
        """

        self._collections.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        registered collections.
        """

        return len(
            self._collections,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self)}"
            f")"
        )