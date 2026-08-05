"""
ScholarOS
Research Session Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manager for
research sessions.
"""

from __future__ import annotations

from scholaros.research.registry import (
    ResearchSessionRegistry,
)
from scholaros.research.session import (
    ResearchSession,
)


class ResearchSessionManager:
    """
    Manager for
    research sessions.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        manager.
        """

        self._registry = (
            ResearchSessionRegistry()
        )

    @property
    def registry(
        self,
    ) -> ResearchSessionRegistry:
        """
        Return the
        session registry.
        """

        return self._registry

    def create(
        self,
        query: str,
    ) -> ResearchSession:
        """
        Create and register
        a research session.
        """

        session = (
            ResearchSession(
                query=query,
            )
        )

        self.register(
            session,
        )

        return session

    def register(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Register a
        research session.
        """

        self._registry.register(
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

        self._registry.unregister(
            session,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        research sessions.
        """

        self._registry.clear()

    def sessions(
        self,
    ) -> list[
        ResearchSession
    ]:
        """
        Return all
        research sessions.
        """

        return (
            self._registry.sessions()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of sessions.
        """

        return len(
            self._registry,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        research sessions.
        """

        return iter(
            self._registry,
        )

    def __contains__(
        self,
        session: ResearchSession,
    ) -> bool:
        """
        Return whether the
        session is managed.
        """

        return (
            session
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