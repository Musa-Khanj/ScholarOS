from unittest.mock import Mock

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.knowledge.rag.context import RAGContext
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult


def make_llm(content: str = "ScholarOS is a research assistant.") -> Mock:
    llm = Mock(spec=LLM)
    llm.generate.return_value = LLMResponse(
        content=content,
        model="test-rag-model",
        prompt_tokens=25,
        completion_tokens=15,
        total_tokens=40,
    )
    return llm


def make_result(
    source: str = "paper-01",
    content: str = "Quantum computing research notes.",
    score: float = 0.92,
    provenance: dict | None = None,
    collection: str = "papers",
) -> RetrievalResult:
    metadata = {}
    if provenance:
        metadata["provenance"] = provenance
    return RetrievalResult(
        source=source,
        content=content,
        score=score,
        metadata=metadata,
        collection=collection,
    )


# ---------------------------------------------------------------------------
# RAGRequest Enhancements & Validation
# ---------------------------------------------------------------------------


def test_rag_request_defaults():
    req = RAGRequest(query="What is quantum entanglement?")
    assert req.query == "What is quantum entanglement?"
    assert req.minimum_score == 0.0
    assert req.strategy == "default"
    assert req.limit == 10
    assert req.collections is None
    assert req.filters is None
    assert req.options == {}
    assert repr(req) == "RAGRequest(query='What is quantum entanglement?', minimum_score=0.0)"


def test_rag_request_custom_attributes():
    req = RAGRequest(
        query="Graph Neural Networks",
        minimum_score=0.7,
        strategy="hybrid",
        limit=5,
        collections=["ai_papers", "cs_theses"],
        filters={"year": 2025},
        options={"temperature": 0.2},
    )
    assert req.strategy == "hybrid"
    assert req.limit == 5
    assert req.collections == ("ai_papers", "cs_theses")
    assert req.filters == {"year": 2025}
    assert req.options == {"temperature": 0.2}
    assert "strategy='hybrid'" in repr(req)
    assert "limit=5" in repr(req)


def test_rag_request_to_retrieval_query():
    req = RAGRequest(
        query="Generative AI",
        minimum_score=0.8,
        strategy="semantic",
        limit=7,
        collections=["articles"],
        filters={"category": "ai"},
    )
    q = req.to_retrieval_query()
    assert isinstance(q, RetrievalQuery)
    assert q.text == "Generative AI"
    assert q.min_score == 0.8
    assert q.strategy == "semantic"
    assert q.limit == 7
    assert q.collections == ["articles"]
    assert q.filters == {"category": "ai"}


def test_rag_request_validation():
    with pytest.raises(TypeError, match="RAG strategy must be a string"):
        RAGRequest(query="test", strategy=123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RAG limit must be an integer"):
        RAGRequest(query="test", limit="10")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="RAG limit must be greater than zero"):
        RAGRequest(query="test", limit=0)

    with pytest.raises(TypeError, match="RAG collections must be a list or tuple"):
        RAGRequest(query="test", collections="single-string")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RAG filters must be a dictionary"):
        RAGRequest(query="test", filters=["not", "a", "dict"])  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RAG options must be a dictionary"):
        RAGRequest(query="test", options="invalid")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# RAGContext Metadata & Provenance Preservation
# ---------------------------------------------------------------------------


def test_rag_context_provenance_and_sources():
    r1 = make_result(
        source="paper-01",
        provenance={"streams": ["keyword", "semantic"], "fusion_mode": "rrf"},
    )
    r2 = make_result(
        source="paper-02",
        provenance={"streams": ["semantic"], "distance": 0.15},
    )
    r3 = make_result(source="paper-01")  # duplicate source

    ctx = RAGContext([r1, r2, r3])

    assert ctx.sources == ("paper-01", "paper-02")
    assert len(ctx.provenance) == 2
    assert ctx.provenance[0]["streams"] == ["keyword", "semantic"]
    assert ctx.provenance[1]["distance"] == 0.15
    assert len(ctx.metadata) == 3


def test_rag_context_format_with_metadata():
    r1 = make_result(
        source="doc-A",
        content="First paragraph.",
        score=0.95,
        provenance={"keyword_rank": 1},
    )
    ctx = RAGContext([r1])

    formatted = ctx.format_with_metadata(
        include_sources=True,
        include_scores=True,
        include_provenance=True,
    )
    assert "[Source 1: doc-A | Score: 0.950 | Provenance: {'keyword_rank': 1}]" in formatted
    assert "First paragraph." in formatted


