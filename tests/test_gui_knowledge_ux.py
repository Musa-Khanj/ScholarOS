"""
Tests for Part 7 — Knowledge Library UX.

Verifies end-to-end Knowledge Library UX requirements:
- Knowledge search: LibraryView -> GUIApplication.search_knowledge() -> RAG / Retrieval subsystem
- Document import / ingestion: connect UI to KnowledgeLoader / KnowledgeManager
- Document tree / list: display indexed documents, status, chunk counts
- Document preview: inspect document metadata, content chunks, content hash
- Reindex / remove lifecycle operations
- Non-blocking async operations for search, import, remove, and reindex
- Result and chunk presentation with relevance scores, source provenance, and metadata
- Error handling without silent mock fallbacks
- Full end-to-end integration with bootstrap_runtime()
"""

from __future__ import annotations

import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import Mock

import pytest

from scholaros.bootstrap.runtime import bootstrap_runtime
from scholaros.gui.application import GUIApplication
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.views.workspace_views import LibraryView
from scholaros.gui.window import GUIWindow
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.manager import KnowledgeManager


# ---------------------------------------------------------------------------
# Headless Tk Fixtures
# ---------------------------------------------------------------------------

_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    global _root
    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            _root = tk.Tk()
            _root.withdraw()
    return _root


@pytest.fixture
def test_root():
    return get_test_root()


@pytest.fixture
def runtime_services():
    """Create a clean production runtime services bundle."""
    return bootstrap_runtime(use_mock_ai=True)


# ---------------------------------------------------------------------------
# 1. UI Initialization & Component Layout
# ---------------------------------------------------------------------------


def test_library_view_initialization(test_root):
    """Verify LibraryView initializes with all required production controls and panes."""
    view = LibraryView(parent=test_root)

    # Search controls
    assert view.search_entry is not None
    assert view.search_button is not None
    assert view._search_entry is view.search_entry
    assert view._search_btn is view.search_button

    # Management controls
    assert view.import_button is not None
    assert view.remove_button is not None
    assert view.reindex_button is not None
    assert view.refresh_button is not None
    assert view.status_label is not None

    # Dual-pane components
    assert view.doc_tree is not None
    assert view.preview_text is not None
    assert view.display is not None
    assert view._display is view.display

    # Initial state
    assert "Ready" in view.status_label.cget("text")
    assert "Knowledge documents and RAG search results" in view.display.get("1.0", "end")


# ---------------------------------------------------------------------------
# 2. Knowledge Search: Sync Delegation & Presentation
# ---------------------------------------------------------------------------


def test_library_view_sync_search_delegation(test_root):
    """Verify LibraryView synchronously queries application.search_knowledge() and renders results."""
    mock_app = Mock(spec=GUIApplication)
    mock_app.search_knowledge.return_value = [
        {
            "content": "Attention mechanisms dynamically weight input features.",
            "score": 0.94,
            "source": "attention_paper.pdf",
            "metadata": {"section": "Abstract", "year": "2017"},
        },
        {
            "content": "Feedforward neural networks process information unidirectionally.",
            "score": 0.81,
            "source": "intro_deep_learning.md",
            "metadata": {"author": "Goodfellow"},
        },
    ]

    view = LibraryView(parent=test_root, application=mock_app)
    results = view.search("attention mechanism")

    mock_app.search_knowledge.assert_called_once_with("attention mechanism")
    assert len(results) == 2

    viewer_text = view.display.get("1.0", "end")
    assert "Searching for: attention mechanism" in viewer_text
    assert "Score: 0.94" in viewer_text
    assert "Source: attention_paper.pdf" in viewer_text
    assert "Attention mechanisms dynamically weight input features." in viewer_text
    assert "Score: 0.81" in viewer_text
    assert "Source: intro_deep_learning.md" in viewer_text
    assert "2 matches found" in view.status_label.cget("text")


def test_library_view_empty_and_no_match_search(test_root):
    """Verify empty queries return early and empty results render clear empty state."""
    mock_app = Mock(spec=GUIApplication)
    mock_app.search_knowledge.return_value = []

    view = LibraryView(parent=test_root, application=mock_app)

    # Empty query
    assert view.search("   ") == []
    mock_app.search_knowledge.assert_not_called()

    # No match query
    res = view.search("nonexistent topic")
    mock_app.search_knowledge.assert_called_once_with("nonexistent topic")
    assert res == []

    viewer_text = view.display.get("1.0", "end")
    assert "No relevant documents found." in viewer_text
    assert "0 matches found" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 3. Knowledge Search: Async Execution
# ---------------------------------------------------------------------------


