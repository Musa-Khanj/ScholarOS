"""
ScholarOS
Memory

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the runtime working memory.

Responsibilities
----------------
• Store temporary runtime data
• Provide a stable memory API
• Remain independent of AI providers
"""

from __future__ import annotations


class Memory:
    """
    Represents runtime working memory.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the runtime memory.
        """

        self._storage: dict[str, object] = {}

    @property
    def storage(
        self,
    ) -> dict[str, object]:
        """
        Return the underlying runtime storage.
        """

        return self._storage

    def set(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store a value in runtime memory.
        """

        self._storage[key] = value

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Return a value from runtime memory.
        """

        return self._storage.get(
            key,
            default,
        )

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a value from runtime memory
        if it exists.
        """

        self._storage.pop(
            key,
            None,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all values from runtime memory.
        """

        self._storage.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the memory.
        """

        return (
            f"{self.__class__.__name__}("
            f"size={len(self._storage)}"
            f")"
        )