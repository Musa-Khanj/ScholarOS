"""
ScholarOS
Retrieval Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads and unloads
retrieval collections.
"""

from __future__ import annotations

from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.manager import (
    RetrievalManager,
)


class RetrievalLoader:
    """
    Loads and unloads
    retrieval collections.
    """

    def __init__(
        self,
        manager: RetrievalManager,
    ) -> None:
        """
        Initialize the retrieval
        loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> RetrievalManager:
        """
        Return the retrieval
        manager.
        """

        return self._manager

    def load(
        self,
        name: str,
        collection: RetrievalCollection,
    ) -> None:
        """
        Load a retrieval
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
        Unload a retrieval
        collection.
        """

        self._manager.unregister(
            name,
        )

    def reload(
        self,
        name: str,
        collection: RetrievalCollection,
    ) -> None:
        """
        Reload a retrieval
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
        Return the discovered
        retrieval collections.
        """

        return self._manager.installed()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.manager.registry)}"
            f")"
        )