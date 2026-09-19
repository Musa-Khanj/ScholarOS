from unittest.mock import Mock

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.knowledge.rag.context import RAGContext
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.retrieval.collection import RetrievalCollection
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult


def make_llm(content: str = "ScholarOS verified response.") -> Mock:
    llm = Mock(spec=LLM)
    llm.generate.return_value = LLMResponse(
        content=content,
        model="claude-3-5-sonnet",
        prompt_tokens=40,
        completion_tokens=25,
        total_tokens=65,
    )
    return llm


def make_result(
    source: str = "paper-01",
    content: str = "Deep learning architecture details.",
    score: float = 0.94,
    collection: str = "research_papers",
    chunk_id: str | None = "chunk-101",
    document_id: str | None = "doc-501",
    provenance: dict | None = None,
) -> RetrievalResult:
    meta = {}
    if provenance:
        meta["provenance"] = provenance
    return RetrievalResult(
        source=source,
        content=content,
        score=score,
        collection=collection,
        chunk_id=chunk_id,
        document_id=document_id,
        metadata=meta,
    )


# ---------------------------------------------------------------------------
# 1. Source Attribution & Citation Helpers
# ---------------------------------------------------------------------------


def test_context_and_response_attributions():
    r1 = make_result(
        source="arxiv-2401.001",
        content="First paragraph on sparse autoencoders.",
        score=0.96,
        collection="ai_safety",
        chunk_id="chk-01",
        document_id="doc-01",
        provenance={"streams": ["keyword", "semantic"], "fusion_mode": "rrf"},
    )
    r2 = make_result(
        source="arxiv-2401.002",
        content="Second paragraph on mechanistic interpretability.",
        score=0.88,
        collection="ai_safety",
        chunk_id="chk-02",
        document_id="doc-02",
        provenance={"streams": ["semantic"], "distance": 0.12},
    )

    ctx = RAGContext([r1, r2], query="interpretability")
    assert len(ctx.attributions) == 2

    attr1 = ctx.attributions[0]
    assert attr1["index"] == 1
    assert attr1["source"] == "arxiv-2401.001"
    assert attr1["score"] == 0.96
    assert attr1["collection"] == "ai_safety"
    assert attr1["chunk_id"] == "chk-01"
    assert attr1["document_id"] == "doc-01"
    assert attr1["provenance"]["streams"] == ["keyword", "semantic"]

    # Test source membership helpers
    assert ctx.has_source("arxiv-2401.001") is True
    assert ctx.has_source("unknown-source") is False
    assert len(ctx.get_by_source("arxiv-2401.001")) == 1

    # Test delegation on RAGResponse
    resp = RAGResponse(
        content="Analysis complete.",
        model="test-model",
        results=[r1, r2],
        context=ctx,
    )
    assert resp.attributions == ctx.attributions
    assert resp.has_source("arxiv-2401.001") is True
    assert resp.has_source("nonexistent") is False


# ---------------------------------------------------------------------------
# 2. Response Diagnostics Telemetry
# ---------------------------------------------------------------------------


def test_response_diagnostics_completeness():
    r1 = make_result("doc-diag", "Diagnostic content", 0.91)
    ctx = RAGContext([r1], query="Diagnostic test query")

    resp = RAGResponse(
        content="Generated answer",
        model="gpt-4o",
        results=[r1],
        prompt_tokens=50,
        completion_tokens=30,
        total_tokens=80,
        context=ctx,
        metadata={"strategy": "hybrid", "query": "Diagnostic test query"},
        latency_ms=125.5,
    )

    diag = resp.diagnostics
    assert isinstance(diag, dict)
    assert diag["query"] == "Diagnostic test query"
    assert diag["strategy"] == "hybrid"
    assert diag["model"] == "gpt-4o"
    assert diag["latency_ms"] == 125.5
    assert diag["has_context"] is True
    assert diag["results_count"] == 1
    assert diag["sources"] == ["doc-diag"]
    assert diag["is_truncated"] is False
    assert diag["context_tokens"] > 0
    assert diag["prompt_tokens"] == 50
    assert diag["completion_tokens"] == 30
    assert diag["total_tokens"] == 80


# ---------------------------------------------------------------------------
# 3. RAGRequest Fallback Fields & Validation
# ---------------------------------------------------------------------------