def test_library_view_async_search(test_root):
    """Verify non-blocking search_async() runs background search and updates display."""
    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window)

    def fake_search(query: str, minimum_score: float = 0.0):
        return [
            {
                "content": f"Async result for {query}",
                "score": 0.88,
                "source": "async_doc.txt",
                "metadata": {"type": "test"},
            }
        ]

    app.search_knowledge = fake_search  # type: ignore[assignment]
    view = LibraryView(parent=test_root, application=app)

    completed_results: list[dict] = []

    def on_done(res):
        completed_results.extend(res)
        test_root.quit()

    view.search_async("transformers", on_complete=on_done)

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(completed_results) == 1
    assert "Async result for transformers" in completed_results[0]["content"]

    viewer_text = view.display.get("1.0", "end")
    assert "Async result for transformers" in viewer_text
    assert "Source: async_doc.txt" in viewer_text
    assert "1 matches found" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 4. Document Listing, Treeview, and Refresh
# ---------------------------------------------------------------------------


def test_library_view_document_listing_and_refresh(test_root):
    """Verify LibraryView populates doc_tree from application.list_documents()."""
    mock_app = Mock(spec=GUIApplication)
    mock_app.list_documents.return_value = [
        {
            "id": "doc-001",
            "title": "Quantum Principles",
            "chunks_count": 5,
            "status": "indexed",
            "collection": "physics",
        },
        {
            "id": "doc-002",
            "title": "Graph Algorithms",
            "chunks_count": 8,
            "status": "indexed",
            "collection": "cs",
        },
    ]

    view = LibraryView(parent=test_root, application=mock_app)
    view.refresh_documents()

    mock_app.list_documents.assert_called()

    children = view.doc_tree.get_children()
    assert len(children) == 2
    assert "doc-001" in children
    assert "doc-002" in children

    row1 = view.doc_tree.item("doc-001")["values"]
    assert row1[0] == "doc-001"
    assert row1[1] == "Quantum Principles"
    assert row1[2] == 5
    assert row1[3] == "indexed"

    assert "2 documents indexed" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 5. Document Inspection & Preview
# ---------------------------------------------------------------------------


def test_library_view_document_preview_selection(test_root):
    """Verify selecting a document in doc_tree renders full metadata and chunks into preview_text."""
    mock_app = Mock(spec=GUIApplication)
    mock_app.list_documents.return_value = [
        {
            "id": "doc-alpha",
            "title": "Alpha Research Document",
            "chunks_count": 2,
            "status": "indexed",
        }
    ]
    mock_app.get_document.return_value = {
        "id": "doc-alpha",
        "title": "Alpha Research Document",
        "collection": "general",
        "status": "indexed",
        "chunks_count": 2,
        "content_hash": "a1b2c3d4e5f67890abcdef1234567890",
        "content": "This is the complete text of the alpha research document for preview testing.",
        "chunks": [
            {"content": "This is chunk 1 of alpha document."},
            {"content": "This is chunk 2 of alpha document."},
        ],
    }

    view = LibraryView(parent=test_root, application=mock_app)
    view.refresh_documents()

    # Simulate selection
    view.doc_tree.selection_set("doc-alpha")
    view._on_doc_selected()

    mock_app.get_document.assert_called_once_with("doc-alpha")

    preview = view.preview_text.get("1.0", "end")
    assert "Document: Alpha Research Document (doc-alpha)" in preview
    assert "Collection: general" in preview
    assert "Status: indexed" in preview
    assert "SHA-256: a1b2c3d4e5f67890..." in preview
    assert "This is the complete text of the alpha research document" in preview
    assert "Chunk #1: This is chunk 1 of alpha document." in preview
    assert "Chunk #2: This is chunk 2 of alpha document." in preview


# ---------------------------------------------------------------------------
# 6. Document Ingestion: File Import & Raw Text
# ---------------------------------------------------------------------------


def test_library_view_import_file(test_root):
    """Verify import_file() reads and ingests document from disk."""
    km = KnowledgeManager()
    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window, knowledge_manager=km)
    view = LibraryView(parent=test_root, application=app)

    tmp_dir = Path(tempfile.mkdtemp())
    tmp_path = tmp_dir / "sample_test_doc.md"
    tmp_path.write_text(
        "# Knowledge Ingestion Test\n\nThis is a sample markdown document for Part 7.",
        encoding="utf-8",
    )

    try:
        view.import_file(file_path=tmp_path, async_op=False)
        children = view.doc_tree.get_children()
        assert len(children) == 1
        item = view.doc_tree.item(children[0])["values"]
        assert "Knowledge Ingestion Test" in str(item[1])
        assert "Imported" in view.status_label.cget("text")
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        if tmp_dir.exists():
            try:
                tmp_dir.rmdir()
            except Exception:
                pass


def test_library_view_add_text_document(test_root):
    """Verify add_text_document() registers and indexes raw content."""
    km = KnowledgeManager()
    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window, knowledge_manager=km)
    view = LibraryView(parent=test_root, application=app)

    view.add_text_document(
        title="Direct Thesis",
        content="Direct thesis statement exploring generative AI applications.",
        collection="default",
        async_op=False,
    )

    children = view.doc_tree.get_children()
    assert len(children) == 1
    assert "Direct Thesis" in view.doc_tree.item(children[0])["values"][1]
    assert "Added 'Direct Thesis'" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 7. Document Removal & Reindexing Lifecycle
