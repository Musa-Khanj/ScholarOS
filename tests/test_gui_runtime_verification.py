"""
Tests for Part 4 — Runtime Verification Checkpoint.

Proves that production workspace views are wired to real V1 services:
- Production application context & service resolution via bootstrap_runtime()
- SettingsView runtime information & active provider/model state
- PluginsView connectivity to PluginManager
- ChatView delegation through GUIApplication to AI / RAG / Provider
- ResearchView delegation through GUIApplication to ResearchPipeline
- LibraryView delegation through GUIApplication to Knowledge / Retrieval
- Graceful behavior when services are missing / unconfigured
"""

from __future__ import annotations

import tkinter as tk

import pytest

from scholaros.bootstrap.runtime import bootstrap_runtime
from scholaros.gui.application import ApplicationState, GUIApplication
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.theme import GUITheme
from scholaros.gui.views.workspace_views import (
    ChatView,
    LibraryView,
    PluginsView,
    ResearchView,
    SettingsView,
)
from scholaros.gui.window import GUIWindow
from scholaros.plugins.base import Plugin
from scholaros.plugins.metadata import PluginMetadata
from scholaros.research.result import ResearchResult


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


# ===========================================================================
# 1. Production Application Context & Service Resolution
# ===========================================================================


def test_production_application_context_and_service_resolution(test_root, runtime_services):
    """Verify production composition root registers and resolves all real V1 managers."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )

    app = integration.application
    assert app is not None
    assert app.state == ApplicationState.INITIALIZED

    # Startup application
    app.startup()
    assert app.state == ApplicationState.RUNNING
    assert app.is_running is True
    assert app.status() == "READY"

    # Verify actual production managers are resolved and bound
    assert app.ai_manager is runtime_services.ai_manager
    assert app.plugin_manager is runtime_services.plugin_manager
    assert app.knowledge_manager is runtime_services.knowledge_manager
    assert app.rag_pipeline is runtime_services.rag_pipeline
    assert app.rag_pipeline.retrieval_pipeline is runtime_services.retrieval_pipeline
    assert app.research_pipeline is runtime_services.research_pipeline
    assert app.config_manager is runtime_services.config_manager
    assert app.container is runtime_services.container

    # Verify window <-> application two-way binding
    assert app.window.application is app
    assert integration.window.application is app


# ===========================================================================
# 2. SettingsView Runtime Information Display
# ===========================================================================


def test_settings_view_runtime_information(test_root, runtime_services):
    """Verify SettingsView displays real runtime, provider, model, plugin, and knowledge telemetry."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_settings()
    settings_view: SettingsView = window.settings_view

    assert settings_view is not None
    assert isinstance(settings_view, SettingsView)

    # Refresh telemetry
    settings_view.refresh()
    content = settings_view._info_display.get("1.0", "end")

    # Assert real runtime diagnostic details
    assert "Runtime: Connected" in content
    assert "Provider: Mock" in content or "Provider: Ollama" in content
    assert "Plugin Manager: Connected" in content
    assert "Knowledge: Ready" in content

    # Crucially ensure offline/mock fallback message is NOT displayed
    assert "Application layer: Offline / Mock" not in content


# ===========================================================================
# 3. PluginsView Connectivity to PluginManager
# ===========================================================================


