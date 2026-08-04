"""
ScholarOS
Retrieval Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manages registered
retrieval collections.
"""

from __future__ import annotations

from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.registry import (
    RetrievalRegistry,
)


class RetrievalManager:
    """
    Manages registered
    retrieval collections.
    """

    def __init__(
        self,
        registry: RetrievalRegistry,
    ) -> None:
        """
        Initialize the retrieval
        manager.
        """

        self._registry = registry

    @property
    def registry(
        self,
    ) -> RetrievalRegistry:
        """
        Return the retrieval
        registry.
        """

        return self._registry

    def register(
        self,
        name: str,
        collection: RetrievalCollection,
    ) -> None:
        """
        Register a retrieval
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
        Unregister a retrieval
        collection.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> RetrievalCollection | None:
        """
        Return a registered
        retrieval collection.
        """

        return self._registry.get(
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

        return self._registry.contains(
            name,
        )

    def installed(
        self,
    ) -> list[str]:
        """
        Return registered
        retrieval collection
        names.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        retrieval collections.
        """

        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self._registry)}"
            f")"
        )