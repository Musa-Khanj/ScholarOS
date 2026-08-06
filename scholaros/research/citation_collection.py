"""
ScholarOS
Citation Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Collection of
research citations.
"""

from __future__ import annotations

from scholaros.research.citation import (
    Citation,
)


class CitationCollection:
    """
    Collection of
    research citations.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        collection.
        """

        self._citations: list[
            Citation
        ] = []

    def add(
        self,
        citation: Citation,
    ) -> None:
        """
        Add a
        citation.
        """

        self._citations.append(
            citation,
        )

    def remove(
        self,
        citation: Citation,
    ) -> None:
        """
        Remove a
        citation.
        """

        self._citations.remove(
            citation,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        citations.
        """

        self._citations.clear()

    def all(
        self,
    ) -> list[
        Citation
    ]:
        """
        Return all
        citations.
        """

        return list(
            self._citations,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of citations.
        """

        return len(
            self._citations,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        citations.
        """

        return iter(
            self._citations,
        )

    def __contains__(
        self,
        citation: Citation,
    ) -> bool:
        """
        Return whether the
        citation exists.
        """

        return (
            citation
            in self._citations
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"size={len(self)}"
            f")"
        )