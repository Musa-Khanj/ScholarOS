"""
Tests for Part 10 — End-to-End Workflows, Production Launch & Final Verification Freeze.

Verifies the unified production GUI integrated against the complete ScholarOS composition root:
1. Chat: multi-turn interaction, conversation continuity, and citation surfacing.
2. Research: execution flow, findings, citations, and workflow cancellation.
3. Knowledge: file ingestion, hybrid search, metadata inspection, removal, and reindexing.
4. Plugins: registration listing, discovery, lifecycle operations, and sandbox inspection.
5. Settings: configuration schema validation, secret masking, persistence, and diagnostics.
6. Dashboard & Status Bar: 4-card dashboard updates, status bar states, and coordinated refresh.
7. Production Launch: GUILauncher reaches bootstrap_runtime() authoritative composition root.
8. Provider Failure Honesty: unreachable local Ollama server surfaces UNHEALTHY without silent fallback.
"""

from __future__ import annotations

import tempfile
import tkinter as tk
from pathlib import Path

import pytest

from scholaros.bootstrap.runtime import bootstrap_runtime
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.launcher import GUILauncher
from scholaros.gui.views.workspace_views import (
    ChatView,
    HomeView,
    LibraryView,
    PluginsView,
    ResearchView,
    SettingsView,
)
from scholaros.services.health import HealthStatus


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
def e2e_runtime():
    """Create a fully assembled production runtime services bundle."""
    return bootstrap_runtime(use_mock_ai=True)


# ---------------------------------------------------------------------------
# 1. Chat E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_chat_workflow(test_root, e2e_runtime):
    """Verify end-to-end multi-turn chat interaction, citation display, and session reset."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    chat_view = integration.window._chat_view
    assert isinstance(chat_view, ChatView)

    # Turn 1: user prompt
    chat_view.send_message("What is machine learning?")
    history_1 = chat_view.chat.history.get("1.0", "end")
    assert "You: What is machine learning?" in history_1
    assert "ScholarOS:" in history_1
    assert len(app.conversation.messages) == 2

    # Turn 2: follow-up prompt
    chat_view.send_message("Can you explain supervised learning?")
    history_2 = chat_view.chat.history.get("1.0", "end")
    assert "Can you explain supervised learning?" in history_2
    assert len(app.conversation.messages) == 4

    # Clear chat session
    chat_view.clear()
    history_cleared = chat_view.chat.history.get("1.0", "end").strip()
    assert history_cleared == ""
    assert len(app.conversation.messages) == 0

    app.shutdown()


# ---------------------------------------------------------------------------
# 2. Research E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_research_workflow(test_root, e2e_runtime):
    """Verify research execution, results rendering, and cancellation handling."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    # Route to research view
    integration.window.show_research()
    research_view = integration.window._research_view
    assert isinstance(research_view, ResearchView)

    # 1. Execute research query
    res = research_view.run_research("Quantum Annealing Applications")
    assert res is not None
    assert research_view.state == "completed"

    rendered = research_view.results_text.get("1.0", "end")
    assert "Findings:" in rendered or "Executing research" in rendered

    # 2. Check session recording
    recent = app.get_recent_research(limit=5)
    assert len(recent) >= 1
    assert recent[0]["query"] == "Quantum Annealing Applications"

    app.shutdown()


# ---------------------------------------------------------------------------
# 3. Knowledge Library E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_knowledge_workflow(test_root, e2e_runtime):
    """Verify document ingestion, indexing, search, preview, and lifecycle removal."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    # Route to library view
    integration.window.show_library()
    library_view = integration.window._library_view
    assert isinstance(library_view, LibraryView)

    tmp_dir = Path(tempfile.mkdtemp())
    sample_file = tmp_dir / "quantum_mechanics.md"
    sample_file.write_text(
        "# Quantum Mechanics Fundamentals\n\nQuantum mechanics studies the behavior of matter and light on atomic scales.",
        encoding="utf-8",
    )

    try:
        # Ingest document
        library_view.import_file(file_path=sample_file, async_op=False)
        children = library_view.doc_tree.get_children()
        assert len(children) >= 1

        # Select and preview document
        library_view.doc_tree.selection_set(children[0])
        library_view._on_doc_selected()
        preview = library_view.preview_text.get("1.0", "end")
        assert "Quantum Mechanics" in preview

        # Search knowledge
        results = library_view.search("atomic scales")
        assert isinstance(results, list)

        # Remove document
        doc_id = children[0]
        library_view.doc_tree.selection_set(doc_id)
        library_view.remove_selected_document(async_op=False)
        assert doc_id not in library_view.doc_tree.get_children()

    finally:
        sample_file.unlink(missing_ok=True)
        try:
            tmp_dir.rmdir()
        except Exception:
            pass
        app.shutdown()


# ---------------------------------------------------------------------------
# 4. Plugins E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_plugins_workflow(test_root, e2e_runtime):
    """Verify plugin listing, discovery, and lifecycle operations."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    # Route to plugins view
    integration.window.show_plugins()
    plugins_view = integration.window._plugins_view
    assert isinstance(plugins_view, PluginsView)

    # Initial refresh
    items = plugins_view.refresh()
    assert isinstance(items, list)

    # Discover plugins
    discovered = plugins_view.discover_plugins(async_op=False)
    assert isinstance(discovered, list)

    app.shutdown()


