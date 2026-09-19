"""
ScholarOS Knowledge Registry.

Stores and queries registered knowledge collections.
"""

from __future__ import annotations

from typing import Iterator

from scholaros.knowledge.collection import KnowledgeCollection


class KnowledgeRegistry:
    """
    Stores registered knowledge collections.
    """

    def __init__(self) -> None:
        """
        Initialize the knowledge registry.
        """
        self._collections: dict[str, KnowledgeCollection] = {}

    def add(self, name: str, collection: KnowledgeCollection) -> None:
        """
        Register a knowledge collection under the supplied name.
        """
        if name in self._collections:
            raise ValueError(f"Knowledge collection {name!r} is already registered.")
        self._collections[name] = collection

    def update(self, name: str, collection: KnowledgeCollection) -> None:
        """
        Add or replace a registered collection.
        """
        self._collections[name] = collection

    def remove(self, name: str) -> None:
        """
        Remove a registered collection by name.
        """
        self._collections.pop(name, None)

    def get(self, name: str) -> KnowledgeCollection:
        """
        Return a registered collection by name.
        """
        try:
            return self._collections[name]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge collection {name!r}.") from exc

    def get_or_create(self, name: str, description: str = "") -> KnowledgeCollection:
        """
        Retrieve collection by name, or create and register it if absent.
        """
        if name not in self._collections:
            coll = KnowledgeCollection(name=name, description=description)
            self._collections[name] = coll
        return self._collections[name]

    def contains(self, name: str) -> bool:
        """
        Return whether a collection is registered under the supplied name.
        """
        return name in self._collections

    def names(self) -> tuple[str, ...]:
        """
        Return registered collection names.
        """
        return tuple(self._collections.keys())

    def values(self) -> tuple[KnowledgeCollection, ...]:
        """
        Return registered collections.
        """
        return tuple(self._collections.values())

    def items(self) -> tuple[tuple[str, KnowledgeCollection], ...]:
        """
        Return registered collection name and collection pairs.
        """
        return tuple(self._collections.items())

    def clear(self) -> None:
        """
        Remove all registered collections.
        """
        self._collections.clear()

    def __contains__(self, name: str) -> bool:
        """
        Return whether the supplied collection is registered.
        """
        return self.contains(name)

    def __iter__(self) -> Iterator[KnowledgeCollection]:
        """
        Iterate over registered collections.
        """
        return iter(self._collections.values())

    def __len__(self) -> int:
        """
        Return the number of registered collections.
        """
        return len(self._collections)

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the registry.
        """
        return f"{self.__class__.__name__}(collections={len(self)})"


Registry = KnowledgeRegistry

__all__ = [
    "KnowledgeRegistry",
    "Registry",
]