def test_plugin_manager_connectivity(test_root, runtime_services):
    """Verify PluginsView connects to real PluginManager and reflects registered state."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_plugins()
    plugins_view: PluginsView = window.plugins_view

    assert plugins_view is not None
    assert isinstance(plugins_view, PluginsView)

    # Initial state: PluginManager is connected
    content_initial = plugins_view._list_text.get("1.0", "end")
    assert "Plugin manager not connected." not in content_initial

    # Register a test plugin dynamically into the real production PluginManager
    class SampleRuntimePlugin(Plugin):
        def __init__(self) -> None:
            super().__init__(
                PluginMetadata(
                    id="test_analytics_plugin",
                    name="Test Analytics",
                    version="1.2.0",
                    description="Provides runtime telemetry and analysis.",
                )
            )

    sample_plugin = SampleRuntimePlugin()
    runtime_services.plugin_manager.register(sample_plugin)
    runtime_services.plugin_manager.enable("test_analytics_plugin")

    # Refresh view
    plugins = plugins_view.refresh()
    content_after = plugins_view._list_text.get("1.0", "end")

    assert any(p["id"] == "test_analytics_plugin" for p in plugins)
    assert "Test Analytics" in content_after
    assert "v1.2.0" in content_after
    assert "Plugin manager not connected." not in content_after


# ===========================================================================
# 4. ChatView Delegation through Production AI / RAG
# ===========================================================================


def test_chat_view_delegation_to_ai_provider(test_root, runtime_services):
    """Verify ChatView sends messages through GUIApplication to the real AI / RAG provider."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_chat()
    chat_view: ChatView = window.chat_view

    assert chat_view is not None
    assert isinstance(chat_view, ChatView)

    # Send message through ChatView
    response = chat_view.send_message("Explain the hypothesis behind ScholarOS.")

    assert response is not None
    assert len(response) > 0
    # Response from configured MockProvider in runtime_services
    assert "ScholarOS V1" in response

    # Check that message was recorded in chat display
    chat_text = chat_view.chat.history.get("1.0", "end")
    assert "You: Explain the hypothesis behind ScholarOS." in chat_text
    assert "ScholarOS:" in chat_text
    assert "ScholarOS V1" in chat_text


# ===========================================================================
# 5. ResearchView Delegation through ResearchPipeline
# ===========================================================================


def test_research_view_delegation_to_research_pipeline(test_root, runtime_services):
    """Verify ResearchView executes research via ResearchPipeline returning ResearchResult."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_research()
    research_view: ResearchView = window.research_view

    assert research_view is not None
    assert isinstance(research_view, ResearchView)

    # Execute research through ResearchView
    result = research_view.run_research("Autonomous agents in multi-turn dialogues")

    assert result is not None
    assert isinstance(result, ResearchResult)
    assert result.content is not None
    assert len(result.content) > 0

    # Ensure findings are visible in the results viewer widget
    viewer_text = research_view._results_text.get("1.0", "end")
    assert "Findings:" in viewer_text
    assert result.content in viewer_text


# ===========================================================================
# 6. LibraryView Delegation through Knowledge / Retrieval
# ===========================================================================


def test_library_view_delegation_to_knowledge_retrieval(test_root, runtime_services):
    """Verify LibraryView queries the real RAG / Retrieval pipeline."""
    builder = GUIBuilder()
    integration = builder.build(
        services=runtime_services,
        container=runtime_services.container,
        root=test_root,
    )
    integration.application.startup()

    window = integration.window
    window.show_library()
    library_view: LibraryView = window.library_view

    assert library_view is not None
    assert isinstance(library_view, LibraryView)

    # Perform search via LibraryView on empty index
    results = library_view.search("quantum annealing")

    assert isinstance(results, list)
    viewer_text = library_view._display.get("1.0", "end")
    assert "Searching for: quantum annealing" in viewer_text
    # On empty in-memory vector store, it displays "No relevant documents found."
    assert "No relevant documents found." in viewer_text


# ===========================================================================
# 7. Missing Service Behavior & Fallback Handling
# ===========================================================================


def test_missing_service_behavior(test_root):
    """Verify system behaves gracefully and safely when subsystems are unconfigured."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    app = GUIApplication(window=window)  # No services or container

    assert app.ai_manager is None
    assert app.plugin_manager is None
    assert app.knowledge_manager is None
    assert app.research_pipeline is None
    assert app.rag_pipeline is None

    # Chat raises expected RuntimeError
    with pytest.raises(RuntimeError, match="No AI provider or RAG pipeline"):
        app.chat("hello")

    # Research raises expected RuntimeError
    with pytest.raises(RuntimeError, match="Research pipeline is not configured"):
        app.research("topic")

    # Search knowledge raises expected RuntimeError
    with pytest.raises(RuntimeError, match="RAG pipeline is not configured"):
        app.search_knowledge("topic")

    # Plugins list returns empty list
    assert app.list_plugins() == []

    # SettingsView without application shows offline indication
    settings_view = SettingsView(parent=test_root, application=None)
    content = settings_view._info_display.get("1.0", "end")
    assert "Application layer: Offline / Mock" in content

    # PluginsView without application shows not connected indication
    plugins_view = PluginsView(parent=test_root, application=None)
    p_content = plugins_view._list_text.get("1.0", "end")
    assert "Plugin manager not connected." in p_content
