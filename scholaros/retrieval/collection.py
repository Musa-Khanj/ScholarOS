"""
ScholarOS
Retrieval Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Stores retrieval
results.
"""

from __future__ import annotations

from scholaros.retrieval.result import (
    RetrievalResult,
)


class RetrievalCollection:
    """
    Stores retrieval
    results.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the retrieval
        collection.
        """

        self._results: list[
            RetrievalResult
        ] = []

    def add(
        self,
        result: RetrievalResult,
    ) -> None:
        """
        Add a retrieval
        result.
        """

        self._results.append(
            result,
        )

    def remove(
        self,
        result: RetrievalResult,
    ) -> None:
        """
        Remove a retrieval
        result.
        """

        if result in self._results:
            self._results.remove(
                result,
            )

    def clear(
        self,
    ) -> None:
        """
        Remove all retrieval
        results.
        """

        self._results.clear()

    def values(
        self,
    ) -> list[
        RetrievalResult
    ]:
        """
        Return all retrieval
        results.
        """

        return list(
            self._results,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        retrieval results.
        """

        return len(
            self._results,
        )

    def __iter__(
        self,
    ):
        """
        Return an iterator over
        retrieval results.
        """

        return iter(
            self._results,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval collection.
        """

        return (
            f"{self.__class__.__name__}("
            f"results={len(self)}"
            f")"
        )