from unittest.mock import Mock

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import MessageRole
from scholaros.ai.llm.response import LLMResponse
from scholaros.knowledge.rag.context import RAGContext
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.retrieval.collection import RetrievalCollection
from scholaros.retrieval.context import RetrievalContext
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult


def make_llm(content: str = "ScholarOS answers the question.") -> Mock:
    llm = Mock(spec=LLM)
    llm.generate.return_value = LLMResponse(
        content=content,
        model="gpt-4o-mini",
        prompt_tokens=30,
        completion_tokens=20,
        total_tokens=50,
    )
    return llm


def make_result(
    source: str = "doc-alpha",
    content: str = "A detailed paragraph on neural networks.",
    score: float = 0.95,
) -> RetrievalResult:
    return RetrievalResult(
        source=source,
        content=content,
        score=score,
    )


# ---------------------------------------------------------------------------
# 1. RAGRequest max_tokens & system_prompt
# ---------------------------------------------------------------------------


def test_rag_request_max_tokens_and_system_prompt():
    req = RAGRequest(
        query="What is reinforcement learning?",
        max_tokens=256,
        system_prompt="You are a specialist in robotics and control theory.",
    )
    assert req.max_tokens == 256
    assert req.system_prompt == "You are a specialist in robotics and control theory."
    assert "max_tokens=256" in repr(req)
    assert "system_prompt=" in repr(req)

    q = req.to_retrieval_query()
    assert q.options.get("max_tokens") == 256


def test_rag_request_validation_for_execution_fields():
    with pytest.raises(TypeError, match="RAG max_tokens must be an integer"):
        RAGRequest(query="valid", max_tokens="256")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="RAG max_tokens must be greater than zero"):
        RAGRequest(query="valid", max_tokens=0)

    with pytest.raises(TypeError, match="RAG system_prompt must be a string"):
        RAGRequest(query="valid", system_prompt=123)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="RAG system_prompt must not be blank"):
        RAGRequest(query="valid", system_prompt="   ")


# ---------------------------------------------------------------------------
# 2. RAGContext Token Budgeting & from_retrieval_context Bridge
# ---------------------------------------------------------------------------


def test_rag_context_token_budget_truncation():
    # Long contents that each take ~25 tokens (100 characters)
    r1 = make_result("doc-1", "A" * 100, 0.9)
    r2 = make_result("doc-2", "B" * 100, 0.8)
    r3 = make_result("doc-3", "C" * 100, 0.7)

    # Context with small token budget: fits only 1 result
    ctx = RAGContext(
        [r1, r2, r3],
        query="Test query",
        max_tokens=35,
    )

    assert ctx.query == "Test query"
    assert ctx.max_tokens == 35
    assert ctx.is_truncated is True
    assert len(ctx.results) == 1
    assert ctx.results[0] is r1
    assert ctx.token_count > 0


def test_rag_context_without_truncation():
    r1 = make_result("doc-1", "Short text.", 0.9)
    ctx = RAGContext([r1], max_tokens=500)
    assert ctx.is_truncated is False
    assert len(ctx.results) == 1


def test_rag_context_from_retrieval_context_bridge():
    r1 = make_result("paper-01", "Transformer attention mechanisms.", 0.98)
    retrieval_ctx = RetrievalContext(
        query="Attention",
        results=[r1],
        total_tokens=20,
        metadata={"max_tokens": 128},
    )

    rag_ctx = RAGContext.from_retrieval_context(retrieval_ctx)
    assert rag_ctx.query == "Attention"
    assert rag_ctx.max_tokens == 128
    assert len(rag_ctx.results) == 1
    assert rag_ctx.results[0].source == "paper-01"


def test_rag_context_iteration_and_contains():
    r1 = make_result("doc-1", "Content 1", 0.9)
    r2 = make_result("doc-2", "Content 2", 0.8)
    ctx = RAGContext([r1, r2])

    assert list(ctx) == [r1, r2]
    assert r1 in ctx
    assert make_result("doc-unknown") not in ctx


# ---------------------------------------------------------------------------
# 3. RAGResponse Execution Properties
# ---------------------------------------------------------------------------


