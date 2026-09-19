"""
ScholarOS Observability Subsystem - Production Verification Test Suite.

Verifies end-to-end trace capture, diagnostics registry ring buffer, telemetry percentiles,
structured JSON logging, multi-subsystem health aggregation, and pipeline integration.
"""

from __future__ import annotations

import json
import logging
import time
from unittest.mock import MagicMock


from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.events.bus import EventBus
from scholaros.gui.application import GUIApplication
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.retrieval.result import RetrievalResult
from scholaros.observability import (
    DiagnosticsRegistry,
    RAGTrace,
    RetrievedChunkTrace,
    StructuredJsonFormatter,
    SystemHealthAggregator,
    TelemetryCollector,
    TelemetryEventSubscriber,
    TraceContext,
    get_current_trace,
    trace_scope,
)
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.security.logging import SensitiveDataFilter
from scholaros.services.health import HealthStatus, ServiceHealth


# ===========================================================================
# 1. Trace Context & Distributed Scope Tests
# ===========================================================================


def test_trace_context_creation_and_span_nesting() -> None:
    root = TraceContext(name="root_op", tags={"env": "test"})
    assert root.trace_id is not None
    assert len(root.span_id) == 8
    assert root.parent_span_id is None
    assert root.tags["env"] == "test"
    time.sleep(0.005)
    assert root.elapsed_ms() > 0

    child = root.new_span("child_op", tags={"step": 1})
    assert child.trace_id == root.trace_id
    assert child.parent_span_id == root.span_id
    assert child.span_id != root.span_id
    assert child.tags["env"] == "test"
    assert child.tags["step"] == 1

    d = child.to_dict()
    assert d["trace_id"] == root.trace_id
    assert d["parent_span_id"] == root.span_id
    assert d["name"] == "child_op"


def test_trace_scope_contextvar_propagation() -> None:
    assert get_current_trace() is None

    with trace_scope("outer_scope", tags={"service": "research"}) as outer:
        assert get_current_trace() is outer
        assert outer.name == "outer_scope"

        with trace_scope("inner_scope", tags={"step": "retrieval"}) as inner:
            assert get_current_trace() is inner
            assert inner.trace_id == outer.trace_id
            assert inner.parent_span_id == outer.span_id
            assert inner.tags["service"] == "research"
            assert inner.tags["step"] == "retrieval"

        assert get_current_trace() is outer

    assert get_current_trace() is None


# ===========================================================================
# 2. RAG Diagnostic Trace & Markdown Generation Tests
# ===========================================================================


def test_rag_trace_to_dict_and_markdown() -> None:
    chunk1 = RetrievedChunkTrace(
        document_id="doc_alpha",
        chunk_id="chunk_1",
        score=0.9254,
        content_snippet="ScholarOS uses an autonomous pipeline architecture.",
        source="spec.pdf",
    )
    chunk2 = RetrievedChunkTrace(
        document_id="doc_beta",
        chunk_id="chunk_2",
        score=0.8123,
        content_snippet="Knowledge retrieval integrates with vector stores.",
        source="arch.md",
    )

    trace = RAGTrace(
        trace_id="trace-test-12345",
        query="Explain ScholarOS architecture",
        strategy="hybrid",
        retrieved_chunks=[chunk1, chunk2],
        scores=[0.9254, 0.8123],
        context_text="ScholarOS uses an autonomous pipeline architecture.\nKnowledge retrieval integrates with vector stores.",
        context_tokens=32,
        system_prompt="You are a research assistant.",
        formatted_prompt="User Question:\nExplain ScholarOS architecture",
        model="llama3:8b",
        response_content="ScholarOS is an autonomous research operating system.",
        prompt_tokens=150,
        completion_tokens=40,
        total_tokens=190,
        retrieval_latency_ms=45.2,
        llm_latency_ms=120.8,
        total_latency_ms=166.0,
    )

    assert trace.is_success is True
    assert trace.chunks_count == 2

    # Check to_dict
    data = trace.to_dict()
    assert data["trace_id"] == "trace-test-12345"
    assert data["tokens"]["total"] == 190
    assert data["latencies_ms"]["total"] == 166.0
    assert len(data["retrieved_chunks"]) == 2

    # Check to_markdown output answers "The research answer is wrong"
    md = trace.to_markdown()
    assert "# RAG Diagnostic Trace: `trace-test-12345`" in md
    assert "Explain ScholarOS architecture" in md
    assert "llama3:8b" in md
    assert "Retrieval" in md
    assert "45.20 ms" in md
    assert "LLM Generation" in md
    assert "120.80 ms" in md
    assert "doc_alpha" in md
    assert "0.9254" in md
    assert "ScholarOS is an autonomous research operating system." in md


