"""
ScholarOS
Memory Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores registered memory
collections.
"""

from __future__ import annotations

from scholaros.memory.collection import (
    MemoryCollection,
)


class MemoryRegistry:
    """
    Stores registered memory
    collections.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the memory
        registry.
        """

        self._collections: dict[
            str,
            MemoryCollection,
        ] = {}

    def add(
        self,
        name: str,
        collection: MemoryCollection,
    ) -> None:
        """
        Register a memory
        collection.
        """

        self._collections[
            name
        ] = collection

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered memory
        collection.
        """

        self._collections.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> MemoryCollection | None:
        """
        Return a registered memory
        collection.
        """

        return self._collections.get(
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

        return (
            name
            in self._collections
        )

    def names(
        self,
    ) -> list[str]:
        """
        Return registered memory
        collection names.
        """

        return list(
            self._collections.keys(),
        )

    def values(
        self,
    ) -> list[MemoryCollection]:
        """
        Return registered memory
        collections.
        """

        return list(
            self._collections.values(),
        )

    def items(
        self,
    ) -> list[
        tuple[
            str,
            MemoryCollection,
        ]
    ]:
        """
        Return registered memory
        collection items.
        """

        return list(
            self._collections.items(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        memory collections.
        """

        self._collections.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        registered memory
        collections.
        """

        return len(
            self._collections,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        memory registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections={len(self)}"
            f")"
        )