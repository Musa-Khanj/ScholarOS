"""
Unit tests for ScholarOS ResearchResult RAG integration (Milestone 10F).
"""

from __future__ import annotations

from scholaros.ai.response import AIResponse
from scholaros.knowledge.rag.context import RAGContext
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.research.result import ResearchResult
from scholaros.retrieval.result import RetrievalResult


class TestResearchResultRAGIntegration:
    """Test ResearchResult wrapping of both AIResponse and RAGResponse."""

    def test_legacy_ai_response_wrapping(self) -> None:
        ai_resp = AIResponse(content="Simple summary", model="legacy-model")
        result = ResearchResult(ai_resp)

        assert result.content == "Simple summary"
        assert result.model == "legacy-model"
        assert result.response is ai_resp
        assert result.is_rag is False
        assert result.sources == ()
        assert result.attributions == ()
        assert result.diagnostics == {}
        assert result.has_context is False
        assert result.latency_ms == 0.0
        assert result.results == ()
        assert result.has_content() is True
        assert result.is_empty() is False

        data = result.to_dict()
        assert data == {"content": "Simple summary", "model": "legacy-model"}

    def test_rag_response_wrapping_and_telemetry(self) -> None:
        r1 = RetrievalResult(
            content="GNN representations",
            score=0.92,
            source="paper-gnn",
            chunk_id="c1",
            document_id="d1",
        )
        ctx = RAGContext(results=[r1], query="GNN query")
        rag_resp = RAGResponse(
            content="Graph neural networks process graphs.",
            model="qwen2.5:1.5b",
            results=(r1,),
            context=ctx,
            metadata={"strategy": "semantic", "latency_ms": 42.5},
            latency_ms=42.5,
        )

        result = ResearchResult.from_rag_response(rag_resp)

        assert result.is_rag is True
        assert result.content == "Graph neural networks process graphs."
        assert result.model == "qwen2.5:1.5b"
        assert result.sources == ("paper-gnn",)
        assert len(result.attributions) == 1
        assert result.attributions[0]["source"] == "paper-gnn"
        assert result.attributions[0]["chunk_id"] == "c1"
        assert result.has_context is True
        assert result.latency_ms == 42.5
        assert len(result.results) == 1
        assert result.results[0] is r1
        assert result.diagnostics["results_count"] == 1
        assert result.diagnostics["latency_ms"] == 42.5

        data = result.to_dict()
        assert data["content"] == "Graph neural networks process graphs."
        assert data["sources"] == ["paper-gnn"]
        assert data["has_context"] is True
        assert data["latency_ms"] == 42.5
        assert len(data["attributions"]) == 1
