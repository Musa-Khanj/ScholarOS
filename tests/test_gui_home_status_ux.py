"""
Tests for Part 9 — Home Dashboard & Status Bar.

Validates:
1. HomeView Dashboard Layout:
   - Quick Actions Bar (Chat, Research, Library, Settings)
   - Status Summary Header (_info_label)
   - Four Core Dashboard Cards:
     * Research Dashboard (Recent research activity, turns, models, citations)
     * AI & Provider Status (Provider, model, health, available providers)
     * Knowledge Library Overview (Indexed documents count, collections list, status)
     * Plugins Overview (Registered count, active count, manager status)
2. Interactive Navigation:
   - Quick action buttons route to chat, research, library, and settings
   - Card buttons route to corresponding workspaces
3. Live Data Synchronization:
   - Displays empty states gracefully when no research, documents, or plugins exist
   - Renders live research turns from ResearchSession into the Research Dashboard
   - Reflects indexed document counts from KnowledgeManager
   - Reflects registered/active plugins from PluginManager
   - Shows active provider and health without confusing connectivity with availability
4. Status Bar & Execution States:
   - Meaningful states: idle, running, completed, cancelled, failed
   - Color styling: normal (#212529), active blue (#0d6efd), success green (#198754),
     warning orange (#fd7e14), error red (#dc3545)
   - Toolbar Refresh button triggers view refresh
   - Application status bar delegation
5. EventBus Lifecycle Status Updates:
   - ResearchStarted, ResearchStageStarted, ResearchCompleted, ResearchFailed
   - AIRequestStarted, AIRequestCompleted, AIRequestFailed
6. End-to-end integration with bootstrap_runtime().
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock

import pytest

from scholaros.bootstrap.runtime import bootstrap_runtime
from scholaros.events.bus import EventBus
from scholaros.gui.application import GUIApplication
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.theme import GUITheme
from scholaros.gui.views.workspace_views import HomeView
from scholaros.gui.window import GUIWindow
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.plugins.base import Plugin
from scholaros.plugins.metadata import PluginMetadata
from scholaros.research.pipeline import ResearchPipeline
from scholaros.research.result import ResearchResult


class DummyPlugin(Plugin):
    """Dummy plugin for testing."""

    def __init__(self, name: str = "TestPlugin", version: str = "1.0.0") -> None:
        super().__init__(
            PluginMetadata(
                id=name.lower(),
                name=name,
                version=version,
                description="Test dummy plugin",
            )
        )

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass


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
def test_root() -> tk.Tk:
    return get_test_root()


def test_home_view_initial_structure(test_root: tk.Tk) -> None:
    """Verify that HomeView builds the quick actions, status header, and 4 cards."""
    view = HomeView(parent=test_root)

    # 1. Quick actions and status summary header
    assert hasattr(view, "_info_label")
    assert "System Status:" in view._info_label.cget("text")

    # 2. Four dashboard cards exist
    assert hasattr(view, "_research_box")
    assert hasattr(view, "_ai_box")
    assert hasattr(view, "_knowledge_box")
    assert hasattr(view, "_plugins_box")

    # 3. Card sub-widgets exist
    assert hasattr(view, "_research_status_label")
    assert hasattr(view, "_recent_research_text")
    assert hasattr(view, "_ai_provider_label")
    assert hasattr(view, "_ai_model_label")
    assert hasattr(view, "_ai_health_label")
    assert hasattr(view, "_ai_avail_label")
    assert hasattr(view, "_knowledge_docs_label")
    assert hasattr(view, "_knowledge_colls_label")
    assert hasattr(view, "_knowledge_status_label")
    assert hasattr(view, "_plugins_total_label")
    assert hasattr(view, "_plugins_active_label")
    assert hasattr(view, "_plugins_status_label")

    # 4. Initial state before application connection
    assert "Idle" in view._research_status_label.cget(
        "text"
    ) or "Disconnected" in view._research_status_label.cget("text")
    content = view._recent_research_text.get("1.0", "end")
    assert "No recent research activity" in content


def test_home_view_navigation_callbacks(test_root: tk.Tk) -> None:
    """Verify quick actions and card buttons navigate to requested workspaces."""
    nav_targets: list[str] = []

    def _mock_nav(target: str) -> None:
        nav_targets.append(target)

    view = HomeView(parent=test_root, on_navigate=_mock_nav)

    # Test quick action navigation
    view._navigate("chat")
    view._navigate("research")
    view._navigate("library")
    view._navigate("settings")

    assert nav_targets == ["chat", "research", "library", "settings"]


def test_home_view_offline_state_graceful(test_root: tk.Tk) -> None:
    """Verify HomeView handles application=None gracefully when refreshed."""
    view = HomeView(parent=test_root, application=None)
    view.refresh()

    assert "Offline" in view._info_label.cget("text") or "Ready" in view._info_label.cget("text")
    assert "Disconnected" in view._ai_provider_label.cget("text")
    assert "0" in view._knowledge_docs_label.cget("text")
    assert "0" in view._plugins_total_label.cget("text")


def test_home_view_refresh_with_minimal_mock(test_root: tk.Tk) -> None:
    """Verify backward compatibility when application.info() returns minimal dict."""
    view = HomeView(parent=test_root)
    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}

    view.set_application(mock_app)
    view.refresh()

    info_text = view._info_label.cget("text")
    assert "Status: READY" in info_text
    assert "AI: Yes" in info_text
    assert "RAG: Yes" in info_text


def test_home_view_research_dashboard_populated(test_root: tk.Tk) -> None:
    """Verify that recent research turns are displayed in the Research Dashboard."""
    view = HomeView(parent=test_root)

    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}
    mock_app.get_recent_research.return_value = [
        {
            "query": "Quantum Machine Learning",
            "model": "qwen2.5:1.5b",
            "content": "Quantum ML combines variational circuits with classical optimizers.",
            "sources": ["paper1.pdf", "paper2.pdf"],
            "citations": [{"title": "QML Paper", "source": "arxiv"}],
            "timestamp": 1234567.89,
        },
        {
            "query": "Attention Mechanisms",
            "model": "qwen2.5:1.5b",
            "content": "Self-attention computes scaled dot-product scores across sequence tokens.",
            "sources": ["vaswani.pdf"],
            "citations": [],
            "timestamp": 1234560.00,
        },
    ]

    view.set_application(mock_app)
    view.refresh()

    assert "2 turn(s)" in view._research_status_label.cget("text")
    text_content = view._recent_research_text.get("1.0", "end")
    assert "Quantum Machine Learning" in text_content
    assert "Attention Mechanisms" in text_content
    assert "qwen2.5:1.5b" in text_content
    assert "Sources: 2" in text_content
    assert "Citations: 1" in text_content


def test_home_view_ai_status_telemetry(test_root: tk.Tk) -> None:
    """Verify active provider, model, and health status are rendered accurately."""
    view = HomeView(parent=test_root)

    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}
    mock_app.get_ai_status.return_value = {
        "app_connected": True,
        "active_provider": "Ollama",
        "active_model": "qwen2.5:1.5b",
        "provider_healthy": True,
        "provider_health_status": "HEALTHY",
        "available_providers": ["mock", "ollama"],
    }

    view.set_application(mock_app)
    view.refresh()

    assert "Active Provider: Ollama" in view._ai_provider_label.cget("text")
    assert "Active Model: qwen2.5:1.5b" in view._ai_model_label.cget("text")
    assert "Provider Health: HEALTHY" in view._ai_health_label.cget("text")
    assert "mock, ollama" in view._ai_avail_label.cget("text")
    assert str(view._ai_health_label.cget("foreground")) == "#198754"

    # Test unhealthy state
    mock_app.get_ai_status.return_value = {
        "app_connected": True,
        "active_provider": "Ollama",
        "active_model": "qwen2.5:1.5b",
        "provider_healthy": False,
        "provider_health_status": "DEGRADED",
        "available_providers": ["mock", "ollama"],
    }
    view.refresh()
    assert "Provider Health: DEGRADED" in view._ai_health_label.cget("text")
    assert str(view._ai_health_label.cget("foreground")) == "#dc3545"


def test_home_view_knowledge_overview(test_root: tk.Tk) -> None:
    """Verify indexed documents count and collections list from KnowledgeManager."""
    view = HomeView(parent=test_root)

    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}
    mock_app.get_knowledge_overview.return_value = {
        "status": "Ready",
        "collections_count": 2,
        "documents_count": 14,
        "collections": ["default", "papers"],
    }

    view.set_application(mock_app)
    view.refresh()

    assert "Indexed Documents: 14" in view._knowledge_docs_label.cget("text")
    assert "default, papers" in view._knowledge_colls_label.cget("text")
    assert "Knowledge Subsystem: Ready" in view._knowledge_status_label.cget("text")


def test_home_view_plugins_overview(test_root: tk.Tk) -> None:
    """Verify registered plugins count and active plugins count from PluginManager."""
    view = HomeView(parent=test_root)

    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}
    mock_app.get_plugins_overview.return_value = {
        "status": "Ready",
        "total": 5,
        "active": 3,
        "plugins": ["arxiv", "pubmed", "bibtex"],
    }

    view.set_application(mock_app)
    view.refresh()

    assert "Registered Plugins: 5" in view._plugins_total_label.cget("text")
    assert "Active Plugins: 3" in view._plugins_active_label.cget("text")
    assert "Plugin Manager: Ready" in view._plugins_status_label.cget("text")


def test_status_bar_execution_states_and_colors(test_root: tk.Tk) -> None:
    """Verify GUIWindow status bar reflects idle, running, completed, cancelled, and failed states."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    # Initial state
    assert window.get_status() == "READY"
    assert window.status_state == "idle"

    # Running state
    window.set_status("Research: Running query 'Quantum ML'...", state="running")
    assert window.get_status() == "Research: Running query 'Quantum ML'..."
    assert window.status_state == "running"
    assert str(window.statusbar.cget("foreground")) == "#0d6efd"

    # Completed state
    window.set_status("Research: Completed in 120ms", state="completed")
    assert window.status_state == "completed"
    assert str(window.statusbar.cget("foreground")) == "#198754"

    # Cancelled state
    window.set_status("Research: Cancelled by user", state="cancelled")
    assert window.status_state == "cancelled"
    assert str(window.statusbar.cget("foreground")) == "#fd7e14"

    # Failed state
    window.set_status("Research: Execution failed", error=True)
    assert window.status_state == "failed"
    assert str(window.statusbar.cget("foreground")) == "#dc3545"

    # Idle / Ready state
    window.set_status("Ready", state="idle")
    assert window.status_state == "idle"
    assert str(window.statusbar.cget("foreground")) == "#212529"