def test_rag_trace_error_reporting() -> None:
    trace = RAGTrace(
        trace_id="err-1",
        query="Failed query",
        total_latency_ms=10.0,
        error="Connection timeout to LLM provider",
    )
    assert trace.is_success is False
    md = trace.to_markdown()
    assert "FAILED" in md
    assert "Connection timeout to LLM provider" in md


# ===========================================================================
# 3. Diagnostics Registry Ring Buffer Tests
# ===========================================================================


def test_diagnostics_registry_ring_buffer_and_filtering() -> None:
    registry = DiagnosticsRegistry(capacity=3)

    t1 = RAGTrace(trace_id="t1", query="quantum physics", strategy="dense")
    t2 = RAGTrace(trace_id="t2", query="relativity", strategy="sparse", error="Syntax error")
    t3 = RAGTrace(trace_id="t3", query="quantum computing", strategy="dense")

    registry.record(t1)
    registry.record(t2)
    registry.record(t3)

    assert len(registry) == 3
    assert registry.get("t1") == t1
    assert registry.get("t2") == t2

    # Eviction on overflowing capacity
    t4 = RAGTrace(trace_id="t4", query="thermodynamics", strategy="hybrid")
    registry.record(t4)

    assert len(registry) == 3
    assert registry.get("t1") is None  # Evicted
    assert registry.get("t4") == t4

    # Search / filtering
    quantum_matches = registry.find(query="quantum")
    assert len(quantum_matches) == 1
    assert quantum_matches[0].trace_id == "t3"

    failed = registry.find(failed_only=True)
    assert len(failed) == 1
    assert failed[0].trace_id == "t2"

    dense = registry.find(strategy="dense")
    assert len(dense) == 1
    assert dense[0].trace_id == "t3"

    # Clear
    registry.clear()
    assert len(registry) == 0


# ===========================================================================
# 4. Telemetry Collector & Percentile Calculations
# ===========================================================================


def test_telemetry_collector_percentiles_and_tokens() -> None:
    telemetry = TelemetryCollector(sample_window=100)
    telemetry.reset()

    # Record 10 queries with known latencies: 10, 20, 30, ... 100 ms
    for i in range(1, 11):
        telemetry.record_query(
            latency_ms=float(i * 10),
            retrieval_ms=float(i * 2),
            llm_ms=float(i * 8),
            success=True,
            prompt_tokens=50,
            completion_tokens=20,
        )

    snap = telemetry.snapshot()
    assert snap["queries"]["total"] == 10
    assert snap["queries"]["successful"] == 10
    assert snap["queries"]["success_rate_percent"] == 100.0

    # Average RAG latency = 55.0
    assert snap["latencies_ms"]["rag"]["avg"] == 55.0
    # Percentiles: p50 should be around 55, p90 around 91
    assert 50.0 <= snap["latencies_ms"]["rag"]["p50"] <= 60.0
    assert snap["latencies_ms"]["rag"]["p90"] >= 85.0

    assert snap["tokens"]["total_tokens"] == 700
    assert snap["tokens"]["avg_tokens_per_query"] == 70.0


