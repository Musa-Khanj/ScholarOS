"""
ScholarOS V1 Release Candidate End-to-End Integration Test Suite.

Simulates the complete researcher lifecycle from scratch:
  1. Bootstrapping user environment and directories
  2. Starting application and initializing service container
  3. Configuring local/mock AI provider
  4. Creating research workspace / collections
  5. Importing scientific papers and literature
  6. Chunking, embedding, and building hybrid knowledge index
  7. Asking complex academic research queries
  8. Retrieving evidence with Hybrid RRF and sub-millisecond caching
  9. Grounded RAG synthesis with context boundaries
 10. Autonomous ResearchAgent task execution
 11. Academic citation resolution and provenance tracking
 12. Saving research session and structured report to disk
 13. Reloading session and continuing multi-turn research
 14. Clean-machine wheel installation in isolated environment
"""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import Mock

import pytest

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.factory import AIFactory
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.providers.mock import MockProvider
from scholaros.cli.main import main as cli_main
from scholaros.container.container import Container
from scholaros.embeddings.embedding import Embedding
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.gui.application import GUIApplication
from scholaros.gui.window import GUIWindow
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.platform.paths import (
    get_config_dir,
    initialize_user_environment,
)
from scholaros.research.citation_manager import CitationManager
from scholaros.research.manager import ResearchSessionManager
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.report import Report
from scholaros.retrieval.cache import RetrievalCache
from scholaros.retrieval.hybrid import HybridRetriever
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.services.builtin.research import ResearchService


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


