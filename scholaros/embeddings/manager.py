"""
ScholarOS
Embedding Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manages embedding
collections.
"""

from __future__ import annotations

from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.registry import (
    EmbeddingRegistry,
)


class EmbeddingManager:
    """
    Manages embedding
    collections.
    """

    def __init__(
        self,
        registry: EmbeddingRegistry,
    ) -> None:
        """
        Initialize the
        embedding manager.
        """

        self._registry = registry

    @property
    def registry(
        self,
    ) -> EmbeddingRegistry:
        """
        Return the embedding
        registry.
        """

        return self._registry

    def register(
        self,
        name: str,
        collection: EmbeddingCollection,
    ) -> None:
        """
        Register an embedding
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
        Unregister an embedding
        collection.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> EmbeddingCollection | None:
        """
        Return a registered
        embedding collection.
        """

        return self._registry.get(
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

        return self._registry.contains(
            name,
        )

    def installed(
        self,
    ) -> list[str]:
        """
        Return the registered
        collection names.
        """

        return self._registry.names()

    def values(
        self,
    ) -> list[
        EmbeddingCollection
    ]:
        """
        Return the registered
        collections.
        """

        return self._registry.values()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        collections.
        """

        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        embedding manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.registry)}"
            f")"
        )