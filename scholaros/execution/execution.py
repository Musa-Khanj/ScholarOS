"""
ScholarOS
Execution

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates execution of workflows.

Responsibilities
----------------
• Own a workflow
• Coordinate execution
• Provide a stable execution API
"""

from __future__ import annotations

from scholaros.workflow import Workflow


class Execution:
    """
    Coordinates workflow execution.
    """

    def __init__(
        self,
        workflow: Workflow,
    ) -> None:
        """
        Initialize the execution engine.
        """

        self._workflow = workflow

    @property
    def workflow(
        self,
    ) -> Workflow:
        """
        Return the configured workflow.
        """

        return self._workflow

    def execute(
        self,
    ) -> object:
        """
        Execute the configured workflow.
        """

        return self._workflow.run()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the execution engine.
        """

        return (
            f"{self.__class__.__name__}("
            f"workflow={self.workflow.__class__.__name__}"
            f")"
        )