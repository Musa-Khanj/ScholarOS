"""
ScholarOS
Research Agent

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Concrete implementation of BaseAgent
responsible for executing research tasks.
"""

from __future__ import annotations
from scholaros.research.pipeline import ResearchPipeline

from scholaros.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Concrete agent responsible for
    research-oriented tasks.
    """

    def __init__(
        self,
        pipeline: ResearchPipeline,
    ) -> None:
        """
        Initialize the research agent.
        """

        self._pipeline = pipeline

    @property
    def name(
        self,
    ) -> str:
        """
        Return the agent name.
        """

        return "Research Agent"

    @property
    def description(
        self,
    ) -> str:
        """
        Return a short description
        of the agent.
        """

        return (
            "Executes research-oriented "
            "tasks."
        )

    @property
    def version(
        self,
    ) -> str:
        """
        Return the agent version.
        """

        return "1.0"

    @property
    def pipeline(
        self,
    ) -> ResearchPipeline:
        """
        Return the configured research
        pipeline.
        """

        return self._pipeline
    
    def execute(
        self,
        task: str | None = None,
        **kwargs: str,
    ) -> object:
        """
        Execute the research task.
        """

        if task is None:
            raise NotImplementedError(
                "ResearchAgent.execute requires a task or template name."
            )

        return self._pipeline.execute(
            task,
            **kwargs,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the agent.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}"
            f")"
        )