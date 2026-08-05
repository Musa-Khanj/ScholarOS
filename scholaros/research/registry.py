"""
ScholarOS
Research Session Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registry for
research sessions.
"""

from __future__ import annotations

from scholaros.research.collection import (
    ResearchSessionCollection,
)
from scholaros.research.session import (
    ResearchSession,
)


class ResearchSessionRegistry:
    """
    Registry for
    research sessions.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        registry.
        """

        self._collection = (
            ResearchSessionCollection()
        )

    @property
    def collection(
        self,
    ) -> ResearchSessionCollection:
        """
        Return the
        session collection.
        """

        return self._collection

    def register(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Register a
        research session.
        """

        self._collection.add(
            session,
        )

    def unregister(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Unregister a
        research session.
        """

        self._collection.remove(
            session,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        registered sessions.
        """

        self._collection.clear()

    def sessions(
        self,
    ) -> list[
        ResearchSession
    ]:
        """
        Return all
        registered sessions.
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
        sessions.
        """

        return len(
            self._collection,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        registered sessions.
        """

        return iter(
            self._collection,
        )

    def __contains__(
        self,
        session: ResearchSession,
    ) -> bool:
        """
        Return whether the
        session is
        registered.
        """

        return (
            session
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