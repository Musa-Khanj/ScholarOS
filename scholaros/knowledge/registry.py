"""
ScholarOS
Knowledge Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores registered knowledge
collections.
"""

from __future__ import annotations

from scholaros.knowledge.collection import (
    KnowledgeCollection,
)


class KnowledgeRegistry:
    """
    Stores registered knowledge
    collections.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the knowledge
        registry.
        """

        self._collections: dict[
            str,
            KnowledgeCollection,
        ] = {}

    def add(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Register a knowledge
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
        collection.
        """

        self._collections.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> KnowledgeCollection | None:
        """
        Return a registered
        collection.
        """

        return self._collections.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a collection
        is registered.
        """

        return name in self._collections

    def names(
        self,
    ) -> list[str]:
        """
        Return registered collection
        names.
        """

        return list(
            self._collections.keys(),
        )

    def values(
        self,
    ) -> list[KnowledgeCollection]:
        """
        Return registered
        collections.
        """

        return list(
            self._collections.values(),
        )

    def items(
        self,
    ) -> list[
        tuple[
            str,
            KnowledgeCollection,
        ]
    ]:
        """
        Return registered collection
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