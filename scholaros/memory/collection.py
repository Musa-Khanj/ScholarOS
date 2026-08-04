"""
ScholarOS
Memory Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores and manages memory
entries.
"""

from __future__ import annotations

from scholaros.memory.entry import MemoryEntry


class MemoryCollection:
    """
    Stores memory entries.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the memory
        collection.
        """

        self._entries: dict[
            str,
            MemoryEntry,
        ] = {}

    def add(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Add a memory entry.
        """

        self._entries[
            entry.entry_id
        ] = entry

    def remove(
        self,
        entry_id: str,
    ) -> None:
        """
        Remove a memory entry.
        """

        self._entries.pop(
            entry_id,
            None,
        )

    def get(
        self,
        entry_id: str,
    ) -> MemoryEntry | None:
        """
        Return a memory entry.
        """

        return self._entries.get(
            entry_id,
        )

    def contains(
        self,
        entry_id: str,
    ) -> bool:
        """
        Return whether a memory
        entry exists.
        """

        return (
            entry_id
            in self._entries
        )

    def entries(
        self,
    ) -> list[MemoryEntry]:
        """
        Return stored memory
        entries.
        """

        return list(
            self._entries.values(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all memory
        entries.
        """

        self._entries.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        stored memory entries.
        """

        return len(
            self._entries,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the memory
        collection.
        """

        return (
            f"{self.__class__.__name__}("
            f"entries={len(self)}"
            f")"
        )