"""
ScholarOS
Research Pipeline

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates high-level research workflows.

Responsibilities
----------------
• Coordinate AI-powered research tasks
• Delegate prompt execution to AIService (legacy template workflows)
• Delegate grounded knowledge retrieval to RAGService / RAGPipeline
• Serve as the application entry point for research operations
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.research.exceptions import ResearchExecutionError
from scholaros.research.result import ResearchResult

if TYPE_CHECKING:
    from scholaros.ai.ai_service import AIService
    from scholaros.events.bus import EventBus
    from scholaros.knowledge.rag.pipeline import RAGPipeline
    from scholaros.knowledge.rag.request import RAGRequest
    from scholaros.knowledge.rag.service import RAGService
    from scholaros.research.session import ResearchSession
    from scholaros.research.workflow_engine import ResearchWorkflowEngine


class ResearchPipeline:
    """
    Coordinates research workflows.
    """

    def __init__(
        self,
        ai: AIService | None = None,
        rag: RAGService | RAGPipeline | None = None,
        event_bus: EventBus | None = None,
        workflow_engine: ResearchWorkflowEngine | None = None,
    ) -> None:
        """
        Initialize the research pipeline with AI prompt service and/or RAG service.
        """
        if ai is None and rag is None and workflow_engine is None:
            raise ValueError(
                "ResearchPipeline requires either an AIService, a RAGService, or both."
            )

        self._ai = ai
        self._rag = rag
        self._event_bus = event_bus
        self._workflow_engine = workflow_engine

    @classmethod
    def from_rag(
        cls,
        rag: RAGService | RAGPipeline,
        event_bus: EventBus | None = None,
        workflow_engine: ResearchWorkflowEngine | None = None,
    ) -> ResearchPipeline:
        """Create a ResearchPipeline backed by RAG."""
        return cls(rag=rag, event_bus=event_bus, workflow_engine=workflow_engine)

    @classmethod
    def from_ai(
        cls,
        ai: AIService,
        event_bus: EventBus | None = None,
    ) -> ResearchPipeline:
        """Create a ResearchPipeline backed by legacy AIService."""
        return cls(ai=ai, event_bus=event_bus)

    @property
    def event_bus(self) -> EventBus | None:
        """Return the attached EventBus if configured."""
        return self._event_bus

    @property
    def ai(
        self,
    ) -> AIService:
        """
        Return the configured AI service.
        """
        if self._ai is None:
            raise AttributeError("ResearchPipeline was initialized without an AIService.")
        return self._ai

    @property
    def rag(self) -> RAGService | RAGPipeline | None:
        """Return the configured RAG service or pipeline."""
        return self._rag

    @property
    def has_rag(self) -> bool:
        """Return True if RAG capabilities are available."""
        return self._rag is not None

    @property
    def has_ai(self) -> bool:
        """Return True if AI template capabilities are available."""
        return self._ai is not None

    @property
    def workflow_engine(self) -> ResearchWorkflowEngine | None:
        """Return the workflow engine if available or lazily created from RAG."""
        if self._workflow_engine is None and self._rag is not None:
            from scholaros.research.workflow_engine import ResearchWorkflowEngine

            self._workflow_engine = ResearchWorkflowEngine(
                rag=self._rag,
                event_bus=self._event_bus,
            )
        return self._workflow_engine

    def execute(
        self,
        template: str,
        **variables: Any,
    ) -> Any:
        """
        Execute a research prompt or RAG query.

        If template is found in configured AIService, executes via prompt template.
        Otherwise, if RAG is available, treats template as a research query.
        """
        if self._ai is not None and self._ai.contains(template):
            return self._ai.execute(
                template,
                **variables,
            )

        if (variables.pop("use_workflow", False) or variables.pop("workflow", False)) and hasattr(
            self, "execute_workflow"
        ):
            return self.execute_workflow(template, **variables)

        if self._rag is not None:
            return self.execute_rag(template, **variables)

        if self._ai is not None:
            # Fallback to AI service to preserve exact error behavior
            return self._ai.execute(
                template,
                **variables,
            )

        raise ResearchExecutionError(f"No execution engine available for task '{template}'.")

    def execute_rag(
        self,
        query: str | RAGRequest,
        strategy: str = "default",
        limit: int = 10,
        min_score: float = 0.0,
        max_tokens: int | None = None,
        collections: list[str] | None = None,
        session: ResearchSession | None = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """
        Execute a grounded research query through the RAG subsystem.
        """
        if self._rag is None:
            raise ResearchExecutionError(
                "ResearchPipeline has no RAG service or pipeline configured."
            )

        import time
        from scholaros.knowledge.rag.request import RAGRequest
        from scholaros.knowledge.rag.service import RAGService
        from scholaros.research.events import (
            ResearchCompleted,
            ResearchFailed,
            ResearchStarted,
        )

        if session is not None and "session_context" not in kwargs:
            s_ctx = session.get_conversation_context()
            if s_ctx:
                kwargs["session_context"] = s_ctx

        if isinstance(query, RAGRequest):
            rag_req = query
        else:
            rag_req = RAGRequest(
                query=query,
                strategy=strategy,
                limit=limit,
                minimum_score=min_score,
                max_tokens=max_tokens,
                collections=collections,
                options=kwargs,
            )

        if self._event_bus is not None:
            try:
                self._event_bus.publish(
                    ResearchStarted(query=rag_req.query, strategy=rag_req.strategy)
                )
            except Exception:
                pass

        start_time = time.perf_counter()
        try:
            if isinstance(self._rag, RAGService):
                rag_response = self._rag.generate(rag_req)
            else:
                rag_response = self._rag.execute(rag_req)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            result = ResearchResult.from_rag_response(rag_response)

            if session is not None:
                session.record_interaction(query=rag_req.query, result=result)

            if self._event_bus is not None:
                try:
                    self._event_bus.publish(
                        ResearchCompleted(
                            query=rag_req.query,
                            model=result.model,
                            sources_count=len(result.sources),
                            latency_ms=elapsed_ms,
                        )
                    )
                except Exception:
                    pass

            return result

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if self._event_bus is not None:
                try:
                    self._event_bus.publish(
                        ResearchFailed(
                            query=rag_req.query,
                            error=str(e),
                            latency_ms=elapsed_ms,
                        )
                    )
                except Exception:
                    pass
            if isinstance(e, ResearchExecutionError):
                raise
            raise ResearchExecutionError(f"Research execution failed: {e}") from e

    def execute_workflow(
        self,
        query: str,
        strategy: str = "default",
        limit_per_query: int = 5,
        collections: list[str] | None = None,
        record_memory: bool = True,
        initial_data: dict[str, Any] | None = None,
        session: ResearchSession | None = None,
    ) -> ResearchResult:
        """
        Execute a full multi-stage research workflow (Plan -> Retrieve -> Analyze -> Synthesize).
        """
        if self.workflow_engine is None:
            raise ResearchExecutionError(
                "ResearchPipeline cannot execute workflow: no RAG service or workflow engine configured."
            )
        init_dict: dict[str, Any] = dict(initial_data) if initial_data else {}
        if session is not None:
            s_ctx = session.get_conversation_context()
            if s_ctx and "session_context" not in init_dict:
                init_dict["session_context"] = s_ctx
            if "session_id" not in init_dict:
                init_dict["session_id"] = session.id

        result = self.workflow_engine.execute(
            query=query,
            strategy=strategy,
            limit_per_query=limit_per_query,
            collections=collections,
            record_memory=record_memory,
            initial_data=init_dict,
        )
        if session is not None:
            session.record_interaction(query=query, result=result)
        return result

    def cancel_active_workflow(self, reason: str = "User requested cancellation") -> bool:
        """Cancel the currently active workflow if supported by workflow engine."""
        if self._workflow_engine is not None and hasattr(self._workflow_engine, "cancel_active"):
            return self._workflow_engine.cancel_active(reason)
        return False

    def build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a research prompt without
        executing it.
        """
        if self._ai is None:
            raise AttributeError(
                "ResearchPipeline has no AIService configured for building templates."
            )

        return self._ai.build(
            template,
            **variables,
        )

    def contains(
        self,
        template: str,
    ) -> bool:
        """
        Returns True if the specified research
        prompt template exists.
        """
        if self._ai is None:
            return False

        return self._ai.contains(
            template,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the ResearchPipeline.
        """
        parts: list[str] = []
        if self._ai is not None:
            parts.append(f"ai={self._ai!r}")
        if self._rag is not None:
            parts.append(f"rag={self._rag!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


__all__ = [
    "ResearchPipeline",
]
