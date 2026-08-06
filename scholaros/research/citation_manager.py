"""
ScholarOS
Citation Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manager for
research citations.
"""

from __future__ import annotations

from scholaros.research.citation import (
    Citation,
)
from scholaros.research.citation_registry import (
    CitationRegistry,
)


class CitationManager:
    """
    Manager for
    research citations.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        manager.
        """

        self._registry = (
            CitationRegistry()
        )

    @property
    def registry(
        self,
    ) -> CitationRegistry:
        """
        Return the
        citation registry.
        """

        return self._registry

    def create(
        self,
        title: str,
        source: str,
        url: str | None = None,
        authors: list[str] | None = None,
        published: str | None = None,
        accessed: str | None = None,
    ) -> Citation:
        """
        Create and register
        a citation.
        """

        citation = Citation(
            title=title,
            source=source,
            url=url,
            authors=(
                authors
                if authors is not None
                else []
            ),
            published=published,
            accessed=accessed,
        )

        self.register(
            citation,
        )

        return citation

    def register(
        self,
        citation: Citation,
    ) -> None:
        """
        Register a
        citation.
        """

        self._registry.register(
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

        self._registry.unregister(
            citation,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        citations.
        """

        self._registry.clear()

    def citations(
        self,
    ) -> list[
        Citation
    ]:
        """
        Return all
        citations.
        """

        return (
            self._registry.citations()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of citations.
        """

        return len(
            self._registry,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        citations.
        """

        return iter(
            self._registry,
        )

    def __contains__(
        self,
        citation: Citation,
    ) -> bool:
        """
        Return whether the
        citation is managed.
        """

        return (
            citation
            in self._registry
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