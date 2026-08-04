"""
ScholarOS
Memory Entry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single memory entry
stored within ScholarOS.
"""

from __future__ import annotations

from typing import Any


class MemoryEntry:
    """
    Represents a single memory
    entry.
    """

    def __init__(
        self,
        entry_id: str,
        content: str,
        metadata: dict[str, Any],
        embedding: list[float] | None = None,
    ) -> None:
        """
        Initialize a memory entry.
        """

        self._entry_id = entry_id
        self._content = content
        self._metadata = metadata
        self._embedding = embedding

    @property
    def entry_id(
        self,
    ) -> str:
        """
        Return the memory entry ID.
        """

        return self._entry_id

    @property
    def content(
        self,
    ) -> str:
        """
        Return the memory content.
        """

        return self._content

    @property
    def metadata(
        self,
    ) -> dict[str, Any]:
        """
        Return the memory metadata.
        """

        return self._metadata

    @property
    def embedding(
        self,
    ) -> list[float] | None:
        """
        Return the embedding vector.
        """

        return self._embedding

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the memory
        entry.
        """

        return (
            f"{self.__class__.__name__}("
            f"entry_id={self.entry_id!r}, "
            f"content={self.content!r}"
            f")"
        )