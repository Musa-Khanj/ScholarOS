"""
Tests for Milestone 10L - GUI / Desktop Application Completion.

Validates:
- GUIApplication lifecycle (startup, shutdown, state tracking, status)
- GUI -> Application -> Services -> Core architecture
- Chat, Research, Knowledge/Library, and Plugin domain delegation
- Provider and model selection and switching
- Main window navigation and view switching (Home, Chat, Research, Library, Plugins, Settings)
- Status and error display mechanisms
- GUIBuilder dependency wiring
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock
import pytest

from scholaros.gui.application import ApplicationState, GUIApplication
from scholaros.gui.builder import GUIBuilder, create_application
from scholaros.gui.theme import GUITheme
from scholaros.gui.views.workspace_views import (
    ChatView,
    LibraryView,
    ResearchView,
    SettingsView,
)
from scholaros.gui.window import GUIWindow


# ---------------------------------------------------------------------------
# Shared Tk Root Fixture (Headless Safe)
# ---------------------------------------------------------------------------

_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    """Return a shared withdrawn Tk root instance for widget instantiation."""
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
def mock_window():
    window = Mock(spec=GUIWindow)
    window.root = get_test_root()
    window.build = Mock()
    window.show = Mock()
    window.set_status = Mock()
    window.get_status = Mock(return_value="Ready")
    return window


# ---------------------------------------------------------------------------
# 1. GUIApplication Lifecycle & State Tests
# ---------------------------------------------------------------------------

def test_gui_application_lifecycle(mock_window):
    """Verify application transitions through INITIALIZED -> RUNNING -> STOPPED."""
    app = GUIApplication(mock_window)
    assert app.state == ApplicationState.INITIALIZED
    assert app.is_running is False
    assert app.status() == "INITIALIZED"

    # Startup
    app.startup()
    assert app.state == ApplicationState.RUNNING
    assert app.is_running is True
    assert app.status() == "READY"
    mock_window.set_status.assert_called_with("Ready", error=False)

    # Info summary
    info = app.info()
    assert info["status"] == "READY"
    assert info["ai"] is False
    assert info["research"] is False
    assert info["rag"] is False

    # Shutdown
    app.shutdown()
    assert app.state == ApplicationState.STOPPED
    assert app.is_running is False
    assert app.status() == "STOPPED"
    mock_window.set_status.assert_called_with("Stopped", error=False)


# ---------------------------------------------------------------------------
# 2. Chat Delegation Tests (AIManager & RAG fallback)
# ---------------------------------------------------------------------------

def test_gui_application_chat_delegation(mock_window):
    """Verify chat delegates to AIManager without business logic in GUI."""
    mock_provider = Mock()
    mock_response = Mock(content="Hello from AI model")
    mock_provider.generate = Mock(return_value=mock_response)

    mock_ai = Mock()
    mock_ai.select_provider = Mock(return_value=mock_provider)

    app = GUIApplication(mock_window, ai_manager=mock_ai)
    reply = app.chat("Tell me about quantum computing", model="gpt-4o", provider="openai")

    assert reply == "Hello from AI model"
    mock_ai.select_provider.assert_called_once_with(
        model="gpt-4o",
        requested_provider="openai",
    )
    mock_provider.generate.assert_called_once()


def test_gui_application_chat_rag_fallback(mock_window):
    """Verify chat falls back to RAGPipeline when no AIManager is supplied."""
    mock_rag = Mock()
    mock_response = Mock(content="RAG response content")
    mock_rag.run = Mock(return_value=mock_response)

    app = GUIApplication(mock_window, rag_pipeline=mock_rag)
    reply = app.chat("Retrieve knowledge")

    assert reply == "RAG response content"
    mock_rag.run.assert_called_once()


def test_gui_application_chat_empty_prompt(mock_window):
    """Verify chat rejects empty prompts."""
    app = GUIApplication(mock_window)
    with pytest.raises(ValueError, match="cannot be empty"):
        app.chat("   ")


def test_gui_application_chat_no_provider(mock_window):
    """Verify chat raises error if no AI or RAG is configured."""
    app = GUIApplication(mock_window)
    with pytest.raises(RuntimeError, match="No AI provider or RAG pipeline"):
        app.chat("Hello")


# ---------------------------------------------------------------------------
# 3. Research Delegation Tests
# ---------------------------------------------------------------------------

def test_gui_application_research_delegation(mock_window):
    """Verify research delegates to ResearchPipeline."""
    mock_rp = Mock()
    mock_rp.execute = Mock(return_value="Research Findings")

    app = GUIApplication(mock_window, research_pipeline=mock_rp)
    res = app.research("Machine learning optimization")

    assert res == "Research Findings"
    mock_rp.execute.assert_called_once_with("Machine learning optimization")


def test_gui_application_research_template_delegation(mock_window):
    """Verify research executes with custom template and variables."""
    mock_rp = Mock()
    mock_rp.execute = Mock(return_value="Template Results")

    app = GUIApplication(mock_window, research_pipeline=mock_rp)
    res = app.research("AI safety", template="comparative_analysis", depth="deep")

    assert res == "Template Results"
    mock_rp.execute.assert_called_once_with(
        "comparative_analysis",
        query="AI safety",
        depth="deep",
    )


def test_gui_application_research_empty_query(mock_window):
    """Verify research rejects empty query strings."""
    app = GUIApplication(mock_window)
    with pytest.raises(ValueError, match="cannot be empty"):
        app.research("")


# ---------------------------------------------------------------------------
# 4. Knowledge / Library Search Tests
# ---------------------------------------------------------------------------

def test_gui_application_search_knowledge(mock_window):
    """Verify knowledge search delegates to RAGPipeline and formats results."""
    mock_source = Mock()
    mock_source.content = "Quantum annealing paper excerpt"
    mock_source.score = 0.94
    mock_source.source = "d-wave-paper.pdf"
    mock_source.metadata = {"year": 2024}

    mock_rag = Mock()
    mock_rag.run = Mock(return_value=Mock(sources=[mock_source]))

    app = GUIApplication(mock_window, rag_pipeline=mock_rag)
    results = app.search_knowledge("annealing", minimum_score=0.8)

    assert len(results) == 1
    assert results[0]["content"] == "Quantum annealing paper excerpt"
    assert results[0]["score"] == 0.94
    assert results[0]["source"] == "d-wave-paper.pdf"
    assert results[0]["metadata"]["year"] == 2024


def test_gui_application_search_knowledge_empty(mock_window):
    """Verify searching for whitespace returns empty list without calling RAG."""
    mock_rag = Mock()
    app = GUIApplication(mock_window, rag_pipeline=mock_rag)
    assert app.search_knowledge("   ") == []
    mock_rag.run.assert_not_called()


# ---------------------------------------------------------------------------
# 5. Provider & Model Selection Tests
# ---------------------------------------------------------------------------

def test_gui_application_provider_management(mock_window):
    """Verify listing and switching providers."""
    mock_ai = Mock()
    mock_ai.get_available_providers = Mock(return_value=("ollama", "openai", "anthropic"))

    m1 = Mock()
    m1.name = "gpt-4o"
    m2 = Mock()
    m2.name = "gpt-4o-mini"
    mock_ai.list_models = Mock(return_value=[m1, m2])

    app = GUIApplication(mock_window, ai_manager=mock_ai)

    providers = app.list_providers()
    assert providers == ["ollama", "openai", "anthropic"]

    models = app.list_models(provider="openai")
    assert models == ["gpt-4o", "gpt-4o-mini"]

    app.set_provider("openai")
    mock_ai.switch_provider.assert_called_once_with("openai")


# ---------------------------------------------------------------------------
# 6. Plugin Delegation Tests
# ---------------------------------------------------------------------------

def test_gui_application_plugin_management(mock_window):
    """Verify plugin listing and enable/disable operations."""
    mock_plugin = Mock()
    mock_plugin.id = "my_tool"
    mock_plugin.name = "My Tool Plugin"
    mock_plugin.version = "1.0.0"
    mock_plugin.description = "Extends scholaros tools"

    state_mock = Mock()
    state_mock.name = "STARTED"

    mock_pm = Mock()
    mock_pm.plugins = {"my_tool": mock_plugin}
    mock_pm.state = Mock(return_value=state_mock)

    app = GUIApplication(mock_window, plugin_manager=mock_pm)
    plugins = app.list_plugins()

    assert len(plugins) == 1
    assert plugins[0]["id"] == "my_tool"
    assert plugins[0]["state"] == "STARTED"

    app.enable_plugin("my_tool")
    mock_pm.enable.assert_called_once_with("my_tool")

    app.disable_plugin("my_tool")
    mock_pm.disable.assert_called_once_with("my_tool")


# ---------------------------------------------------------------------------
# 7. Main Window Navigation & View Switching
# ---------------------------------------------------------------------------

def test_gui_window_navigation_and_status(test_root):
    """Verify window navigation methods route to expected views."""
    theme = GUITheme()
    window = GUIWindow(root=test_root, theme=theme)

    # Test status bar helpers
    window.set_status("Loading models...")
    assert window.get_status() == "Loading models..."

    window.set_status("System ready")
    assert window.get_status() == "System ready"

    # Test show_view routing
    window.show_view("chat")
    window.show_view("research")
    window.show_view("library")
    window.show_view("plugins")
    window.show_view("settings")
    window.show_view("home")


# ---------------------------------------------------------------------------
# 8. Workspace Views Presentation & Callbacks
# ---------------------------------------------------------------------------

def test_chat_view_send_message_delegation(test_root):
    """Verify ChatView delegates message sending to application.chat()."""
    mock_app = Mock()
    mock_app.chat = Mock(return_value="Answer from chat agent")

    view = ChatView(parent=test_root, application=mock_app)
    response = view.send_message("What is entropy?")

    assert response == "Answer from chat agent"
    mock_app.chat.assert_called_once_with("What is entropy?")


def test_research_view_run_delegation(test_root):
    """Verify ResearchView delegates to application.research()."""
    mock_app = Mock()
    mock_app.research = Mock(return_value="Research paper summary")

    view = ResearchView(parent=test_root, application=mock_app)
    result = view.run_research("Renewable energy grid integration")

    assert result == "Research paper summary"
    mock_app.research.assert_called_once_with("Renewable energy grid integration")


def test_library_view_search_delegation(test_root):
    """Verify LibraryView delegates to application.search_knowledge()."""
    mock_app = Mock()
    mock_app.search_knowledge = Mock(return_value=[
        {"content": "Extracted text chunk", "score": 0.88, "source": "thesis.pdf"}
    ])

    view = LibraryView(parent=test_root, application=mock_app)
    results = view.search("thesis")

    assert len(results) == 1
    assert results[0]["source"] == "thesis.pdf"
    mock_app.search_knowledge.assert_called_once_with("thesis")


def test_settings_view_apply_provider(test_root):
    """Verify SettingsView apply_provider calls application.set_provider()."""
    mock_app = Mock()
    mock_app.info = Mock(return_value={"status": "READY", "ai": True, "rag": True})

    view = SettingsView(parent=test_root, application=mock_app)
    view._provider_combo.set("openai")
    view.apply_provider()

    mock_app.set_provider.assert_called_once_with("openai")


# ---------------------------------------------------------------------------
# 9. GUIBuilder & Convenience Factories
# ---------------------------------------------------------------------------

def test_gui_builder_with_services(test_root):
    """Verify GUIBuilder constructs and wires full integration with services."""
    mock_ai = Mock()
    mock_rp = Mock()
    mock_services = Mock(ai_manager=mock_ai, research_pipeline=mock_rp)

    builder = GUIBuilder()
    integration = builder.build(services=mock_services, root=test_root)

    assert integration.application.ai_manager is mock_ai
    assert integration.application.research_pipeline is mock_rp
    assert integration.window is not None
    assert integration.application.window is integration.window


def test_create_application_factory(mock_window):
    """Verify create_application factory helper."""
    app = create_application(window=mock_window)
    assert isinstance(app, GUIApplication)
    assert app.window is mock_window
