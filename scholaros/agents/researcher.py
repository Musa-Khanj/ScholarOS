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

from typing import TYPE_CHECKING, Any

from scholaros.agents.base import BaseAgent
from scholaros.research.pipeline import ResearchPipeline

if TYPE_CHECKING:
    from scholaros.knowledge.rag.pipeline import RAGPipeline
    from scholaros.knowledge.rag.service import RAGService
    from scholaros.research.result import ResearchResult
    from scholaros.research.session import ResearchSession



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

    @classmethod
    def from_rag(cls, rag: RAGService | RAGPipeline) -> ResearchAgent:
        """Create a ResearchAgent configured with RAG."""
        return cls(pipeline=ResearchPipeline.from_rag(rag))

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

    def research(
        self,
        query: str,
        session: ResearchSession | None = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """
        Execute grounded research for a query through the RAG-enabled pipeline.
        """
        return self._pipeline.execute_rag(query, session=session, **kwargs)

    def run_workflow(
        self,
        query: str,
        session: ResearchSession | None = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """
        Execute a full multi-stage research workflow.
        """
        return self._pipeline.execute_workflow(query, session=session, **kwargs)



    def execute(
        self,
        task: str | None = None,
        **kwargs: Any,
    ) -> object:
        """
        Execute the research task.
        """

        if task is None:
            if "query" in kwargs and isinstance(kwargs["query"], str):
                q = kwargs.pop("query")
                return self.research(q, **kwargs)
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


__all__ = [
    "ResearchAgent",
]