# ===========================================================================
# 5. Structured JSON Logging Tests
# ===========================================================================


def test_structured_json_formatter_with_trace_context() -> None:
    formatter = StructuredJsonFormatter()

    with trace_scope("logging_test") as ctx:
        logger = logging.getLogger("test_structured_logger")
        record = logger.makeRecord(
            name="test_structured_logger",
            level=logging.INFO,
            fn="test_observability.py",
            lno=100,
            msg="User prompt dispatched",
            args=(),
            exc_info=None,
            extra={"client_ip": "127.0.0.1", "custom_tag": "research_v1"},
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test_structured_logger"
        assert data["message"] == "User prompt dispatched"
        assert data["trace_id"] == ctx.trace_id
        assert data["span_id"] == ctx.span_id
        assert data["extra"]["client_ip"] == "127.0.0.1"
        assert data["extra"]["custom_tag"] == "research_v1"


def test_structured_json_formatter_with_sensitive_filter() -> None:
    formatter = StructuredJsonFormatter()
    filter_ = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test_filter",
        level=logging.WARNING,
        pathname="test.py",
        lineno=42,
        msg="Using key sk-abcdef1234567890abcdef1234567890 for provider",
        args=(),
        exc_info=None,
    )

    filter_.filter(record)
    output = formatter.format(record)
    data = json.loads(output)
    assert "[REDACTED_KEY]" in data["message"]
    assert "sk-abcdef1234567890" not in data["message"]


# ===========================================================================
# 6. System Health Aggregator Tests
# ===========================================================================


def test_system_health_aggregator_all_healthy() -> None:
    mock_retrieval = MagicMock()
    mock_retrieval.strategies.list_strategies.return_value = ["dense", "sparse"]
    mock_retrieval.storage = None
    mock_retrieval.ai_provider = None
    mock_retrieval.metrics.query_count = 5
    mock_retrieval.metrics.success_count = 5
    mock_retrieval.metrics.avg_latency_ms = 12.0

    mock_ai = MagicMock()
    mock_ai.health.return_value = HealthStatus.HEALTHY
    mock_ai.active_provider_name = "ollama"

    aggregator = SystemHealthAggregator(
        retrieval_manager=mock_retrieval,
        ai_manager=mock_ai,
    )
    report = aggregator.check_health()
    assert report.status == HealthStatus.HEALTHY
    assert "All monitored subsystems operational" in report.details
    assert "retrieval" in report.metrics["subsystems"]
    assert "ai" in report.metrics["subsystems"]


def test_system_health_aggregator_degraded_and_unhealthy() -> None:
    mock_ai = MagicMock()
    mock_ai.health.return_value = HealthStatus.UNHEALTHY
    mock_ai.active_provider_name = "offline_provider"

    aggregator = SystemHealthAggregator(ai_manager=mock_ai)
    report = aggregator.check_health()
    assert report.status == HealthStatus.UNHEALTHY
    assert len(report.errors) > 0


# ===========================================================================
# 7. Telemetry Event Subscriber Tests
# ===========================================================================


def test_telemetry_event_subscriber_with_event_bus() -> None:
    bus = EventBus()
    collector = TelemetryCollector()
    subscriber = TelemetryEventSubscriber(event_bus=bus, telemetry=collector)
    subscriber.subscribe()

    from scholaros.knowledge.rag.events import RAGCompleted, RAGFailed

    # Dispatch RAGCompleted
    bus.publish(
        RAGCompleted(
            query="test query",
            strategy="dense",
            model="llama3",
            results_count=3,
            latency_ms=42.0,
        )
    )

    snap = collector.snapshot()
    assert snap["queries"]["successful"] == 1
    assert snap["latencies_ms"]["rag"]["avg"] == 42.0

    # Dispatch RAGFailed
    bus.publish(
        RAGFailed(
            query="fail query",
            strategy="sparse",
            error="boom",
            latency_ms=10.0,
        )
    )
    snap = collector.snapshot()
    assert snap["queries"]["failed"] == 1

    subscriber.unsubscribe()


