"""
Tests for Part 2 — GUIApplication <-> GUIWindow Context Injection.
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock

from scholaros.ai.manager import AIManager
from scholaros.config.manager import ConfigManager
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.gui.application import GUIApplication
from scholaros.gui.window import GUIWindow
from scholaros.gui.workspace import GUIWorkspace
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.plugins.manager import PluginManager
from scholaros.research.pipeline import ResearchPipeline

# Shared Tk root fixture helper
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


def test_application_injects_itself_into_window():
    """Verify GUIApplication.__init__ sets window.application to itself."""
    window = GUIWindow(get_test_root())
    assert window.application is None

    app = GUIApplication(window)
    assert window.application is app


def test_window_propagates_application_to_lazily_created_views():
    """Verify window passes application when creating workspace views."""
    root = get_test_root()
    window = GUIWindow(root)
    window.build()
    app = GUIApplication(window)

    # Show Research
    window.show_research()
    assert window.research_view is not None
    assert window.research_view.application is app

    # Show Library
    window.show_library()
    assert window.library_view is not None
    assert window.library_view.application is app

    # Show Plugins
    window.show_plugins()
    assert window.plugins_view is not None
    assert window.plugins_view.application is app

    # Show Settings
    window.show_settings()
    assert window.settings_view is not None
    assert window.settings_view.application is app


def test_window_set_application_propagates_to_existing_views():
    """Verify calling set_application on window updates already instantiated views."""
    root = get_test_root()
    window = GUIWindow(root)
    window.build()
    window.show_settings()

    mock_view = window.settings_view
    assert mock_view is not None

    mock_app = Mock(spec=GUIApplication)
    window.set_application(mock_app)

    assert window.application is mock_app
    assert mock_view.application is mock_app


def test_application_resolves_missing_dependencies_from_container():
    """Verify GUIApplication inspects container for unprovided dependencies."""
    window = Mock(spec=GUIWindow)
    window.set_application = Mock()

    container = Container()
    mock_ai = Mock(spec=AIManager)
    mock_km = Mock(spec=KnowledgeManager)
    mock_res = Mock(spec=ResearchPipeline)
    mock_rag = Mock(spec=RAGPipeline)
    mock_pm = Mock(spec=PluginManager)
    mock_cfg = Mock(spec=ConfigManager)
    mock_eb = Mock(spec=EventBus)

    container.add_instance(AIManager, mock_ai)
    container.add_instance(KnowledgeManager, mock_km)
    container.add_instance(ResearchPipeline, mock_res)
    container.add_instance(RAGPipeline, mock_rag)
    container.add_instance(PluginManager, mock_pm)
    container.add_instance(ConfigManager, mock_cfg)
    container.add_instance(EventBus, mock_eb)

    app = GUIApplication(window, container=container)

    assert app.ai_manager is mock_ai
    assert app.knowledge_manager is mock_km
    assert app.research_pipeline is mock_res
    assert app.rag_pipeline is mock_rag
    assert app.plugin_manager is mock_pm
    assert app.config_manager is mock_cfg
    assert app.event_bus is mock_eb
    window.set_application.assert_called_once_with(app)


def test_gui_workspace_injects_application_to_views():
    """Verify GUIWorkspace accepts and propagates application to created views."""
    root = get_test_root()
    mock_app = Mock(spec=GUIApplication)
    mock_app.info.return_value = {"status": "READY"}
    mock_app.list_plugins.return_value = []

    frame = tk.Frame(root)
    workspace = GUIWorkspace(frame, application=mock_app)
    workspace.show("Settings")

    view = workspace.active
    assert view is not None
    assert getattr(view, "application", None) is mock_app
