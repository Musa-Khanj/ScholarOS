"""
ScholarOS
Knowledge Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads and unloads knowledge
collections.
"""

from __future__ import annotations

from scholaros.knowledge.collection import (
    KnowledgeCollection,
)
from scholaros.knowledge.manager import (
    KnowledgeManager,
)


class KnowledgeLoader:
    """
    Loads and unloads knowledge
    collections.
    """

    def __init__(
        self,
        manager: KnowledgeManager,
    ) -> None:
        """
        Initialize the knowledge
        loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> KnowledgeManager:
        """
        Return the knowledge manager.
        """

        return self._manager

    def load(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Load a knowledge collection.
        """

        self._manager.register(
            name,
            collection,
        )

    def unload(
        self,
        name: str,
    ) -> None:
        """
        Unload a knowledge collection.
        """

        self._manager.unregister(
            name,
        )

    def reload(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Reload a knowledge collection.
        """

        self.unload(
            name,
        )

        self.load(
            name,
            collection,
        )

    def discover(
        self,
    ) -> list[str]:
        """
        Return the discovered
        knowledge collections.
        """

        return self._manager.installed()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self.manager.registry)}"
            f")"
        )