"""
ScholarOS
Retrieval Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores registered
retrieval collections.
"""

from __future__ import annotations

from scholaros.retrieval.collection import (
    RetrievalCollection,
)


class RetrievalRegistry:
    """
    Stores registered
    retrieval collections.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the retrieval
        registry.
        """

        self._collections: dict[
            str,
            RetrievalCollection,
        ] = {}

    def add(
        self,
        name: str,
        collection: RetrievalCollection,
    ) -> None:
        """
        Register a retrieval
        collection.
        """

        self._collections[
            name
        ] = collection

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered
        retrieval collection.
        """

        self._collections.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> RetrievalCollection | None:
        """
        Return a registered
        retrieval collection.
        """

        return self._collections.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a retrieval
        collection is registered.
        """

        return name in self._collections

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
        RetrievalCollection
    ]:
        """
        Return registered
        retrieval collections.
        """

        return list(
            self._collections.values(),
        )

    def items(
        self,
    ) -> list[
        tuple[
            str,
            RetrievalCollection,
        ]
    ]:
        """
        Return registered
        retrieval collection
        items.
        """

        return list(
            self._collections.items(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        retrieval collections.
        """

        self._collections.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        registered retrieval
        collections.
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
        retrieval registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self)}"
            f")"
        )