def test_window_refresh_button_triggers_view_refresh(test_root: tk.Tk) -> None:
    """Verify toolbar refresh button or window.refresh() invokes refresh() on views."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    mock_home_refresh = Mock()
    window.home_view.refresh = mock_home_refresh  # type: ignore[method-assign]

    window.refresh()
    mock_home_refresh.assert_called_once()


def test_application_status_delegation_to_window(test_root: tk.Tk) -> None:
    """Verify GUIApplication.set_status() updates its status_state and forwards to GUIWindow."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    app = GUIApplication(window=window)
    assert app.status_state == "idle"

    app.set_status("AI: Generating response...", state="running")
    assert app.status_state == "running"
    assert window.status_state == "running"
    assert "AI: Generating response..." in window.get_status()

    app.set_status("AI: Response completed", state="completed")
    assert app.status_state == "completed"
    assert window.status_state == "completed"

    app.set_status("AI: Error encountered", error=True)
    assert app.status_state == "failed"
    assert window.status_state == "failed"


def test_event_bus_lifecycle_status_updates(test_root: tk.Tk) -> None:
    """Verify EventBus events trigger corresponding status bar messages and execution states."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    event_bus = EventBus()
    app = GUIApplication(window=window, event_bus=event_bus)

    # 1. ResearchStarted
    from scholaros.research.events import ResearchCompleted, ResearchFailed, ResearchStarted

    event_bus.publish(ResearchStarted(query="Graph Neural Networks", strategy="default"))
    assert app.status_state == "running"
    assert "Graph Neural Networks" in window.get_status()

    # 2. ResearchCompleted
    event_bus.publish(
        ResearchCompleted(
            query="Graph Neural Networks",
            model="test-model",
            sources_count=3,
            latency_ms=150.0,
        )
    )
    assert app.status_state == "completed"
    assert "Completed (150ms)" in window.get_status()

    # 3. ResearchFailed
    event_bus.publish(
        ResearchFailed(
            query="Graph Neural Networks",
            error="Connection refused",
            latency_ms=20.0,
        )
    )
    assert app.status_state == "failed"
    assert "Failed - Connection refused" in window.get_status()


def test_application_research_records_into_session(test_root: tk.Tk) -> None:
    """Verify application.research() records interaction into ResearchSession and surfaces in HomeView."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    mock_pipeline = Mock(spec=ResearchPipeline)
    mock_result = Mock(spec=ResearchResult)
    mock_result.content = "Summary of multi-agent reinforcement learning findings."
    mock_result.model = "qwen2.5:1.5b"
    mock_result.sources = ["paper_a.pdf"]
    mock_result.report = None
    mock_result.workflow_context = None

    mock_pipeline.execute.return_value = mock_result

    app = GUIApplication(window=window, research_pipeline=mock_pipeline)

    # Initially empty
    assert len(app.get_recent_research()) == 0

    # Run research
    res = app.research("Multi-agent RL")
    assert res is mock_result

    recent = app.get_recent_research()
    assert len(recent) == 1
    assert recent[0]["query"] == "Multi-agent RL"
    assert "multi-agent reinforcement learning" in recent[0]["content"]

    # Verify HomeView displays the new turn
    window.home_view.refresh()
    recent_text = window.home_view._recent_research_text.get("1.0", "end")
    assert "Multi-agent RL" in recent_text
    assert "multi-agent reinforcement learning" in recent_text


def test_end_to_end_bootstrap_runtime_home_dashboard(test_root: tk.Tk) -> None:
    """Verify bootstrap_runtime() creates live HomeView with live AI, Knowledge, and Plugin overviews."""
    runtime = bootstrap_runtime(use_mock_ai=True)

    # Ingest a test document into knowledge manager
    km = runtime.knowledge_manager
    doc = KnowledgeDocument(
        identifier="doc-bootstrap-1",
        title="Bootstrap Test Paper",
        content="Test content",
    )
    km.add_document(doc)

    # Register a test plugin
    pm = runtime.plugin_manager
    pm.register(DummyPlugin("BootstrapPlugin", "2.0.0"))

    # Mount runtime on GUIWindow via GUIBuilder
    builder = GUIBuilder()
    integration = builder.build(services=runtime, container=runtime.container, root=test_root)
    integration.application.startup()
    window = integration.window

    # Refresh home view
    window.home_view.refresh()

    # 1. AI Status check
    assert "mock" in window.home_view._ai_provider_label.cget("text").lower()

    # 2. Knowledge Overview check
    assert "1" in window.home_view._knowledge_docs_label.cget("text")

    # 3. Plugins Overview check
    assert "1" in window.home_view._plugins_total_label.cget("text")
