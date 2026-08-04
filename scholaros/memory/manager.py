"""
ScholarOS
Memory Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manages registered memory
collections.
"""

from __future__ import annotations

from scholaros.memory.collection import (
    MemoryCollection,
)
from scholaros.memory.registry import (
    MemoryRegistry,
)


class MemoryManager:
    """
    Manages registered memory
    collections.
    """

    def __init__(
        self,
        registry: MemoryRegistry,
    ) -> None:
        """
        Initialize the memory
        manager.
        """

        self._registry = registry

    @property
    def registry(
        self,
    ) -> MemoryRegistry:
        """
        Return the memory
        registry.
        """

        return self._registry

    def register(
        self,
        name: str,
        collection: MemoryCollection,
    ) -> None:
        """
        Register a memory
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
        Unregister a memory
        collection.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> MemoryCollection | None:
        """
        Return a registered memory
        collection.
        """

        return self._registry.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a memory
        collection is registered.
        """

        return self._registry.contains(
            name,
        )

    def installed(
        self,
    ) -> list[str]:
        """
        Return registered memory
        collection names.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        memory collections.
        """

        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the memory
        manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self._registry)}"
            f")"
        )