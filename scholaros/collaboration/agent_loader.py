"""
ScholarOS
Agent Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loader for
collaboration agents.
"""

from __future__ import annotations

from scholaros.collaboration.agent_manager import (
    AgentManager,
)


class AgentLoader:
    """
    Loader for
    collaboration agents.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        loader.
        """

        self._manager = (
            AgentManager()
        )

    @property
    def manager(
        self,
    ) -> AgentManager:
        """
        Return the
        agent manager.
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