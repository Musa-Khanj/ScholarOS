"""
ScholarOS
Planner

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates planning of workflow execution.

Responsibilities
----------------
• Own an execution engine
• Produce execution plans
• Provide a stable planning API
"""

from __future__ import annotations

from scholaros.execution import Execution


class Planner:
    """
    Coordinates execution planning.
    """

    def __init__(
        self,
        execution: Execution,
    ) -> None:
        """
        Initialize the planner.
        """

        self._execution = execution   

    @property
    def execution(
        self,
    ) -> Execution:
        """
        Return the configured execution engine.
        """

        return self._execution

    def plan(
        self,
    ) -> object:
        """
        Create and execute the current
        execution plan.
        """

        return self._execution.execute()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the planner.
        """

        return (
            f"{self.__class__.__name__}("
            f"execution={self.execution.__class__.__name__}"
            f")"
        )