"""
ScholarOS
Embedding Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads embedding
collections.
"""

from __future__ import annotations

from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.manager import (
    EmbeddingManager,
)


class EmbeddingLoader:
    """
    Loads embedding
    collections.
    """

    def __init__(
        self,
        manager: EmbeddingManager,
    ) -> None:
        """
        Initialize the
        embedding loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> EmbeddingManager:
        """
        Return the embedding
        manager.
        """

        return self._manager

    def load(
        self,
        name: str,
        collection: EmbeddingCollection,
    ) -> None:
        """
        Load an embedding
        collection.
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
        Unload an embedding
        collection.
        """

        self._manager.unregister(
            name,
        )

    def reload(
        self,
        name: str,
        collection: EmbeddingCollection,
    ) -> None:
        """
        Reload an embedding
        collection.
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
        Return loaded
        collections.
        """

        return (
            self._manager.installed()
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        embedding loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.manager.registry)}"
            f")"
        )