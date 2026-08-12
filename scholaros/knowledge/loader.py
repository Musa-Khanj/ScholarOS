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
        Load a knowledge
        collection.
        """

        self._manager.add(
            name,
            collection,
        )

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a loaded knowledge
        collection.
        """

        self._manager.remove(
            name,
        )

    def reload(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Reload a knowledge
        collection.
        """

        self.remove(
            name,
        )

        self.load(
            name,
            collection,
        )

    def discover(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Return the discovered
        knowledge collections.
        """

        return self._manager.names()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of loaded
        knowledge collections.
        """

        return len(
            self._manager,
        )

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
            f"collections={len(self)}"
            f")"
        )