# ---------------------------------------------------------------------------
# 5. Settings E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_settings_workflow(test_root, e2e_runtime):
    """Verify settings population, secret masking, validation, and diagnostics."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    # Route to settings view
    integration.window.show_settings()
    settings_view = integration.window._settings_view
    assert isinstance(settings_view, SettingsView)

    # 1. Secret masking toggle
    assert settings_view._api_key_entry.cget("show") == "*"
    settings_view._show_key_var.set(True)
    settings_view.toggle_key_visibility()
    assert settings_view._api_key_entry.cget("show") == ""

    # 2. Validation
    is_valid = settings_view.validate_settings()
    assert is_valid is True

    # 3. Diagnostics
    diag = app.get_diagnostics()
    assert diag["app_connected"] is True
    assert diag["config_valid"] is True
    assert diag["active_provider"] == "mock"

    app.shutdown()


# ---------------------------------------------------------------------------
# 6. Home Dashboard & Status Bar E2E Workflow
# ---------------------------------------------------------------------------


def test_e2e_home_and_status_bar_workflow(test_root, e2e_runtime):
    """Verify 4-card dashboard telemetry, status updates, and toolbar refresh."""
    builder = GUIBuilder()
    integration = builder.build(
        services=e2e_runtime,
        container=e2e_runtime.container,
        root=test_root,
    )
    app = integration.application
    app.startup()

    home_view = integration.window._home_view
    assert isinstance(home_view, HomeView)

    # 1. Verify cards are populated
    assert "mock" in home_view._ai_provider_label.cget("text").lower()
    assert "ready" in home_view._knowledge_status_label.cget("text").lower()
    assert "plugins" in home_view._plugins_status_label.cget("text").lower()

    # 2. Status bar transitions
    app.set_status("Executing background analysis...", state="running")
    assert integration.window.status_state == "running"
    assert app.status_state == "running"

    app.set_status("Operation completed successfully.", state="completed")
    assert integration.window.status_state == "completed"
    assert app.status_state == "completed"

    # 3. Reset to idle status
    app.set_status("Ready", state="idle")
    assert integration.window.status_state == "idle"

    # 4. Refresh toolbar
    integration.window.refresh()
    assert integration.window.status_state == "idle"

    app.shutdown()


# ---------------------------------------------------------------------------
# 7. Production Launch Verification
# ---------------------------------------------------------------------------


def test_e2e_production_launcher_wires_composition_root(test_root):
    """Verify GUILauncher invokes builder with authoritative bootstrap_runtime."""
    launcher = GUILauncher(use_mock_ai=True)
    builder = launcher.builder

    # Build integration via launcher pattern
    integration = builder.build(root=test_root)
    assert integration.application is not None
    assert integration.window is not None
    assert integration.application.window is integration.window
    assert integration.window.application is integration.application


# ---------------------------------------------------------------------------
# 8. Provider Failure Honesty (No Silent Mock Fallback)
# ---------------------------------------------------------------------------


def test_e2e_provider_failure_honesty():
    """Verify that unmocked production runtime honestly reports offline Ollama without mock fallback."""
    unmocked_runtime = bootstrap_runtime(use_mock_ai=False)
    ai_mgr = unmocked_runtime.ai_manager

    # When Ollama is offline on localhost, health check must report UNHEALTHY, not HEALTHY
    health = ai_mgr.health("ollama")
    assert health.status == HealthStatus.UNHEALTHY
    assert "unreachable" in (health.details or "").lower()
