"""
ScholarOS
UI Application

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the application-facing boundary
between the ScholarOS user interface and
the existing ScholarOS public APIs.

The UI application layer does not implement
research, RAG, AI, or kernel behavior.
It delegates those responsibilities to the
existing subsystems.
"""

from __future__ import annotations

from typing import Any

from scholaros.knowledge.rag.pipeline import (
    RAGPipeline,
)
from scholaros.knowledge.rag.request import (
    RAGRequest,
)
from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.research.pipeline import (
    ResearchPipeline,
)


class UIApplication:
    """
    Provides the application-facing UI boundary.

    The UI application delegates domain operations
    to existing ScholarOS pipelines and exposes
    stable operations suitable for presentation
    layers.
    """

    def __init__(
        self,
        research: ResearchPipeline | None = None,
        rag: RAGPipeline | None = None,
    ) -> None:
        """
        Initialize the UI application.

        Parameters
        ----------
        research:
            Optional configured research pipeline.

        rag:
            Optional configured RAG pipeline.
        """

        self._research = research
        self._rag = rag

    @property
    def research(
        self,
    ) -> ResearchPipeline | None:
        """
        Return the configured research pipeline.
        """

        return self._research

    @property
    def rag(
        self,
    ) -> RAGPipeline | None:
        """
        Return the configured RAG pipeline.
        """

        return self._rag

    def status(
        self,
    ) -> str:
        """
        Return the current UI application status.

        The application is considered ready when
        at least one usable ScholarOS operation
        has been configured.
        """

        if (
            self.research is not None
            or self.rag is not None
        ):
            return "READY"

        return "NOT_CONFIGURED"

    def info(
        self,
    ) -> dict[str, Any]:
        """
        Return UI application information.
        """

        return {
            "research": (
                self.research is not None
            ),
            "rag": (
                self.rag is not None
            ),
            "status": self.status(),
        }

    def research_execute(
        self,
        template: str,
        **variables: str,
    ) -> object:
        """
        Execute a research operation.

        Raises
        ------
        RuntimeError
            If a research pipeline has not
            been configured.
        """

        if self.research is None:
            raise RuntimeError(
                "Research pipeline is not configured."
            )

        return self.research.execute(
            template,
            **variables,
        )

    def research_build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a research prompt without
        executing it.

        Raises
        ------
        RuntimeError
            If a research pipeline has not
            been configured.
        """

        if self.research is None:
            raise RuntimeError(
                "Research pipeline is not configured."
            )

        return self.research.build(
            template,
            **variables,
        )

    def research_contains(
        self,
        template: str,
    ) -> bool:
        """
        Check whether a research template
        exists.

        Raises
        ------
        RuntimeError
            If a research pipeline has not
            been configured.
        """

        if self.research is None:
            raise RuntimeError(
                "Research pipeline is not configured."
            )

        return self.research.contains(
            template,
        )

    def rag_run(
        self,
        request: RAGRequest,
    ) -> RAGResponse:
        """
        Execute a RAG operation.

        Raises
        ------
        RuntimeError
            If a RAG pipeline has not
            been configured.
        """

        if self.rag is None:
            raise RuntimeError(
                "RAG pipeline is not configured."
            )

        return self.rag.run(
            request,
        )

    def rag_query(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> RAGResponse:
        """
        Execute a RAG query through the
        configured RAG pipeline.
        """

        request = RAGRequest(
            query=query,
            minimum_score=minimum_score,
        )

        return self.rag_run(
            request,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the UI application.
        """

        return (
            f"{self.__class__.__name__}("
            f"research={self.research is not None}, "
            f"rag={self.rag is not None}"
            f")"
        )