# ===========================================================================
# 8. RAG Pipeline End-to-End Observability Integration Tests
# ===========================================================================


def test_rag_pipeline_trace_capture_and_diagnostics_inspection() -> None:
    # Set up mock retrieval pipeline returning 1 chunk
    chunk = Chunk(
        document_id="doc_101",
        content="ScholarOS observability allows full trace reconstruction.",
        identifier="c_1",
    )
    result = RetrievalResult.from_chunk(chunk, score=0.98)

    mock_retrieval = MagicMock(spec=RetrievalPipeline)
    mock_retrieval.run.return_value = [result]

    mock_llm = MagicMock(spec=LLM)
    mock_llm.generate.return_value = LLMResponse(
        content="Trace reconstruction works accurately.",
        model="mock-gpt",
        prompt_tokens=45,
        completion_tokens=15,
        total_tokens=60,
    )

    pipeline = RAGPipeline(
        retrieval_pipeline=mock_retrieval,
        llm=mock_llm,
    )

    DiagnosticsRegistry.get_default().clear()

    response = pipeline.run(RAGRequest(query="How does trace reconstruction work?"))

    assert response.content == "Trace reconstruction works accurately."
    trace_id = response.metadata.get("trace_id")
    assert trace_id is not None

    # Verify trace is recorded in default registry
    trace = DiagnosticsRegistry.get_default().get(trace_id)
    assert trace is not None
    assert trace.query == "How does trace reconstruction work?"
    assert trace.model == "mock-gpt"
    assert trace.is_success is True
    assert len(trace.retrieved_chunks) == 1
    assert trace.retrieved_chunks[0].chunk_id == "c_1"
    assert trace.scores[0] == 0.98
    assert trace.prompt_tokens == 45
    assert trace.completion_tokens == 15

    # Check diagnostic markdown answers "The research answer is wrong"
    md = trace.to_markdown()
    assert f"# RAG Diagnostic Trace: `{trace_id}`" in md
    assert "mock-gpt" in md
    assert "doc_101" in md
    assert "0.9800" in md
    assert "Trace reconstruction works accurately." in md


# ===========================================================================
# 9. GUIApplication Observability Endpoints Tests
# ===========================================================================


def test_gui_application_observability_methods() -> None:
    mock_window = MagicMock()
    mock_rag = MagicMock(spec=RAGPipeline)
    mock_ai = MagicMock()
    mock_ai.health.return_value = HealthStatus.HEALTHY
    mock_ai.active_provider_name = "test-ai"

    app = GUIApplication(
        window=mock_window,
        rag_pipeline=mock_rag,
        ai_manager=mock_ai,
    )

    # Register a known trace
    test_trace = RAGTrace(trace_id="gui-trace-1", query="GUI test query")
    DiagnosticsRegistry.get_default().record(test_trace)

    # Test get_trace
    retrieved = app.get_trace("gui-trace-1")
    assert retrieved is not None
    assert retrieved.query == "GUI test query"

    # Test get_recent_traces
    recent = app.get_recent_traces(limit=5)
    assert any(t.trace_id == "gui-trace-1" for t in recent)

    # Test get_telemetry
    telem = app.get_telemetry()
    assert "queries" in telem
    assert "latencies_ms" in telem

    # Test check_system_health
    health = app.check_system_health()
    assert isinstance(health, ServiceHealth)
    assert health.status == HealthStatus.HEALTHY

    # Test set_debug_mode
    app.set_debug_mode(True)
    assert logging.getLogger("ScholarOS").level == logging.DEBUG
    app.set_debug_mode(False)
    assert logging.getLogger("ScholarOS").level == logging.INFO
