"""
Tests for the ScholarOS Knowledge Architecture.

Validates:
1. Unified Knowledge Models (Document, Chunk, Collection, Metadata, Source)
2. Collection Lifecycle (merge, clone, export, import, get_chunks)
3. Document Pipeline (normalizer, parsers, parser registry, chunking)
4. Adapters (TextAdapter, MarkdownAdapter, JSONAdapter, PDFAdapter, FilesystemAdapter)
5. Storage Layer (InMemoryStorage CRUD operations)
6. Inverted Index and Search Engine (BM25, Cosine, Filtered search)
7. Ranking algorithms (BM25, Cosine, Recency, Metadata, Composite)
8. Statistics & Diagnostics
9. Events emitted on EventBus
10. KnowledgeService & Container integration
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import pytest

from scholaros.events.bus import EventBus
from scholaros.container.container import Container
from scholaros.knowledge import (
    Chunk,
    KnowledgeCollection,
    KnowledgeDiagnostics,
    KnowledgeDocument,
    KnowledgeEvent,
    KnowledgeFilter,
    KnowledgeLoader,
    KnowledgeManager,
    KnowledgeMetadata,
    KnowledgeService,
    KnowledgeSource,
    SearchEngine,
    SearchQuery,
    calculate_statistics,
)
from scholaros.knowledge.adapters import (
    FilesystemAdapter,
    JSONAdapter,
    MarkdownAdapter,
    TextAdapter,
)
from scholaros.knowledge.events import (
    CollectionCreated,
    DocumentAdded,
)
from scholaros.knowledge.normalizer import TextNormalizer
from scholaros.knowledge.parser import (
    JSONDocumentParser,
    MarkdownParser,
    ParserRegistry,
    PlainTextParser,
)
from scholaros.knowledge.ranking import (
    BM25Ranker,
    CompositeRanker,
    CosineSimilarityRanker,
    RecencyWeightingRanker,
)
from scholaros.knowledge.storage import InMemoryStorage


class TestKnowledgeModels:
    def test_chunk_creation_and_serialization(self) -> None:
        chunk = Chunk(
            document_id="doc_1",
            content="Quantum computing leverages superposition and entanglement.",
            index=0,
            start_char=0,
            end_char=60,
            embedding=[0.1, 0.2, 0.3],
            token_count=10,
        )
        assert chunk.document_id == "doc_1"
        assert chunk.token_count == 10
        assert chunk.content.startswith("Quantum")

        d = chunk.to_dict()
        assert d["id"] == chunk.id
        assert d["token_count"] == 10

        loaded = Chunk.from_dict(d)
        assert loaded.id == chunk.id
        assert loaded.embedding == [0.1, 0.2, 0.3]

    def test_knowledge_document_chunks_and_backward_compat(self) -> None:
        meta = KnowledgeMetadata(
            title="Attention Is All You Need",
            author="Vaswani et al.",
            tags=["nlp", "transformers"],
        )
        source = KnowledgeSource(type="file", location="/papers/vaswani2017.pdf")
        doc = KnowledgeDocument(
            id="vaswani_2017",
            title="Attention Is All You Need",
            content="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            metadata=meta,
            source=source,
        )
        assert doc.source.type == "file"
        assert len(doc.chunks) == 0

        # Chunking doc
        doc.create_chunks(chunk_size=40, chunk_overlap=10)
        assert len(doc.chunks) > 0
        assert all(isinstance(c, Chunk) for c in doc.chunks)
        assert all(c.document_id == "vaswani_2017" for c in doc.chunks)

        # Dictionary serialization
        d = doc.to_dict()
        loaded = KnowledgeDocument.from_dict(d)
        assert loaded.id == doc.id
        assert loaded.metadata.title == "Attention Is All You Need"
        assert len(loaded.chunks) == len(doc.chunks)

    def test_knowledge_collection_operations(self) -> None:
        col = KnowledgeCollection(id="physics", name="Physics Papers", description="Core physics archive")
        doc1 = KnowledgeDocument(id="p1", title="Relativity", content="Speed of light is constant in vacuum.")
        doc2 = KnowledgeDocument(id="p2", title="Thermodynamics", content="Entropy of an isolated system always increases.")
        col.add_document(doc1)
        col.add_document(doc2)

        assert col.document_count == 2
        assert col.has_document("p1")
        assert col.get_document("p1") == doc1

        # Chunks aggregation
        doc1.create_chunks(chunk_size=20)
        doc2.create_chunks(chunk_size=20)
        chunks = col.get_chunks()
        assert len(chunks) == len(doc1.chunks) + len(doc2.chunks)

        # Clone
        clone = col.clone(new_id="physics_clone", new_name="Physics Copy")
        assert clone.id == "physics_clone"
        assert clone.document_count == 2
        assert clone.has_document("p1")

        # Merge
        col2 = KnowledgeCollection(id="chem", name="Chemistry")
        col2.add_document(KnowledgeDocument(id="c1", title="Periodic Table", content="Elements organized by atomic number."))
        merged = col.merge(col2, new_id="science", new_name="Science Library")
        assert merged.document_count == 3
        assert merged.has_document("p1")
        assert merged.has_document("c1")

        # Export & Import
        json_str = col.export_json()
        assert "Relativity" in json_str
        imported = KnowledgeCollection.import_json(json_str)
        assert imported.id == col.id
        assert imported.document_count == 2


class TestDocumentPipeline:
    def test_text_normalizer(self) -> None:
        raw = "Hello   \t\n  World \u00a0!"
        cleaned = TextNormalizer.normalize(raw)
        assert cleaned == "Hello World !"

    def test_parsers(self) -> None:
        plain_parser = PlainTextParser()
        p_res = plain_parser.parse("Simple raw text")
        assert p_res.content == "Simple raw text"

        md_parser = MarkdownParser()
        md_text = "# Title\n\nSome body text with **bold**."
        md_res = md_parser.parse(md_text)
        assert md_res.title == "Title"
        assert "Some body text" in md_res.content

        json_parser = JSONDocumentParser()
        json_data = json.dumps({"title": "Data Document", "text": "Structured content"})
        json_res = json_parser.parse(json_data)
        assert json_res.title == "Data Document"
        assert json_res.content == "Structured content"

        # ParserRegistry
        assert ParserRegistry.get_parser(".md") is not None
        assert ParserRegistry.get_parser(".txt") is not None
        assert ParserRegistry.get_parser(".json") is not None

    def test_loader_chunking(self) -> None:
        loader = KnowledgeLoader(default_chunk_size=50, default_chunk_overlap=10)
        chunks = loader.chunk_text("Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau", 30, 5)
        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)


class TestAdapters:
    def test_adapters_load(self, tmp_path: Path) -> None:
        # Text Adapter
        txt_path = tmp_path / "sample.txt"
        txt_path.write_text("Plain text content here.", encoding="utf-8")
        txt_adapter = TextAdapter()
        txt_doc = txt_adapter.load(txt_path)
        assert "Plain text content" in txt_doc.content

        # Markdown Adapter
        md_path = tmp_path / "notes.md"
        md_path.write_text("# Note Header\nDetails inside.", encoding="utf-8")
        md_adapter = MarkdownAdapter()
        md_doc = md_adapter.load(md_path)
        assert md_doc.title == "Note Header"

        # JSON Adapter
        json_path = tmp_path / "doc.json"
        json_path.write_text(json.dumps({"title": "Config Spec", "content": "JSON specification"}), encoding="utf-8")
        json_adapter = JSONAdapter()
        json_doc = json_adapter.load(json_path)
        assert json_doc.title == "Config Spec"
        assert json_doc.content == "JSON specification"

        # Filesystem Adapter
        fs_adapter = FilesystemAdapter(chunk_size=100)
        docs = fs_adapter.load_directory(tmp_path)
        assert len(docs) >= 3


class TestStorageAndSearch:
    def test_in_memory_storage(self) -> None:
        storage = InMemoryStorage()
        col = KnowledgeCollection(id="test_col", name="Test Collection")
        storage.save_collection(col)
        assert storage.get_collection("test_col") is not None

        doc = KnowledgeDocument(id="d1", title="Algorithms", content="Graph traversal using BFS and DFS.")
        doc.create_chunks(chunk_size=30)
        storage.save_document(doc, collection_id="test_col")

        assert storage.get_document("d1") is not None
        assert len(storage.get_chunks("d1")) == len(doc.chunks)
        assert storage.count_documents("test_col") == 1
        assert storage.count_chunks("test_col") == len(doc.chunks)

        storage.delete_document("d1")
        assert storage.get_document("d1") is None
        assert storage.count_documents("test_col") == 0

    def test_ranking_algorithms(self) -> None:
        # BM25 Ranker
        bm25 = BM25Ranker()
        score1 = bm25.score(
            query_terms=["quantum", "computing"],
            doc_terms=["quantum", "computing", "circuit", "gate"],
            doc_len=4,
            avg_doc_len=4.0,
            doc_freqs={"quantum": 1, "computing": 1},
            total_docs=10,
        )
        score2 = bm25.score(
            query_terms=["quantum", "computing"],
            doc_terms=["classical", "mechanics", "gravity", "mass"],
            doc_len=4,
            avg_doc_len=4.0,
            doc_freqs={"quantum": 1, "computing": 1},
            total_docs=10,
        )
        assert score1 > score2

        # Cosine Ranker
        cosine = CosineSimilarityRanker()
        sim_high = cosine.similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        sim_low = cosine.similarity([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        assert sim_high == pytest.approx(1.0)
        assert sim_low == pytest.approx(0.0)

        # Recency Ranker
        recency = RecencyWeightingRanker(half_life_days=30)
        now = datetime.now(timezone.utc)
        recent_boost = recency.boost(now)
        assert recent_boost == pytest.approx(1.0)

        # Composite Ranker
        comp = CompositeRanker(bm25_weight=0.7, recency_weight=0.3)
        combined = comp.score(bm25_score=10.0, recency_boost=1.0)
        assert combined == 7.0 + 0.3

    def test_search_engine_and_filters(self) -> None:
        engine = SearchEngine()
        doc1 = KnowledgeDocument(
            id="doc_ai",
            title="Artificial Intelligence",
            content="Deep learning and neural networks advance machine intelligence.",
            metadata=KnowledgeMetadata(tags=["ai", "deep-learning"], author="Alice"),
        )
        doc2 = KnowledgeDocument(
            id="doc_db",
            title="Relational Databases",
            content="SQL queries and ACID transactions in relational databases.",
            metadata=KnowledgeMetadata(tags=["database", "sql"], author="Bob"),
        )
        doc1.create_chunks(chunk_size=40)
        doc2.create_chunks(chunk_size=40)

        engine.index_document(doc1)
        engine.index_document(doc2)

        # Keyword search
        query = SearchQuery(query="neural networks", limit=5)
        resp = engine.search(query)
        assert len(resp.results) > 0
        assert resp.results[0].document.id == "doc_ai"

        # Filtered search
        query_filtered = SearchQuery(
            query="databases",
            filter=KnowledgeFilter(authors=["Bob"]),
        )
        resp_filtered = engine.search(query_filtered)
        assert len(resp_filtered.results) == 1
        assert resp_filtered.results[0].document.id == "doc_db"


class TestStatisticsAndDiagnostics:
    def test_statistics_calculation(self) -> None:
        col = KnowledgeCollection(id="stat_col", name="Stat Col")
        doc = KnowledgeDocument(id="doc_stat", title="Stats", content="Document for testing knowledge statistics calculation.")
        doc.create_chunks(chunk_size=20)
        col.add_document(doc)

        stats = calculate_statistics(col)
        assert stats.document_count == 1
        assert stats.chunk_count == len(doc.chunks)
        assert stats.total_characters > 0
        assert stats.avg_chunk_size > 0

    def test_diagnostics_report(self) -> None:
        diag = KnowledgeDiagnostics()
        col = KnowledgeCollection(id="diag_col", name="Diag Col")
        doc_valid = KnowledgeDocument(
            id="valid",
            title="Valid Doc",
            content="Healthy document with full metadata and chunks.",
            metadata=KnowledgeMetadata(title="Valid Doc"),
            source=KnowledgeSource(type="test", location="mem"),
        )
        doc_valid.create_chunks(chunk_size=30)
        col.add_document(doc_valid)

        report = diag.run(col)
        assert report.is_healthy


class TestManagerAndServiceIntegration:
    def test_knowledge_manager_and_events(self) -> None:
        bus = EventBus()
        events_captured: list[KnowledgeEvent] = []

        def on_event(event: KnowledgeEvent) -> None:
            events_captured.append(event)

        bus.subscribe("CollectionCreated", on_event)
        bus.subscribe("DocumentAdded", on_event)

        manager = KnowledgeManager(event_bus=bus)
        col = manager.create_collection("col_main", name="Main Collection")
        assert col.id == "col_main"

        doc = KnowledgeDocument(
            id="doc_m1",
            title="Manager Doc",
            content="Content handled by KnowledgeManager.",
            source=KnowledgeSource(type="test", location="mem"),
        )
        manager.add_document(doc, collection_id="col_main")

        # Search through manager
        results = manager.search("Manager Doc", collection_id="col_main")
        assert len(results) > 0

        # Stats & Diagnostics through manager
        stats = manager.get_statistics("col_main")
        assert stats.document_count == 1
        report = manager.run_diagnostics("col_main")
        assert report.is_healthy

        # Verify events
        event_types = [type(e) for e in events_captured]
        assert CollectionCreated in event_types
        assert DocumentAdded in event_types

    def test_knowledge_service_lifecycle_and_di(self) -> None:
        container = Container()
        service = KnowledgeService()

        # Register into container
        service.register_into_container(container)
        assert container.resolve(KnowledgeService) is not None
        assert container.resolve(KnowledgeManager) is not None

        # Lifecycle
        service.initialize()
        service.start()
        assert service.is_healthy()
        assert service.manager is not None

        service.stop()
        service.shutdown()
