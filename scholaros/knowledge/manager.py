"""
ScholarOS
Knowledge Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manages registered knowledge
collections.
"""

from __future__ import annotations

from scholaros.knowledge.collection import (
    KnowledgeCollection,
)
from scholaros.knowledge.registry import (
    KnowledgeRegistry,
)


class KnowledgeManager:
    """
    Manages registered knowledge
    collections.
    """

    def __init__(
        self,
        registry: KnowledgeRegistry | None = None,
    ) -> None:
        """
        Initialize the knowledge
        manager.
        """

        self._registry = (
            registry
            if registry is not None
            else KnowledgeRegistry()
        )

    @property
    def registry(
        self,
    ) -> KnowledgeRegistry:
        """
        Return the knowledge registry.
        """

        return self._registry

    def add(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Add a knowledge
        collection.
        """

        self._registry.add(
            name,
            collection,
        )

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered
        knowledge collection.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> KnowledgeCollection:
        """
        Return a registered
        knowledge collection.
        """

        return self._registry.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a knowledge
        collection is registered.
        """

        return self._registry.contains(
            name,
        )

    def names(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Return registered knowledge
        collection names.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        knowledge collections.
        """

        self._registry.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        registered collections.
        """

        return len(
            self._registry,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        knowledge manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self)}"
            f")"
        )