"""
ScholarOS
Workflow

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates agent execution within
ScholarOS.

Responsibilities
----------------
• Coordinate workflow execution
• Own an agent
• Provide a stable workflow API
"""

from __future__ import annotations

from scholaros.agents import BaseAgent


class Workflow:
    """
    Coordinates the execution of an agent.
    """

    def __init__(
        self,
        agent: BaseAgent,
    ) -> None:

        self._agent = agent

    @property
    def agent(
        self,
    ) -> BaseAgent:
        """
        Return the configured agent.
        """

        return self._agent

    def run(
        self,
    ) -> object:
        """
        Execute the configured agent.
        """

        return self._agent.execute()