def test_rag_response_execution_properties():
    r1 = make_result("doc-1", "Content", 0.9)
    ctx = RAGContext([r1], query="Original Query")
    resp = RAGResponse(
        content="Response text",
        model="gpt-4o",
        results=[r1],
        context=ctx,
        latency_ms=45.2,
    )

    assert resp.has_context is True
    assert resp.latency_ms == 45.2
    assert resp.query == "Original Query"
    assert resp.metadata["latency_ms"] == 45.2


def test_rag_response_without_context():
    resp = RAGResponse(
        content="No context available",
        model="gpt-4o",
        results=[],
    )
    assert resp.has_context is False
    assert resp.latency_ms == 0.0
    assert resp.query == ""


# ---------------------------------------------------------------------------
# 4. RAGPipeline Prompt Construction & System Prompt Hierarchy
# ---------------------------------------------------------------------------


def test_pipeline_system_prompt_hierarchy():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.run.return_value = [make_result()]
    llm = make_llm()

    # 1. Default system prompt
    pipe_default = RAGPipeline(retrieval_pipeline, llm)
    pipe_default.run(RAGRequest(query="Query 1"))
    msgs1 = llm.generate.call_args[0][0]
    assert "You are a research assistant for ScholarOS" in msgs1[0].content

    # 2. Pipeline-level system prompt
    pipe_custom = RAGPipeline(
        retrieval_pipeline,
        llm,
        system_prompt="Pipeline-level custom prompt.",
    )
    pipe_custom.run(RAGRequest(query="Query 2"))
    msgs2 = llm.generate.call_args[0][0]
    assert msgs2[0].content == "Pipeline-level custom prompt."

    # 3. Request-level system prompt overrides pipeline-level
    pipe_custom.run(
        RAGRequest(
            query="Query 3",
            system_prompt="Request-level override prompt.",
        )
    )
    msgs3 = llm.generate.call_args[0][0]
    assert msgs3[0].content == "Request-level override prompt."


def test_pipeline_execute_with_retrieval_context():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    res = make_result("doc-rc", "Retrieval context text")
    retrieval_ctx = RetrievalContext(
        query="Built context query",
        results=[res],
        total_tokens=15,
        metadata={"max_tokens": 64},
    )
    retrieval_pipeline.execute.return_value = ([res], retrieval_ctx)

    llm = make_llm()
    pipeline = RAGPipeline(retrieval_pipeline, llm)

    response = pipeline.execute("Built context query")

    assert isinstance(response, RAGResponse)
    assert response.has_context is True
    assert response.latency_ms >= 0.0
    assert response.context.query == "Built context query"
    assert response.context.max_tokens == 64
    assert response.sources == ("doc-rc",)


# ---------------------------------------------------------------------------
# 5. End-to-End Pipeline Execution with RetrievalManager
# ---------------------------------------------------------------------------


def test_end_to_end_pipeline_execution_flow():
    manager = RetrievalManager()
    col = RetrievalCollection()
    col.add(
        make_result(
            source="paper-quantum",
            content="Quantum supremacy demonstration using superconducting qubits.",
            score=0.96,
        )
    )
    manager.registry.add("physics", col)

    llm = make_llm("Quantum supremacy is achieved through error-mitigated circuits.")
    pipeline = RAGPipeline.from_manager(
        manager=manager,
        llm=llm,
        strategy="collection",
        system_prompt="Physics Specialist Agent",
    )

    request = RAGRequest(
        query="superconducting",
        strategy="collection",
        limit=3,
        max_tokens=500,
    )

    response = pipeline.execute(request)

    assert isinstance(response, RAGResponse)
    assert response.has_context is True
    assert "paper-quantum" in response.sources
    assert response.latency_ms >= 0.0
    assert response.metadata["strategy"] == "collection"

    # Verify messages passed to LLM
    call_messages = llm.generate.call_args[0][0]
    assert len(call_messages) == 2
    assert call_messages[0].role == MessageRole.SYSTEM
    assert call_messages[0].content == "Physics Specialist Agent"
    assert call_messages[1].role == MessageRole.USER
    assert "paper-quantum" in call_messages[1].content
    assert "superconducting" in call_messages[1].content