# ---------------------------------------------------------------------------


def test_library_view_remove_document(test_root):
    """Verify remove_selected_document() removes document from KnowledgeManager and updates UI."""
    km = KnowledgeManager()
    doc = KnowledgeDocument(
        identifier="remove-me",
        title="Temporary Document",
        content="This document will be deleted.",
    )
    km.add_document(doc)

    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window, knowledge_manager=km)
    view = LibraryView(parent=test_root, application=app)

    assert len(view.doc_tree.get_children()) == 1

    # Select and remove synchronously
    view.doc_tree.selection_set("remove-me")
    view.remove_selected_document(async_op=False)

    # Doc tree should now be empty
    assert len(view.doc_tree.get_children()) == 0
    assert "Removed document 'remove-me'" in view.status_label.cget("text")
    assert "Select a document from the list above" in view.preview_text.get("1.0", "end")


def test_library_view_reindex_all(test_root):
    """Verify reindex_all() triggers reindexing across collections."""
    km = KnowledgeManager()
    doc1 = KnowledgeDocument(identifier="d1", title="Doc 1", content="Content one.")
    doc2 = KnowledgeDocument(identifier="d2", title="Doc 2", content="Content two.")
    km.add_document(doc1)
    km.add_document(doc2)

    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window, knowledge_manager=km)
    view = LibraryView(parent=test_root, application=app)

    view.reindex_all(async_op=False)

    assert "Reindexing complete" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 8. Async Document Operations
# ---------------------------------------------------------------------------


def test_library_view_async_add_and_reindex(test_root):
    """Verify async add and reindex operations complete properly through event loop."""
    km = KnowledgeManager()
    window = GUIWindow(root=test_root)
    app = GUIApplication(window=window, knowledge_manager=km)
    view = LibraryView(parent=test_root, application=app)

    added_box = []

    def on_add_done(info):
        added_box.append(info)
        test_root.quit()

    view.add_text_document(
        title="Async Paper",
        content="Exploring non-blocking asynchronous event dispatching in Tk.",
        async_op=True,
        on_complete=on_add_done,
    )

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(added_box) == 1
    assert added_box[0]["title"] == "Async Paper"
    assert len(view.doc_tree.get_children()) == 1


# ---------------------------------------------------------------------------
# 9. Error Handling
# ---------------------------------------------------------------------------


def test_library_view_error_handling(test_root):
    """Verify search, import, and remove errors surface cleanly without crashes."""
    mock_app = Mock(spec=GUIApplication)
    mock_app.search_knowledge.side_effect = RuntimeError("Retrieval engine unavailable")
    mock_app.list_documents.side_effect = RuntimeError("Storage corrupted")

    view = LibraryView(parent=test_root, application=mock_app)

    # Search error
    res = view.search("failing query")
    assert res == []
    viewer_text = view.display.get("1.0", "end")
    assert "Knowledge search error: Retrieval engine unavailable" in viewer_text
    assert "Search error: Retrieval engine unavailable" in view.status_label.cget("text")

    # Refresh error
    view.refresh_documents()
    assert "Error listing documents: Storage corrupted" in view.status_label.cget("text")


# ---------------------------------------------------------------------------
# 10. End-to-End Integration with bootstrap_runtime()
# ---------------------------------------------------------------------------


def test_knowledge_library_end_to_end_with_bootstrap_runtime(test_root, runtime_services):
    """
    Full end-to-end integration test of Knowledge Library UX:
    - Bootstraps real runtime services
    - Integrates GUIApplication and GUIWindow
    - Ingests a new document via LibraryView
    - Verifies document appears in treeview with preview
    - Executes search via LibraryView and retrieves the document chunks
    """
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_library()
    view: LibraryView = window.library_view

    # 1. Add document to knowledge base synchronously
    view.add_text_document(
        title="Scholarly RAG Synthesis",
        content="Scholarly RAG Synthesis incorporates hybrid retrieval fusing keyword and vector semantics.",
        collection="default",
        async_op=False,
    )

    # 2. Check that it appears in doc_tree
    children = view.doc_tree.get_children()
    assert len(children) >= 1

    # 3. Select and preview
    view.doc_tree.selection_set(children[0])
    view._on_doc_selected()
    preview = view.preview_text.get("1.0", "end")
    assert "Scholarly RAG Synthesis" in preview
    assert "hybrid retrieval fusing keyword and vector semantics" in preview

    # 4. Search for the document content
    results = view.search("hybrid retrieval")
    assert isinstance(results, list)
    viewer_text = view.display.get("1.0", "end")
    assert "Searching for: hybrid retrieval" in viewer_text

    # 5. Clean up
    integration.application.shutdown()
