"""
ScholarOS Research Workflow Engine.

Orchestrates multi-stage research workflows:
Request -> Planning -> Multi-Query Retrieval -> Evidence Analysis -> Synthesis -> Report & Memory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import uuid4

from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.planner.research_planner import ResearchPlan, ResearchPlanner
from scholaros.research.citation import Citation
from scholaros.research.events import (
    ResearchCancelled,
    ResearchCompleted,
    ResearchFailed,
    ResearchStarted,
)
from scholaros.research.exceptions import ResearchExecutionError
from scholaros.research.report import Report
from scholaros.research.result import ResearchResult
from scholaros.retrieval.result import RetrievalResult
from scholaros.workflow.state import WorkflowContext, WorkflowStatus

if TYPE_CHECKING:
    from scholaros.events.bus import EventBus
    from scholaros.execution.workflow_executor import WorkflowExecutor
    from scholaros.knowledge.rag.pipeline import RAGPipeline
    from scholaros.knowledge.rag.service import RAGService
    from scholaros.memory.manager import MemoryManager


class ResearchWorkflowEngine:
    """
    Coordinates end-to-end multi-step research execution.
    """

    def __init__(
        self,
        rag: RAGService | RAGPipeline,
        planner: ResearchPlanner | None = None,
        executor: WorkflowExecutor | None = None,
        memory: MemoryManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._rag = rag
        self._planner = planner or ResearchPlanner()
        if executor is None:
            from scholaros.execution.workflow_executor import WorkflowExecutor as DefaultExecutor

            self._executor = DefaultExecutor(event_bus=event_bus)
        else:
            self._executor = executor
        self._memory = memory
        self._event_bus = event_bus
        self._active_context: WorkflowContext | None = None

    @property
    def rag(self) -> RAGService | RAGPipeline:
        """Return the configured RAG service or pipeline."""
        return self._rag

    @property
    def planner(self) -> ResearchPlanner:
        """Return the research planner."""
        return self._planner

    @property
    def executor(self) -> WorkflowExecutor:
        """Return the workflow executor."""
        return self._executor

    @property
    def memory(self) -> MemoryManager | None:
        """Return the memory manager if configured."""
        return self._memory

    @property
    def event_bus(self) -> EventBus | None:
        """Return the attached EventBus if configured."""
        return self._event_bus

    @property
    def active_context(self) -> WorkflowContext | None:
        """Return the active workflow context if executing."""
        return self._active_context

    def cancel_active(self, reason: str = "User requested cancellation") -> bool:
        """Signal cancellation for the actively executing workflow."""
        if self._active_context is not None and not self._active_context.is_cancelled:
            self._active_context.cancel(reason)
            return True
        return False

    def execute(
        self,
        query: str,
        strategy: str = "default",
        limit_per_query: int = 5,
        collections: list[str] | None = None,
        record_memory: bool = True,
        initial_data: dict[str, Any] | None = None,
    ) -> ResearchResult:
        """
        Execute a full multi-stage research workflow.
        """
        context = WorkflowContext(
            workflow_id=str(uuid4()),
            query=query,
            data=initial_data.copy() if initial_data else {},
            status=WorkflowStatus.EXECUTING,
        )
        self._active_context = context

        if self._event_bus is not None:
            try:
                self._event_bus.publish(ResearchStarted(query=query, strategy=strategy))
            except Exception:
                pass

        try:
            # 1. Planning Stage
            def _stage_plan(ctx: WorkflowContext) -> dict[str, Any]:
                ctx.status = WorkflowStatus.PLANNING
                plan = self._planner.create_plan(
                    query=ctx.query,
                    strategy=strategy,
                    limit_per_query=limit_per_query,
                    collections=collections,
                )
                return {"plan": plan}

            self._executor.execute_stage("planning", _stage_plan, context)
            if context.is_cancelled:
                return self._handle_cancellation(context)

            # 2. Retrieval Stage
            def _stage_retrieve(ctx: WorkflowContext) -> dict[str, Any]:
                ctx.status = WorkflowStatus.RETRIEVING
                plan: ResearchPlan = ctx.data["plan"]
                all_results: list[RetrievalResult] = []
                seen_doc_ids: set[str] = set()

                for sub_q in plan.sub_questions:
                    if ctx.is_cancelled:
                        break
                    rag_req = RAGRequest(
                        query=sub_q,
                        strategy=plan.strategy,
                        limit=plan.limit_per_query,
                        collections=plan.collections,
                    )
                    if hasattr(self._rag, "generate"):
                        sub_resp = self._rag.generate(rag_req)
                    else:
                        sub_resp = self._rag.execute(rag_req)

                    for r in getattr(sub_resp, "results", ()):
                        doc_id = (
                            str(getattr(r.document, "id", None) or id(r))
                            if hasattr(r, "document")
                            else str(id(r))
                        )
                        if doc_id not in seen_doc_ids:
                            seen_doc_ids.add(doc_id)
                            all_results.append(r)

                return {"results": all_results}

            self._executor.execute_stage("retrieval", _stage_retrieve, context)
            if context.is_cancelled:
                return self._handle_cancellation(context)

            # 3. Evidence Analysis Stage
            def _stage_analyze(ctx: WorkflowContext) -> dict[str, Any]:
                ctx.status = WorkflowStatus.ANALYZING
                results: list[RetrievalResult] = ctx.data.get("results", [])
                evidence_summary = {
                    "total_sources": len(results),
                    "document_ids": [
                        getattr(r.document, "id", str(i))
                        for i, r in enumerate(results)
                        if hasattr(r, "document")
                    ],
                }
                return {"analysis": evidence_summary}

            self._executor.execute_stage("analysis", _stage_analyze, context)
            if context.is_cancelled:
                return self._handle_cancellation(context)

            # 4. Synthesis Stage
            def _stage_synthesize(ctx: WorkflowContext) -> dict[str, Any]:
                ctx.status = WorkflowStatus.SYNTHESIZING
                plan: ResearchPlan = ctx.data["plan"]
                results: list[RetrievalResult] = ctx.data.get("results", [])

                # Run main synthesis through RAG
                synthesis_req = RAGRequest(
                    query=ctx.query,
                    strategy=plan.strategy,
                    limit=max(len(results), 1),
                    collections=plan.collections,
                )
                if hasattr(self._rag, "generate"):
                    synthesis_resp = self._rag.generate(synthesis_req)
                else:
                    synthesis_resp = self._rag.execute(synthesis_req)

                citations: list[Citation] = []
                for r in results:
                    if hasattr(r, "document"):
                        title = getattr(r.document, "title", r.document.id)
                        source = getattr(r.document, "source", "ScholarOS Knowledge Base")
                        url = getattr(r.document, "url", None)
                    else:
                        title = str(r)
                        source = "Knowledge Base"
                        url = None
                    citations.append(Citation(title=title, source=source, url=url))

                report = Report(
                    title=f"Research Report: {ctx.query}",
                    content=synthesis_resp.content,
                    citations=citations,
                )
                return {
                    "synthesis_response": synthesis_resp,
                    "report": report,
                    "citations": citations,
                }

            self._executor.execute_stage("synthesis", _stage_synthesize, context)
            if context.is_cancelled:
                return self._handle_cancellation(context)

            # 5. Memory Recording (optional)
            if self._memory is not None and record_memory:
                self._record_to_memory(context)

            context.status = WorkflowStatus.COMPLETED
            synthesis_resp: RAGResponse = context.data["synthesis_response"]
            report: Report = context.data["report"]
            plan: ResearchPlan = context.data["plan"]

            if self._event_bus is not None:
                try:
                    self._event_bus.publish(
                        ResearchCompleted(
                            query=query,
                            model=synthesis_resp.model,
                            sources_count=len(report.citations),
                            latency_ms=context.get_elapsed_ms(),
                        )
                    )
                except Exception:
                    pass

            return ResearchResult(
                response=synthesis_resp,
                report=report,
                workflow_context=context,
                plan=plan,
            )

        except Exception as exc:
            context.status = WorkflowStatus.FAILED
            elapsed_ms = context.get_elapsed_ms()
            if self._event_bus is not None:
                try:
                    self._event_bus.publish(
                        ResearchFailed(query=query, error=str(exc), latency_ms=elapsed_ms)
                    )
                except Exception:
                    pass
            if isinstance(exc, ResearchExecutionError):
                raise
            raise ResearchExecutionError(f"Research workflow execution failed: {exc}") from exc
        finally:
            self._active_context = None

    def _handle_cancellation(self, context: WorkflowContext) -> ResearchResult:
        """Produce a cancelled ResearchResult and publish cancellation event."""
        context.status = WorkflowStatus.CANCELLED
        elapsed_ms = context.get_elapsed_ms()
        if self._event_bus is not None:
            try:
                self._event_bus.publish(
                    ResearchCancelled(
                        query=context.query,
                        reason=context.cancel_reason or "Cancelled",
                        latency_ms=elapsed_ms,
                        workflow_id=context.workflow_id,
                    )
                )
            except Exception:
                pass

        cancelled_resp = RAGResponse(
            content=f"[Workflow Cancelled] {context.cancel_reason or 'Operation was cancelled'}",
            model="cancelled",
            results=[],
            metadata={
                "cancelled": True,
                "reason": context.cancel_reason,
                "workflow_id": context.workflow_id,
            },
            latency_ms=elapsed_ms,
        )
        return ResearchResult(
            response=cancelled_resp,
            report=None,
            workflow_context=context,
            plan=context.data.get("plan"),
        )

    def _record_to_memory(self, context: WorkflowContext) -> None:
        """Optionally record the research findings to MemoryManager."""
        if self._memory is None:
            return
        try:
            col = self._memory.get("research_history")
            if col is None:
                from scholaros.memory.collection import MemoryCollection

                col = MemoryCollection()
                self._memory.register("research_history", col)

            from scholaros.memory.entry import MemoryEntry

            synthesis_resp = context.data.get("synthesis_response")
            content_snippet = synthesis_resp.content[:500] if synthesis_resp else ""
            citations = context.data.get("citations", [])

            entry = MemoryEntry(
                entry_id=str(uuid4()),
                content=f"Query: {context.query}\nSummary: {content_snippet}",
                metadata={
                    "query": context.query,
                    "workflow_id": context.workflow_id,
                    "sources_count": len(citations),
                    "status": context.status.name,
                },
            )
            col.add(entry)
        except Exception:
            pass


__all__ = [
    "ResearchWorkflowEngine",
]
