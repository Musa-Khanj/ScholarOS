"""
ScholarOS
Research Result

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the result of a completed
research task.

Responsibilities
----------------
• Wrap AIResponse or RAGResponse
• Expose research-oriented properties, citations, and provenance
• Provide a stable API for the research layer
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.ai.response import AIResponse

if TYPE_CHECKING:
    from scholaros.knowledge.rag.response import RAGResponse
    from scholaros.planner.research_planner import ResearchPlan
    from scholaros.research.report import Report
    from scholaros.retrieval.result import RetrievalResult
    from scholaros.workflow.state import WorkflowContext, WorkflowStep


class ResearchResult:
    """
    Represents the result of a research task.
    """

    def __init__(
        self,
        response: AIResponse | RAGResponse,
        report: Report | None = None,
        workflow_context: WorkflowContext | None = None,
        plan: ResearchPlan | None = None,
    ) -> None:

        self._response = response
        self._report = report
        self._workflow_context = workflow_context
        self._plan = plan

    @classmethod
    def from_rag_response(
        cls,
        rag_response: RAGResponse,
        report: Report | None = None,
        workflow_context: WorkflowContext | None = None,
        plan: ResearchPlan | None = None,
    ) -> ResearchResult:
        """Create a ResearchResult directly from a RAGResponse."""
        return cls(
            response=rag_response,
            report=report,
            workflow_context=workflow_context,
            plan=plan,
        )

    @property
    def report(self) -> Report | None:
        """Return the structured research report if generated."""
        return self._report

    @property
    def workflow_context(self) -> WorkflowContext | None:
        """Return the workflow context if executed through a multi-stage workflow."""
        return self._workflow_context

    @property
    def plan(self) -> ResearchPlan | None:
        """Return the research plan if planned through ResearchPlanner."""
        return self._plan

    @property
    def has_workflow(self) -> bool:
        """Return True if this result was produced through a research workflow."""
        return self._workflow_context is not None

    @property
    def steps(self) -> tuple[WorkflowStep, ...]:
        """Return the workflow steps executed to produce this result."""
        if self._workflow_context is not None:
            return tuple(self._workflow_context.steps)
        return ()

    @property
    def response(
        self,
    ) -> AIResponse | RAGResponse:
        """
        Return the underlying AI or RAG response.
        """

        return self._response

    @property
    def is_rag(self) -> bool:
        """Return True if this result was produced by a RAG pipeline."""
        return hasattr(self._response, "attributions") or hasattr(self._response, "diagnostics")

    @property
    def content(
        self,
    ) -> str:
        """
        Return the generated research content.
        """

        return self._response.content

    @property
    def model(
        self,
    ) -> str:
        """
        Return the language model used to
        generate this result.
        """

        return self._response.model

    @property
    def sources(self) -> tuple[str, ...]:
        """Return distinct source names that informed this research result."""
        if hasattr(self._response, "sources"):
            return tuple(self._response.sources)
        return ()

    @property
    def attributions(self) -> tuple[dict[str, Any], ...]:
        """Return structured citations/attributions for this research result."""
        if hasattr(self._response, "attributions"):
            return tuple(self._response.attributions)
        return ()

    @property
    def diagnostics(self) -> dict[str, Any]:
        """Return diagnostics telemetry dictionary."""
        if hasattr(self._response, "diagnostics"):
            return dict(self._response.diagnostics)
        return {}

    @property
    def has_context(self) -> bool:
        """Return True if this research result is supported by knowledge context."""
        if hasattr(self._response, "has_context"):
            return bool(self._response.has_context)
        return False

    @property
    def latency_ms(self) -> float:
        """Return execution latency in milliseconds."""
        if hasattr(self._response, "latency_ms"):
            return float(self._response.latency_ms)
        return 0.0

    @property
    def results(self) -> tuple[RetrievalResult, ...]:
        """Return the retrieval results that grounded this response, if RAG-generated."""
        if hasattr(self._response, "results"):
            return tuple(self._response.results)
        return ()

    def has_content(
        self,
    ) -> bool:
        """
        Check whether research content exists.
        """

        return bool(self.content.strip())

    def is_empty(
        self,
    ) -> bool:
        """
        Check whether this result contains
        no meaningful content.
        """

        return not self.has_content()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert research result into
        dictionary representation.
        """
        d: dict[str, Any] = {
            "content": self.content,
            "model": self.model,
        }
        if self.is_rag:
            d["sources"] = list(self.sources)
            d["attributions"] = list(self.attributions)
            d["has_context"] = self.has_context
            d["latency_ms"] = self.latency_ms
        if self._workflow_context is not None:
            d["workflow_id"] = self._workflow_context.workflow_id
            d["steps"] = [s.name for s in self._workflow_context.steps]
            d["status"] = self._workflow_context.status.name
        if self._report is not None:
            d["report_id"] = self._report.id
            d["report_title"] = self._report.title
        return d

    def __str__(
        self,
    ) -> str:
        """
        Return human-readable representation.
        """

        return self.content

    def __repr__(
        self,
    ) -> str:
        """
        Return developer-friendly representation.
        """

        return (
            f"ResearchResult("
            f"model={self.model!r}, "
            f"content_length={len(self.content)}"
            f")"
        )

    def __bool__(
        self,
    ) -> bool:
        """
        Return whether this result
        contains meaningful content.
        """

        return self.has_content()


__all__ = [
    "ResearchResult",
]