def test_rag_context_empty_format():
    ctx = RAGContext([])
    assert ctx.format_with_metadata() == ""
    assert ctx.sources == ()
    assert ctx.provenance == ()
    assert ctx.metadata == ()


# ---------------------------------------------------------------------------
# RAGResponse Metadata & Provenance Properties
# ---------------------------------------------------------------------------


def test_rag_response_provenance_delegation():
    r1 = make_result(
        source="doc-01",
        provenance={"streams": ["hybrid"], "score": 0.88},
    )
    res = RAGResponse(
        content="Answer generated.",
        model="gpt-4o",
        results=[r1],
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        metadata={"latency_ms": 120},
    )

    assert res.sources == ("doc-01",)
    assert len(res.provenance) == 1
    assert res.provenance[0]["streams"] == ["hybrid"]
    assert res.metadata == {"latency_ms": 120}
    assert isinstance(res.context, RAGContext)
    assert res.total_tokens == 15


# ---------------------------------------------------------------------------
# RAGPipeline Strategy Routing & Manager Factory
# ---------------------------------------------------------------------------


def test_pipeline_routes_custom_strategy_to_execute():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.execute.return_value = (
        [make_result(source="hybrid-doc")],
        None,
    )
    llm = make_llm()
    pipeline = RAGPipeline(retrieval_pipeline, llm)

    request = RAGRequest(
        query="What is transformer architecture?",
        strategy="hybrid",
        limit=5,
    )

    response = pipeline.run(request)

    retrieval_pipeline.execute.assert_called_once()
    called_query = retrieval_pipeline.execute.call_args.args[0]
    assert isinstance(called_query, RetrievalQuery)
    assert called_query.text == "What is transformer architecture?"
    assert called_query.strategy == "hybrid"
    assert called_query.limit == 5

    assert len(response.results) == 1
    assert response.sources == ("hybrid-doc",)


def test_pipeline_explicit_execute_method():
    retrieval_pipeline = Mock(spec=RetrievalPipeline)
    retrieval_pipeline.execute.return_value = (
        [make_result(source="exec-doc")],
        None,
    )
    llm = make_llm()
    pipeline = RAGPipeline(retrieval_pipeline, llm)

    response = pipeline.execute("Direct query string")
    assert response.sources == ("exec-doc",)
    retrieval_pipeline.execute.assert_called_once()


def test_pipeline_from_manager_factory():
    manager = RetrievalManager()
    llm = make_llm()

    rag = RAGPipeline.from_manager(manager, llm, strategy="keyword")
    assert isinstance(rag, RAGPipeline)
    assert rag.llm is llm
    assert isinstance(rag.retrieval_pipeline, RetrievalPipeline)


# ---------------------------------------------------------------------------
# End-to-End Integration: Hybrid Retriever -> Pipeline -> Context -> LLM
# ---------------------------------------------------------------------------


def test_end_to_end_hybrid_rag_flow():
    from scholaros.retrieval.collection import RetrievalCollection

    col = RetrievalCollection()
    col.add(
        make_result(
            source="paper-alpha",
            content="Deep learning optimization with adaptive learning rates.",
            score=0.95,
            collection="papers",
        )
    )
    col.add(
        make_result(
            source="paper-beta",
            content="Quantum computing algorithms for molecular simulation.",
            score=0.88,
            collection="papers",
        )
    )

    manager = RetrievalManager()
    manager.registry.add("papers", col)

    llm = make_llm()
    pipeline = RAGPipeline.from_manager(manager, llm, strategy="collection")

    request = RAGRequest(
        query="learning",
        strategy="collection",
        limit=5,
    )

    response = pipeline.execute(request)

    assert isinstance(response, RAGResponse)
    assert len(response.results) >= 1
    assert "paper-alpha" in response.sources

    # Check that LLM received formatted context containing the retrieved source
    call_args = llm.generate.call_args[0][0]
    user_message = [msg for msg in call_args if msg.role.value == "user"][0]
    assert "paper-alpha" in user_message.content
    assert "Deep learning optimization" in user_message.content
