"""
ScholarOS
Citation Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registry for
research citations.
"""

from __future__ import annotations

from scholaros.research.citation import (
    Citation,
)
from scholaros.research.citation_collection import (
    CitationCollection,
)


class CitationRegistry:
    """
    Registry for
    research citations.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        registry.
        """

        self._collection = (
            CitationCollection()
        )

    @property
    def collection(
        self,
    ) -> CitationCollection:
        """
        Return the
        citation collection.
        """

        return self._collection

    def register(
        self,
        citation: Citation,
    ) -> None:
        """
        Register a
        citation.
        """

        self._collection.add(
            citation,
        )

    def unregister(
        self,
        citation: Citation,
    ) -> None:
        """
        Unregister a
        citation.
        """

        self._collection.remove(
            citation,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        registered citations.
        """

        self._collection.clear()

    def citations(
        self,
    ) -> list[
        Citation
    ]:
        """
        Return all
        registered citations.
        """

        return (
            self._collection.all()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of registered
        citations.
        """

        return len(
            self._collection,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        registered citations.
        """

        return iter(
            self._collection,
        )

    def __contains__(
        self,
        citation: Citation,
    ) -> bool:
        """
        Return whether the
        citation is
        registered.
        """

        return (
            citation
            in self._collection
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