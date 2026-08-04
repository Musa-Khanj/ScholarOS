"""
ScholarOS
Memory Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads and unloads memory
collections.
"""

from __future__ import annotations

from scholaros.memory.collection import (
    MemoryCollection,
)
from scholaros.memory.manager import (
    MemoryManager,
)


class MemoryLoader:
    """
    Loads and unloads memory
    collections.
    """

    def __init__(
        self,
        manager: MemoryManager,
    ) -> None:
        """
        Initialize the memory
        loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> MemoryManager:
        """
        Return the memory
        manager.
        """

        return self._manager

    def load(
        self,
        name: str,
        collection: MemoryCollection,
    ) -> None:
        """
        Load a memory
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
        Unload a memory
        collection.
        """

        self._manager.unregister(
            name,
        )

    def reload(
        self,
        name: str,
        collection: MemoryCollection,
    ) -> None:
        """
        Reload a memory
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
        Return the loaded memory
        collection names.
        """

        return self._manager.installed()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the memory
        loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.manager.registry)}"
            f")"
        )