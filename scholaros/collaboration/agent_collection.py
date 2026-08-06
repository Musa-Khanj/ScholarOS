"""
ScholarOS
Agent Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Collection of
collaboration agents.
"""

from __future__ import annotations

from scholaros.collaboration.agent import (
    Agent,
)


class AgentCollection:
    """
    Collection of
    collaboration agents.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        collection.
        """

        self._agents: list[
            Agent
        ] = []

    def add(
        self,
        agent: Agent,
    ) -> None:
        """
        Add an
        agent.
        """

        self._agents.append(
            agent,
        )

    def remove(
        self,
        agent: Agent,
    ) -> None:
        """
        Remove an
        agent.
        """

        self._agents.remove(
            agent,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        agents.
        """

        self._agents.clear()

    def all(
        self,
    ) -> list[
        Agent
    ]:
        """
        Return all
        agents.
        """

        return list(
            self._agents,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of agents.
        """

        return len(
            self._agents,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        agents.
        """

        return iter(
            self._agents,
        )

    def __contains__(
        self,
        agent: Agent,
    ) -> bool:
        """
        Return whether the
        agent exists.
        """

        return (
            agent
            in self._agents
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