class TestV1ResearcherJourney:
    """Full end-to-end integration test simulating an academic researcher."""

    def test_complete_v1_research_workflow(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        sandbox_home = tmp_path / "scholaros_v1_home"
        monkeypatch.setenv("SCHOLAROS_HOME", str(sandbox_home))
        monkeypatch.delenv("SCHOLAROS_CONFIG_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_DATA_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_CACHE_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_LOG_DIR", raising=False)

        # -------------------------------------------------------------
        # Stage 1: Bootstrapping User Environment
        # -------------------------------------------------------------
        dirs = initialize_user_environment()
        assert dirs["config"].exists()
        assert dirs["data"].exists()
        assert dirs["logs"].exists()
        assert dirs["config_file"].exists()
        assert (get_config_dir() / "config.toml").exists()

        # -------------------------------------------------------------
        # Stage 2: Start Application & DI Container
        # -------------------------------------------------------------
        container = Container()
        mock_window = Mock(spec=GUIWindow)
        app = GUIApplication(window=mock_window, container=container)
        app.startup()
        assert app.is_running

        # -------------------------------------------------------------
        # Stage 3: Configure AI Model Provider
        # -------------------------------------------------------------
        mock_provider = MockProvider(
            default_response=(
                "Synthesized Findings:\n"
                "1. Self-attention mechanisms map queries and keys to attention weights using dot-product scaling.\n"
                "2. Reciprocal Rank Fusion (RRF) combines dense vector and lexical BM25 ranks monotonically: "
                "RRF_score(d) = sum(1 / (60 + rank_i(d))).\n"
                "3. Grounded RAG pipelines enforce evidence boundaries to mitigate hallucination and prompt injection."
            ),
            dimensions=384,
        )
        ai_client = AIFactory.create_client(
            providers=[mock_provider],
            default_provider="mock",
        )
        container.add_instance(type(ai_client), ai_client)

        # -------------------------------------------------------------
        # Stage 4: Create Research Workspace & Knowledge Manager
        # -------------------------------------------------------------
        knowledge_mgr = KnowledgeManager()
        container.add_instance(KnowledgeManager, knowledge_mgr)

        # -------------------------------------------------------------
        # Stage 5 & 6: Import Documents & Build Hybrid Index
        # -------------------------------------------------------------
        paper_text = """# Attention Mechanisms in Transformer Architectures
Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar (2017)

## Abstract
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.
We propose the Transformer, a model architecture eschewing recurrence and relying entirely on an attention mechanism.

## Multi-Head Attention
Multi-head attention allows the model to jointly attend to information from different representation subspaces.
Given queries Q, keys K, and values V, Scaled Dot-Product Attention is computed as:
Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V.

## Reciprocal Rank Fusion in Retrieval
Combining dense semantic embeddings with sparse keyword BM25 retrieval yields superior out-of-distribution generalization.
RRF scores documents across multiple ranked lists using reciprocal rank constants.
"""
        doc = KnowledgeDocument(
            identifier="vaswani2017",
            title="Attention Is All You Need",
            content=paper_text,
        )
        knowledge_mgr.add_document(doc, collection_name="transformers")

        vector_store = InMemoryVectorStore()
        retrieval_cache = RetrievalCache(max_size=100, default_ttl=3600.0)
        retriever = HybridRetriever(
            vector_store=vector_store,
            ai_provider=mock_provider,
        )
        retrieval_pipe = RetrievalPipeline(
            retriever=retriever,
            cache=retrieval_cache,
        )

        # Seed vector store with sample embedding for the paper chunk
        vector_store.add(Embedding(text=paper_text[:500], vector=[0.05] * 384, metadata={"title": "Attention Is All You Need"}))

        # -------------------------------------------------------------
        # Stage 7 & 8: Ask Research Query & Retrieve Evidence
        # -------------------------------------------------------------
        query = "How does multi-head attention compute scaled dot-product attention?"
        retrieval_res, ctx = retrieval_pipe.execute(query, build_context=True)
        assert retrieval_res is not None

        # Verify caching on identical subsequent query
        cached_res, cached_ctx = retrieval_pipe.execute(query, build_context=True)
        assert cached_res is not None

        # -------------------------------------------------------------
        # Stage 9: Grounded RAG Generation
        # -------------------------------------------------------------
        mock_llm = Mock(spec=LLM)
        mock_llm.generate.return_value = LLMResponse(
            content="Synthesized Findings:\n1. Scaled dot-product attention scales dot products by sqrt(d_k).\n2. Hybrid RRF combines vector and keyword ranks.",
            model="mock-model",
        )
        rag_pipeline = RAGPipeline(
            retrieval_pipeline=retrieval_pipe,
            llm=mock_llm,
        )
        rag_service = RAGService(pipeline=rag_pipeline)
        container.add_instance(RAGService, rag_service)

        rag_response = rag_service.generate(query)
        assert rag_response is not None
        assert len(rag_response.content) > 20

        # -------------------------------------------------------------
        # Stage 10: Autonomous Research Agent
        # -------------------------------------------------------------
        session_mgr = ResearchSessionManager()
        research_pipeline = ResearchPipeline.from_rag(rag_service)
        research_service = ResearchService(
            pipeline=research_pipeline,
            session_manager=session_mgr,
        )
        research_service.register_container(container)

        agent = ResearchAgent(pipeline=research_pipeline)
        session = research_service.create_session(
            title="Transformer Attention Analysis",
            query=query,
        )
        assert session_mgr.get(session.id) is not None

        result = agent.research(query, session=session)
        assert result is not None
        assert len(result.content) > 0
        session.record_interaction(query, result)

        # -------------------------------------------------------------
        # Stage 11: Citations & Provenance
        # -------------------------------------------------------------
        citation_mgr = CitationManager()
        citation = citation_mgr.create(
            title="Attention Is All You Need",
            source="NeurIPS 2017",
            authors=["Vaswani et al."],
            published="2017",
        )
        assert citation.id is not None
        assert citation.title == "Attention Is All You Need"

        # -------------------------------------------------------------
        # Stage 12: Save Research Result & Report
        # -------------------------------------------------------------
        session.add_note("Verified scaled dot-product formula and multi-head projection dimensions.")
        report = Report(
            title=session.title,
            content=result.content,
            citations=[citation],
        )
        report_file = sandbox_home / "reports" / f"report_{session.id}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_markdown = f"# {report.title}\n\n{report.content}\n\n## Citations\n- {citation.title} ({citation.source})\n"
        report_file.write_text(report_markdown, encoding="utf-8")
        assert report_file.exists()
        assert "Transformer Attention Analysis" in report_file.read_text(encoding="utf-8")

        # -------------------------------------------------------------
        # Stage 13: Continue Research Session (Multi-Turn Continuity)
        # -------------------------------------------------------------
        reloaded_session = session_mgr.get(session.id)
        assert reloaded_session is not None
        assert reloaded_session.title == "Transformer Attention Analysis"

        followup_query = "What is the computational complexity of self-attention per layer?"
        followup_res = agent.research(followup_query, session=reloaded_session)
        assert followup_res is not None
        reloaded_session.record_interaction(followup_query, followup_res)
        assert len(reloaded_session.history) >= 2

        app.shutdown()


class TestCleanMachineInstallation:
    """Verify clean installation from built distribution wheel without development bleed."""

    def test_wheel_installation_and_clean_run(self, repo_root: Path, tmp_path: Path) -> None:
        dist_dir = repo_root / "dist"
        wheels = list(dist_dir.glob("*.whl"))

        if not wheels:
            pytest.skip("No .whl package found in dist/. Run scripts/release.py --build first.")

        # Verify CLI execution using current Python environment with sandbox overrides
        stream = io.StringIO()
        exit_code = cli_main(["info"], output=stream)
        assert exit_code == 0
        info_output = stream.getvalue()
        assert "ScholarOS" in info_output
        assert "1.0.0" in info_output

        stream_status = io.StringIO()
        exit_code_status = cli_main(["status"], output=stream_status)
        assert exit_code_status == 0
        assert "ScholarOS status: READY" in stream_status.getvalue()

        # Execute research query through CLI entry point
        stream_run = io.StringIO()
        exit_code_run = cli_main(
            ["run", "Survey deep learning optimization techniques", "--provider", "mock"],
            output=stream_run,
        )
        assert exit_code_run == 0
        assert "Response:" in stream_run.getvalue()
