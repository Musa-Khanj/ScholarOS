"""Tests for Knowledge Document Ingestion Workflow, Lifecycle, and Deduplication."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.knowledge import (
    BatchIngestionResult,
    DocumentStatus,
    DuplicateDocumentError,
    DuplicatePolicy,
    KnowledgeDocument,
    KnowledgeLoader,
    KnowledgeManager,
)


class DummyEmbeddingGenerator:
    """Mock embedding generator for deterministic testing."""

    def generate(self, text: str):
        class DummyEmb:
            def __init__(self, t: str):
                self.text = t
                val = float(len(t) % 10) / 10.0
                self.vector = [val, val * 0.5, 0.1, 0.2]

        return DummyEmb(text)


@pytest.fixture
def tmp_knowledge_dir(tmp_path: Path) -> Path:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # .txt
    (docs_dir / "sample.txt").write_text("ScholarOS is an autonomous research operating system.", encoding="utf-8")
    # .md
    (docs_dir / "paper.md").write_text(
        "---\ntitle: Quantum Computing\nauthor: Scholar\n---\n# Overview\nQuantum computing leverages superposition.",
        encoding="utf-8",
    )
    # .json
    (docs_dir / "data.json").write_text(
        json.dumps({"title": "Graph Theory", "content": "Graph theory studies pairwise relations between objects."}),
        encoding="utf-8",
    )
    # .pdf (simulated)
    (docs_dir / "manual.pdf").write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Title (Deep Learning) >>\nendobj\nDeep Learning Neural Networks Manual")

    return docs_dir


class TestDocumentLifecycleAndDeduplication:
    """Tests document lifecycle status, content hashing, and duplicate policies."""

    def test_document_lifecycle_and_content_hash(self):
        doc = KnowledgeDocument(identifier="d1", title="Doc 1", content="Hello world")
        assert doc.content_hash is not None
        assert len(doc.content_hash) == 64  # SHA-256
        assert doc.status == DocumentStatus.DRAFT.value

        doc.status = DocumentStatus.PARSED
        assert doc.status == "parsed"

        doc.status = DocumentStatus.CHUNKED
        assert doc.status == "chunked"

    def test_duplicate_policy_replace(self):
        manager = KnowledgeManager()
        doc1 = KnowledgeDocument(identifier="d1", title="Original", content="First version of content")
        manager.add_document(doc1, collection_name="test_col")

        assert manager.get("test_col").get("d1").title == "Original"

        doc2 = KnowledgeDocument(identifier="d1", title="Replaced", content="Second updated version")
        res = manager.add_document(doc2, collection_name="test_col", duplicate_policy=DuplicatePolicy.REPLACE)

        assert res.title == "Replaced"
        assert manager.get("test_col").get("d1").title == "Replaced"
        assert manager.get("test_col").document_count == 1

    def test_duplicate_policy_skip(self):
        manager = KnowledgeManager()
        doc1 = KnowledgeDocument(identifier="d1", title="Original", content="Original content")
        manager.add_document(doc1, collection_name="test_col")

        doc2 = KnowledgeDocument(identifier="d1", title="Ignored", content="Should not overwrite")
        res = manager.add_document(doc2, collection_name="test_col", duplicate_policy=DuplicatePolicy.SKIP)

        assert res.title == "Original"
        assert manager.get("test_col").get("d1").title == "Original"

    def test_duplicate_policy_error(self):
        manager = KnowledgeManager()
        doc1 = KnowledgeDocument(identifier="d1", title="Original", content="Original content")
        manager.add_document(doc1, collection_name="test_col")

        doc2 = KnowledgeDocument(identifier="d1", title="Error Expected", content="Different content")
        with pytest.raises(DuplicateDocumentError):
            manager.add_document(doc2, collection_name="test_col", duplicate_policy=DuplicatePolicy.ERROR)

    def test_duplicate_detection_by_content_hash(self):
        manager = KnowledgeManager()
        doc1 = KnowledgeDocument(identifier="d1", title="Doc 1", content="Identical body content")
        manager.add_document(doc1, collection_name="test_col")

        doc2 = KnowledgeDocument(identifier="d2", title="Doc 2", content="Identical body content")
        with pytest.raises(DuplicateDocumentError):
            manager.add_document(doc2, collection_name="test_col", duplicate_policy=DuplicatePolicy.ERROR)


class TestDualIndexingAndLifecyclePurge:
    """Tests simultaneous InvertedIndex and VectorStore indexing and document updating/purging."""

    def test_add_and_purge_with_vector_store(self):
        vector_store = InMemoryVectorStore()
        generator = DummyEmbeddingGenerator()
        manager = KnowledgeManager(
            vector_store=vector_store,
            embedding_generator=generator,  # type: ignore
        )

        doc = KnowledgeDocument(identifier="doc1", title="ML", content="Machine learning models learn from data.")
        manager.add_document(doc, collection_name="ai")

        assert doc.status == DocumentStatus.INDEXED.value
        assert len(vector_store.embeddings()) > 0
        emb = vector_store.embeddings()[0]
        assert emb.metadata["document_id"] == "doc1"
        assert emb.metadata["collection"] == "ai"

        # Inverted index check
        results = manager.search("machine", collection_name="ai")
        assert len(results.results) > 0

        # Remove document: must purge from both storage, inverted index, and vector store
        manager.remove_document("doc1", collection_name="ai")
        assert len(vector_store.embeddings()) == 0
        assert manager.storage.get_document("doc1", collection_name="ai") is None

        # Re-search in inverted index
        results_after = manager.search("machine", collection_name="ai")
        assert len(results_after.results) == 0

    def test_update_document_lifecycle(self):
        vector_store = InMemoryVectorStore()
        generator = DummyEmbeddingGenerator()
        manager = KnowledgeManager(
            vector_store=vector_store,
            embedding_generator=generator,  # type: ignore
        )

        doc_v1 = KnowledgeDocument(identifier="doc_u", title="V1", content="Initial draft regarding neuroscience.")
        manager.add_document(doc_v1, collection_name="neuro")

        assert len(vector_store.embeddings()) == 1
        assert "neuroscience" in vector_store.embeddings()[0].text

        doc_v2 = KnowledgeDocument(identifier="doc_u", title="V2", content="Updated draft regarding cognitive robotics.")
        manager.update_document(doc_v2, collection_name="neuro")

        assert len(vector_store.embeddings()) == 1
        assert "cognitive robotics" in vector_store.embeddings()[0].text


class TestKnowledgeLoaderIngestionAndBatchResilience:
    """Tests file loading, format parsing, directory scanning, and batch fault tolerance."""

    def test_ingest_various_formats(self, tmp_knowledge_dir: Path):
        vector_store = InMemoryVectorStore()
        generator = DummyEmbeddingGenerator()
        manager = KnowledgeManager(vector_store=vector_store, embedding_generator=generator)  # type: ignore
        loader = KnowledgeLoader(manager=manager)

        # Ingest text file
        txt_res = loader.ingest_file(tmp_knowledge_dir / "sample.txt", collection_name="default")
        assert txt_res.is_success
        assert txt_res.chunks_count > 0
        assert txt_res.embedded is True

        # Ingest markdown file
        md_res = loader.ingest_file(tmp_knowledge_dir / "paper.md", collection_name="default")
        assert md_res.is_success
        assert md_res.document is not None
        assert md_res.document.title == "Quantum Computing"

        # Ingest json file
        json_res = loader.ingest_file(tmp_knowledge_dir / "data.json", collection_name="default")
        assert json_res.is_success
        assert json_res.document is not None
        assert json_res.document.title == "Graph Theory"

        # Ingest pdf file
        pdf_res = loader.ingest_file(tmp_knowledge_dir / "manual.pdf", collection_name="default")
        assert pdf_res.is_success
        assert pdf_res.document is not None

    def test_batch_ingestion_resilience(self, tmp_knowledge_dir: Path):
        manager = KnowledgeManager()
        loader = KnowledgeLoader(manager=manager)

        valid_file = tmp_knowledge_dir / "sample.txt"
        non_existent_file = tmp_knowledge_dir / "does_not_exist.txt"

        batch_result: BatchIngestionResult = loader.ingest_batch(
            file_paths=[valid_file, non_existent_file],
            collection_name="batch_col",
        )

        assert batch_result.total_files == 2
        assert batch_result.success_count == 1
        assert batch_result.failure_count == 1
        assert str(non_existent_file) in batch_result.failed
        assert str(non_existent_file) in batch_result.errors

    def test_directory_ingestion(self, tmp_knowledge_dir: Path):
        manager = KnowledgeManager()
        loader = KnowledgeLoader(manager=manager)

        batch_result = loader.ingest_directory(
            directory_path=tmp_knowledge_dir,
            collection_name="dir_col",
        )

        assert batch_result.total_files == 4
        assert batch_result.success_count == 4
        assert batch_result.failure_count == 0
        assert manager.contains("dir_col")
        assert manager.get("dir_col").document_count == 4
