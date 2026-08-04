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
        registry: KnowledgeRegistry,
    ) -> None:
        """
        Initialize the knowledge
        manager.
        """

        self._registry = registry

    @property
    def registry(
        self,
    ) -> KnowledgeRegistry:
        """
        Return the knowledge registry.
        """

        return self._registry

    def register(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Register a knowledge
        collection.
        """

        self._registry.add(
            name,
            collection,
        )

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a knowledge
        collection.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> KnowledgeCollection | None:
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

    def installed(
        self,
    ) -> list[str]:
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
            f"collections={len(self._registry)}"
            f")"
        )