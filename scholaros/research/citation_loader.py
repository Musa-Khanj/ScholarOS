"""
ScholarOS
Citation Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loader for
research citations.
"""

from __future__ import annotations

from scholaros.research.citation_manager import (
    CitationManager,
)


class CitationLoader:
    """
    Loader for
    research citations.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        loader.
        """

        self._manager = (
            CitationManager()
        )

    @property
    def manager(
        self,
    ) -> CitationManager:
        """
        Return the
        citation manager.
        """

        return self._manager

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            "manager="
            f"{self._manager.__class__.__name__}"
            ")"
        )