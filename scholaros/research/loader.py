"""
ScholarOS
Research Session Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loader for
research sessions.
"""

from __future__ import annotations

from scholaros.research.manager import (
    ResearchSessionManager,
)


class ResearchSessionLoader:
    """
    Loader for
    research sessions.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        loader.
        """

        self._manager = (
            ResearchSessionManager()
        )

    @property
    def manager(
        self,
    ) -> ResearchSessionManager:
        """
        Return the
        research session
        manager.
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