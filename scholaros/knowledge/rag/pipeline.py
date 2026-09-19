"""
ScholarOS
RAG Pipeline

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates Retrieval-Augmented
Generation using the existing
retrieval and LLM abstractions.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from scholaros.ai.llm.base import (
    LLM,
)
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.knowledge.rag.configuration import (
    RAGConfiguration,
)
from scholaros.knowledge.rag.context import (
    RAGContext,
)
from scholaros.knowledge.rag.events import (
    RAGCompleted,
    RAGFailed,
    RAGFallbackTriggered,
    RAGStarted,
)
from scholaros.knowledge.rag.request import (
    RAGRequest,
)
from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.observability.context import (
    TraceContext,
    get_current_trace,
)
from scholaros.observability.registry import (
    DiagnosticsRegistry,
)
from scholaros.observability.telemetry import (
    TelemetryCollector,
)
from scholaros.observability.trace import (
    RAGTrace,
    RetrievedChunkTrace,
)
from scholaros.retrieval.pipeline import (
    RetrievalPipeline,
)

if TYPE_CHECKING:
    from scholaros.events.bus import EventBus
    from scholaros.retrieval.manager import RetrievalManager


class RAGPipeline:
    """
    Coordinates the RAG pipeline.
    """

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        llm: LLM,
        system_prompt: str | None = None,
        fallback_on_empty: bool = False,
        empty_fallback_message: str | None = None,
        event_bus: EventBus | None = None,
        config: RAGConfiguration | None = None,
    ) -> None:
        """
        Initialize the RAG pipeline.
        """

        self._retrieval_pipeline = (
            retrieval_pipeline
        )

        self._llm = llm
        self._system_prompt = system_prompt
        self._fallback_on_empty = fallback_on_empty
        self._empty_fallback_message = (
            empty_fallback_message
            or "No relevant knowledge context was found to answer this question."
        )
        self._event_bus = event_bus
        self._config = config or RAGConfiguration()

    @classmethod
    def from_manager(
        cls,
        manager: RetrievalManager,
        llm: LLM,
        strategy: str = "default",
        system_prompt: str | None = None,
        fallback_on_empty: bool = False,
        empty_fallback_message: str | None = None,
        event_bus: EventBus | None = None,
        config: RAGConfiguration | None = None,
    ) -> RAGPipeline:
        """
        Create a RAGPipeline using a configured RetrievalManager.
        """
        strat = strategy if strategy != "default" else (config.default_strategy if config else "default")
        pipeline = manager.create_pipeline(strategy=strat)
        return cls(
            retrieval_pipeline=pipeline,
            llm=llm,
            system_prompt=system_prompt,
            fallback_on_empty=fallback_on_empty,
            empty_fallback_message=empty_fallback_message,
            event_bus=event_bus,
            config=config,
        )

    @property
    def retrieval_pipeline(
        self,
    ) -> RetrievalPipeline:
        """
        Return the retrieval pipeline.
        """

        return self._retrieval_pipeline

    @property
    def llm(
        self,
    ) -> LLM:
        """
        Return the configured LLM.
        """

        return self._llm

    @property
    def system_prompt(self) -> str | None:
        """
        Return the default system prompt, if configured.
        """
        return self._system_prompt

    @property
    def fallback_on_empty(self) -> bool:
        """
        Return True if this pipeline should fallback when retrieval yields empty context.
        """
        return self._fallback_on_empty

    @property
    def empty_fallback_message(self) -> str:
        """
        Return the fallback message used when retrieval yields empty context.
        """
        return self._empty_fallback_message

    @property
    def event_bus(self) -> EventBus | None:
        """Return the attached EventBus, if configured."""
        return self._event_bus

    @property
    def config(self) -> RAGConfiguration:
        """Return the RAG configuration."""
        return self._config

    def _publish_event(self, event: Any) -> None:
        """Helper to publish an event if event_bus is present and enabled."""
        if self._event_bus is not None and self._config.enable_events:
            try:
                self._event_bus.publish(event)
            except Exception:
                # Event publishing failure must never break execution
                pass

    def run(
        self,
        request: RAGRequest,
    ) -> RAGResponse:
        """
        Execute the RAG pipeline.
        """
        start_time = time.perf_counter()
        trace_ctx = get_current_trace() or TraceContext(
            name="rag_run",
            tags={"query": request.query, "strategy": request.strategy},
        )

        self._publish_event(
            RAGStarted(
                query=request.query,
                strategy=request.strategy,
                limit=request.limit,
                max_tokens=request.max_tokens,
                correlation_id=trace_ctx.trace_id,
            )
        )

        retrieval_elapsed_ms = 0.0
        try:
            t_retrieval_start = time.perf_counter()
            retrieval_context = None
            if hasattr(self._retrieval_pipeline, "execute") and (
                request.strategy != "default"
                or request.collections is not None
                or request.filters is not None
                or request.limit != 10
                or request.max_tokens is not None
                or bool(request.options)
            ):
                results, retrieval_context = (
                    self._retrieval_pipeline.execute(
                        request.to_retrieval_query(),
                        build_context=True,
                    )
                )
            else:
                results = (
                    self._retrieval_pipeline.run(
                        request.query,
                        request.minimum_score,
                    )
                )
            retrieval_elapsed_ms = (time.perf_counter() - t_retrieval_start) * 1000.0

            if retrieval_context is not None:
                context = RAGContext.from_retrieval_context(
                    retrieval_context,
                    query=request.query,
                )
            else:
                context = RAGContext(
                    results,
                    query=request.query,
                    max_tokens=request.max_tokens,
                )

            fallback_active = (
                len(context) == 0
                and (
                    request.fallback_on_empty
                    or self._fallback_on_empty
                    or bool(request.options.get("fallback_on_empty"))
                )
            )

            if fallback_active:
                fallback_text = (
                    request.empty_fallback_message
                    or self._empty_fallback_message
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                metadata = {
                    "strategy": request.strategy,
                    "query": request.query,
                    "latency_ms": elapsed_ms,
                    "results_count": 0,
                    "has_context": False,
                    "empty_fallback": True,
                    "trace_id": trace_ctx.trace_id,
                }
                self._publish_event(
                    RAGFallbackTriggered(
                        query=request.query,
                        reason="empty_context",
                        correlation_id=trace_ctx.trace_id,
                    )
                )
                self._publish_event(
                    RAGCompleted(
                        query=request.query,
                        strategy=request.strategy,
                        model="fallback",
                        results_count=0,
                        latency_ms=elapsed_ms,
                        correlation_id=trace_ctx.trace_id,
                    )
                )
                trace = RAGTrace(
                    trace_id=trace_ctx.trace_id,
                    query=request.query,
                    strategy=request.strategy,
                    retrieved_chunks=[],
                    scores=[],
                    context_text=context.text,
                    context_tokens=context.token_count,
                    system_prompt=self._system_prompt,
                    formatted_prompt="",
                    model="fallback",
                    response_content=fallback_text,
                    retrieval_latency_ms=retrieval_elapsed_ms,
                    total_latency_ms=elapsed_ms,
                    fallback_triggered=True,
                    fallback_reason="empty_context",
                    metadata=metadata,
                )
                DiagnosticsRegistry.get_default().record(trace)
                TelemetryCollector.get_default().record_query(
                    latency_ms=elapsed_ms,
                    retrieval_ms=retrieval_elapsed_ms,
                    success=True,
                    fallback=True,
                )
                return RAGResponse(
                    content=fallback_text,
                    model="fallback",
                    results=(),
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    context=context,
                    metadata=metadata,
                    latency_ms=elapsed_ms,
                )

            messages = self._build_messages(
                request,
                context,
            )

            t_llm_start = time.perf_counter()
            response = self._llm.generate(
                messages,
            )
            llm_elapsed_ms = (time.perf_counter() - t_llm_start) * 1000.0
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = {
                "strategy": request.strategy,
                "query": request.query,
                "latency_ms": elapsed_ms,
                "results_count": len(context.results),
                "has_context": len(context.results) > 0,
                "trace_id": trace_ctx.trace_id,
            }

            self._publish_event(
                RAGCompleted(
                    query=request.query,
                    strategy=request.strategy,
                    model=response.model,
                    results_count=len(context.results),
                    latency_ms=elapsed_ms,
                    correlation_id=trace_ctx.trace_id,
                )
            )

            retrieved_chunks = [
                RetrievedChunkTrace(
                    document_id=str(getattr(r, "document_id", None) or (getattr(getattr(r, "chunk", None), "document_id", None)) or "unknown"),
                    chunk_id=str(getattr(r, "chunk_id", None) or getattr(getattr(r, "chunk", None), "identifier", None) or getattr(r, "source", "unknown")),
                    score=float(getattr(r, "score", 0.0)),
                    content_snippet=str(getattr(r, "content", None) or getattr(getattr(r, "chunk", None), "content", "")),
                    source=str(getattr(r, "source", None) or getattr(getattr(r, "chunk", None), "source", None) or "") or None,
                    metadata=dict(getattr(r, "metadata", None) or getattr(getattr(r, "chunk", None), "metadata", {})),
                )
                for r in context.results
            ]

            trace = RAGTrace(
                trace_id=trace_ctx.trace_id,
                query=request.query,
                strategy=request.strategy,
                retrieved_chunks=retrieved_chunks,
                scores=[r.score for r in context.results],
                context_text=context.text,
                context_tokens=context.token_count,
                system_prompt=messages[0].content if len(messages) > 1 else None,
                formatted_prompt=messages[1].content if len(messages) > 1 else (messages[0].content if messages else ""),
                model=response.model,
                response_content=response.content,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                retrieval_latency_ms=retrieval_elapsed_ms,
                llm_latency_ms=llm_elapsed_ms,
                total_latency_ms=elapsed_ms,
                metadata=metadata,
            )
            DiagnosticsRegistry.get_default().record(trace)
            TelemetryCollector.get_default().record_query(
                latency_ms=elapsed_ms,
                retrieval_ms=retrieval_elapsed_ms,
                llm_ms=llm_elapsed_ms,
                success=True,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
            )

            return RAGResponse(
                content=response.content,
                model=response.model,
                results=context.results,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                context=context,
                metadata=metadata,
                latency_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            trace = RAGTrace(
                trace_id=trace_ctx.trace_id,
                query=request.query,
                strategy=request.strategy,
                total_latency_ms=elapsed_ms,
                error=str(e),
                metadata={"strategy": request.strategy, "query": request.query, "trace_id": trace_ctx.trace_id},
            )
            DiagnosticsRegistry.get_default().record(trace)
            TelemetryCollector.get_default().record_query(
                latency_ms=elapsed_ms,
                success=False,
            )
            self._publish_event(
                RAGFailed(
                    query=request.query,
                    strategy=request.strategy,
                    error=str(e),
                    latency_ms=elapsed_ms,
                    correlation_id=trace_ctx.trace_id,
                )
            )
            raise

    def execute(
        self,
        request: RAGRequest | str,
    ) -> RAGResponse:
        """
        Execute the full multi-stage RAG pipeline.
        """
        start_time = time.perf_counter()
        req = (
            request
            if isinstance(request, RAGRequest)
            else RAGRequest(query=request)
        )
        trace_ctx = get_current_trace() or TraceContext(
            name="rag_execute",
            tags={"query": req.query, "strategy": req.strategy},
        )

        self._publish_event(
            RAGStarted(
                query=req.query,
                strategy=req.strategy,
                limit=req.limit,
                max_tokens=req.max_tokens,
                correlation_id=trace_ctx.trace_id,
            )
        )

        retrieval_elapsed_ms = 0.0
        try:
            t_retrieval_start = time.perf_counter()
            retrieval_context = None
            if hasattr(self._retrieval_pipeline, "execute"):
                results, retrieval_context = self._retrieval_pipeline.execute(
                    req.to_retrieval_query(),
                    build_context=True,
                )
            else:
                results = self._retrieval_pipeline.run(
                    req.query,
                    req.minimum_score,
                )
            retrieval_elapsed_ms = (time.perf_counter() - t_retrieval_start) * 1000.0

            if retrieval_context is not None:
                context = RAGContext.from_retrieval_context(
                    retrieval_context,
                    query=req.query,
                )
            else:
                context = RAGContext(
                    results,
                    query=req.query,
                    max_tokens=req.max_tokens,
                )

            fallback_active = (
                len(context) == 0
                and (
                    req.fallback_on_empty
                    or self._fallback_on_empty
                    or bool(req.options.get("fallback_on_empty"))
                )
            )

            if fallback_active:
                fallback_text = (
                    req.empty_fallback_message
                    or self._empty_fallback_message
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                metadata = {
                    "strategy": req.strategy,
                    "query": req.query,
                    "latency_ms": elapsed_ms,
                    "results_count": 0,
                    "has_context": False,
                    "empty_fallback": True,
                    "trace_id": trace_ctx.trace_id,
                }
                self._publish_event(
                    RAGFallbackTriggered(
                        query=req.query,
                        reason="empty_context",
                        correlation_id=trace_ctx.trace_id,
                    )
                )
                self._publish_event(
                    RAGCompleted(
                        query=req.query,
                        strategy=req.strategy,
                        model="fallback",
                        results_count=0,
                        latency_ms=elapsed_ms,
                        correlation_id=trace_ctx.trace_id,
                    )
                )
                trace = RAGTrace(
                    trace_id=trace_ctx.trace_id,
                    query=req.query,
                    strategy=req.strategy,
                    retrieved_chunks=[],
                    scores=[],
                    context_text=context.text,
                    context_tokens=context.token_count,
                    system_prompt=self._system_prompt,
                    formatted_prompt="",
                    model="fallback",
                    response_content=fallback_text,
                    retrieval_latency_ms=retrieval_elapsed_ms,
                    total_latency_ms=elapsed_ms,
                    fallback_triggered=True,
                    fallback_reason="empty_context",
                    metadata=metadata,
                )
                DiagnosticsRegistry.get_default().record(trace)
                TelemetryCollector.get_default().record_query(
                    latency_ms=elapsed_ms,
                    retrieval_ms=retrieval_elapsed_ms,
                    success=True,
                    fallback=True,
                )
                return RAGResponse(
                    content=fallback_text,
                    model="fallback",
                    results=(),
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    context=context,
                    metadata=metadata,
                    latency_ms=elapsed_ms,
                )

            messages = self._build_messages(req, context)
            t_llm_start = time.perf_counter()
            response = self._llm.generate(messages)
            llm_elapsed_ms = (time.perf_counter() - t_llm_start) * 1000.0
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            metadata = {
                "strategy": req.strategy,
                "query": req.query,
                "latency_ms": elapsed_ms,
                "results_count": len(context.results),
                "has_context": len(context.results) > 0,
                "trace_id": trace_ctx.trace_id,
            }

            self._publish_event(
                RAGCompleted(
                    query=req.query,
                    strategy=req.strategy,
                    model=response.model,
                    results_count=len(context.results),
                    latency_ms=elapsed_ms,
                    correlation_id=trace_ctx.trace_id,
                )
            )

            retrieved_chunks = [
                RetrievedChunkTrace(
                    document_id=str(getattr(r, "document_id", None) or (getattr(getattr(r, "chunk", None), "document_id", None)) or "unknown"),
                    chunk_id=str(getattr(r, "chunk_id", None) or getattr(getattr(r, "chunk", None), "identifier", None) or getattr(r, "source", "unknown")),
                    score=float(getattr(r, "score", 0.0)),
                    content_snippet=str(getattr(r, "content", None) or getattr(getattr(r, "chunk", None), "content", "")),
                    source=str(getattr(r, "source", None) or getattr(getattr(r, "chunk", None), "source", None) or "") or None,
                    metadata=dict(getattr(r, "metadata", None) or getattr(getattr(r, "chunk", None), "metadata", {})),
                )
                for r in context.results
            ]

            trace = RAGTrace(
                trace_id=trace_ctx.trace_id,
                query=req.query,
                strategy=req.strategy,
                retrieved_chunks=retrieved_chunks,
                scores=[r.score for r in context.results],
                context_text=context.text,
                context_tokens=context.token_count,
                system_prompt=messages[0].content if len(messages) > 1 else None,
                formatted_prompt=messages[1].content if len(messages) > 1 else (messages[0].content if messages else ""),
                model=response.model,
                response_content=response.content,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                retrieval_latency_ms=retrieval_elapsed_ms,
                llm_latency_ms=llm_elapsed_ms,
                total_latency_ms=elapsed_ms,
                metadata=metadata,
            )
            DiagnosticsRegistry.get_default().record(trace)
            TelemetryCollector.get_default().record_query(
                latency_ms=elapsed_ms,
                retrieval_ms=retrieval_elapsed_ms,
                llm_ms=llm_elapsed_ms,
                success=True,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
            )

            return RAGResponse(
                content=response.content,
                model=response.model,
                results=context.results,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                context=context,
                metadata=metadata,
                latency_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            trace = RAGTrace(
                trace_id=trace_ctx.trace_id,
                query=req.query,
                strategy=req.strategy,
                total_latency_ms=elapsed_ms,
                error=str(e),
                metadata={"strategy": req.strategy, "query": req.query, "trace_id": trace_ctx.trace_id},
            )
            DiagnosticsRegistry.get_default().record(trace)
            TelemetryCollector.get_default().record_query(
                latency_ms=elapsed_ms,
                success=False,
            )
            self._publish_event(
                RAGFailed(
                    query=req.query,
                    strategy=req.strategy,
                    error=str(e),
                    latency_ms=elapsed_ms,
                    correlation_id=trace_ctx.trace_id,
                )
            )
            raise

    def _build_messages(
        self,
        request: RAGRequest,
        context: RAGContext,
    ) -> list[Message]:
        """
        Build the messages supplied to
        the configured LLM.
        """

        if request.system_prompt is not None:
            system_content = request.system_prompt
        elif self._system_prompt is not None:
            system_content = self._system_prompt
        else:
            system_content = (
                "You are a research assistant "
                "for ScholarOS. Answer the "
                "user's question using the "
                "provided knowledge context. "
                "If the context does not "
                "contain sufficient information "
                "to answer the question, say so "
                "instead of inventing facts."
            )

        secure_mode = (
            bool(request.options.get("secure_context"))
            or bool(request.options.get("security_mode"))
            or bool(getattr(self._config, "extra_options", {}).get("secure_context"))
        )

        if secure_mode:
            from scholaros.security.rag import format_secure_rag_context

            directive, user_content = format_secure_rag_context(context, request.query)
            if len(context.results) > 0:
                system_content = f"{system_content}\n\n{directive}"
        else:
            user_content = (
                "Knowledge Context:\n"
                f"{context.text}\n\n"
                "User Question:\n"
                f"{request.query}"
            )

        return [
            Message(
                role=MessageRole.SYSTEM,
                content=system_content,
            ),
            Message(
                role=MessageRole.USER,
                content=user_content,
            ),
        ]

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the pipeline.
        """

        return (
            f"{self.__class__.__name__}("
            f"llm={self.llm!r}"
            f")"
        )


__all__ = [
    "RAGPipeline",
]
