"""
ScholarOS
Agent Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registry for
collaboration agents.
"""

from __future__ import annotations

from scholaros.collaboration.agent import (
    Agent,
)
from scholaros.collaboration.agent_collection import (
    AgentCollection,
)


class AgentRegistry:
    """
    Registry for
    collaboration agents.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        registry.
        """

        self._collection = (
            AgentCollection()
        )

    @property
    def collection(
        self,
    ) -> AgentCollection:
        """
        Return the
        agent collection.
        """

        return self._collection

    def register(
        self,
        agent: Agent,
    ) -> None:
        """
        Register an
        agent.
        """

        self._collection.add(
            agent,
        )

    def unregister(
        self,
        agent: Agent,
    ) -> None:
        """
        Unregister an
        agent.
        """

        self._collection.remove(
            agent,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        registered agents.
        """

        self._collection.clear()

    def agents(
        self,
    ) -> list[
        Agent
    ]:
        """
        Return all
        registered agents.
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
        agents.
        """

        return len(
            self._collection,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        registered agents.
        """

        return iter(
            self._collection,
        )

    def __contains__(
        self,
        agent: Agent,
    ) -> bool:
        """
        Return whether the
        agent is
        registered.
        """

        return (
            agent
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