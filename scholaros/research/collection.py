"""
ScholarOS
Research Session Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Collection of
research sessions.
"""

from __future__ import annotations

from scholaros.research.session import (
    ResearchSession,
)


class ResearchSessionCollection:
    """
    Collection of
    research sessions.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        collection.
        """

        self._sessions: list[
            ResearchSession
        ] = []

    def add(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Add a research
        session.
        """

        self._sessions.append(
            session,
        )

    def remove(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Remove a research
        session.
        """

        self._sessions.remove(
            session,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        sessions.
        """

        self._sessions.clear()

    def all(
        self,
    ) -> list[
        ResearchSession
    ]:
        """
        Return all
        sessions.
        """

        return list(
            self._sessions,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of sessions.
        """

        return len(
            self._sessions,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        sessions.
        """

        return iter(
            self._sessions,
        )

    def __contains__(
        self,
        session: ResearchSession,
    ) -> bool:
        """
        Return whether the
        session exists.
        """

        return (
            session
            in self._sessions
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