def test_rag_request_fallback_fields_and_validation():
    req = RAGRequest(
        query="Explain quantum gravity",
        fallback_on_empty=True,
        empty_fallback_message="No physics papers found.",
    )
    assert req.fallback_on_empty is True
    assert req.empty_fallback_message == "No physics papers found."
    assert "fallback_on_empty=True" in repr(req)
    assert "empty_fallback_message=" in repr(req)

    with pytest.raises(TypeError, match="fallback_on_empty must be a boolean"):
        RAGRequest(query="valid", fallback_on_empty="yes")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="empty_fallback_message must be a string"):
        RAGRequest(query="valid", empty_fallback_message=123)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="empty_fallback_message must not be blank"):
        RAGRequest(query="valid", empty_fallback_message="   ")


# ---------------------------------------------------------------------------
# 4. Empty-Context Behavior & Fact Invention Prevention
# ---------------------------------------------------------------------------


def test_empty_context_default_behavior_preserves_do_not_invent_facts():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.run.return_value = []
    llm = make_llm()

    pipeline = RAGPipeline(retrieval_pipeline, llm)
    req = RAGRequest(query="What is the secret formula for unobtainium?")

    resp = pipeline.run(req)

    # LLM must be called with instruction NOT to invent facts
    llm.generate.assert_called_once()
    system_msg = llm.generate.call_args[0][0][0]
    assert "If the context does not contain sufficient information" in system_msg.content
    assert "say so instead of inventing facts" in system_msg.content

    assert resp.has_context is False
    assert len(resp.results) == 0
    assert resp.diagnostics["has_context"] is False
    assert resp.diagnostics["results_count"] == 0


def test_empty_context_with_request_fallback_bypasses_llm():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.run.return_value = []
    llm = make_llm()

    pipeline = RAGPipeline(retrieval_pipeline, llm)
    req = RAGRequest(
        query="Nonexistent topic",
        fallback_on_empty=True,
        empty_fallback_message="Custom: No knowledge matches your request.",
    )

    resp = pipeline.run(req)

    # LLM must NOT be called
    llm.generate.assert_not_called()

    assert resp.content == "Custom: No knowledge matches your request."
    assert resp.model == "fallback"
    assert resp.has_context is False
    assert resp.total_tokens == 0
    assert resp.metadata["empty_fallback"] is True
    assert resp.diagnostics["has_context"] is False


def test_empty_context_with_pipeline_fallback():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.run.return_value = []
    llm = make_llm()

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
        fallback_on_empty=True,
        empty_fallback_message="Pipeline fallback: context missing.",
    )
    req = RAGRequest(query="Topic with no results")

    resp = pipeline.run(req)
    llm.generate.assert_not_called()
    assert resp.content == "Pipeline fallback: context missing."
    assert resp.has_context is False


# ---------------------------------------------------------------------------
# 5. End-to-End Quality & Retrieval Traceability Flow
# ---------------------------------------------------------------------------


def test_end_to_end_traceability_flow():
    manager = RetrievalManager()
    collection = RetrievalCollection()
    collection.add(
        make_result(
            source="paper-alpha",
            content="Alpha findings on neuromorphic compute.",
            score=0.97,
            collection="hardware",
            chunk_id="c-001",
            document_id="d-001",
            provenance={"keyword_score": 0.95, "semantic_score": 0.98},
        )
    )
    manager.registry.add("hardware", collection)

    llm = make_llm("Neuromorphic architectures emulate neural structures.")
    pipeline = RAGPipeline.from_manager(manager, llm, strategy="collection")

    request = RAGRequest(
        query="neuromorphic",
        strategy="collection",
        limit=5,
    )

    response = pipeline.execute(request)

    # Validate output quality and traceability
    assert response.has_context is True
    assert response.has_source("paper-alpha") is True
    assert len(response.attributions) == 1
    assert response.attributions[0]["chunk_id"] == "c-001"
    assert response.attributions[0]["document_id"] == "d-001"
    assert response.attributions[0]["provenance"]["keyword_score"] == 0.95

    # Validate diagnostics
    diag = response.diagnostics
    assert diag["strategy"] == "collection"
    assert diag["has_context"] is True
    assert diag["results_count"] == 1
    assert diag["sources"] == ["paper-alpha"]
    assert diag["latency_ms"] >= 0.0
