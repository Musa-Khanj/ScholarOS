"""
ScholarOS
Agent Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manager for
collaboration agents.
"""

from __future__ import annotations

from scholaros.collaboration.agent import (
    Agent,
)
from scholaros.collaboration.agent_registry import (
    AgentRegistry,
)


class AgentManager:
    """
    Manager for
    collaboration agents.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        manager.
        """

        self._registry = (
            AgentRegistry()
        )

    @property
    def registry(
        self,
    ) -> AgentRegistry:
        """
        Return the
        agent registry.
        """

        return self._registry

    def create(
        self,
        name: str,
        role: str,
        description: str,
        enabled: bool = True,
    ) -> Agent:
        """
        Create and register
        an agent.
        """

        agent = Agent(
            name=name,
            role=role,
            description=description,
            enabled=enabled,
        )

        self.register(
            agent,
        )

        return agent

    def register(
        self,
        agent: Agent,
    ) -> None:
        """
        Register an
        agent.
        """

        self._registry.register(
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

        self._registry.unregister(
            agent,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        agents.
        """

        self._registry.clear()

    def agents(
        self,
    ) -> list[
        Agent
    ]:
        """
        Return all
        agents.
        """

        return (
            self._registry.agents()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of agents.
        """

        return len(
            self._registry,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        agents.
        """

        return iter(
            self._registry,
        )

    def __contains__(
        self,
        agent: Agent,
    ) -> bool:
        """
        Return whether the
        agent is managed.
        """

        return (
            agent
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