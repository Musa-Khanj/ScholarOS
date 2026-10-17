"""
Tests for Part 3 — Activating production workspace views (HomeView, ChatView) in GUIWindow.

Validates:
- GUIWindow preserves legacy _welcome_view and _chat_panel
- GUIWindow instantiates and mounts active _home_view and _chat_view
- HomeView and ChatView properties are exposed on GUIWindow
- Navigation to "home" and "chat" displays active views
- show_welcome() continues to display legacy WelcomeView for backward compatibility
- Context injection propagates application reference to HomeView and ChatView
- HomeView quick-action callbacks navigate correctly via show_view
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from scholaros.gui.theme import GUITheme
from scholaros.gui.views.workspace_views import ChatView, HomeView
from scholaros.gui.window import GUIWindow


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


def test_initial_state_includes_home_and_chat_views(test_root):
    """Verify home_view and chat_view are initially None before build."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    assert window.welcome_view is None
    assert window.chat_panel is None
    assert window.home_view is None
    assert window.chat_view is None


def test_build_instantiates_both_legacy_and_production_views(test_root):
    """Verify build creates both legacy and active production views."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    # Legacy views preserved
    assert window.welcome_view is not None
    assert window.chat_panel is not None

    # Production views active
    assert window.home_view is not None
    assert isinstance(window.home_view, HomeView)
    assert window.chat_view is not None
    assert isinstance(window.chat_view, ChatView)


def test_show_home_activates_home_view(test_root):
    """Verify show_home raises home_view frame."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    with patch.object(window.home_view, "show", wraps=window.home_view.show) as mock_show:
        window.show_home()
        mock_show.assert_called_once()


def test_show_chat_activates_chat_view(test_root):
    """Verify show_chat raises chat_view frame, not legacy chat_panel."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    with (
        patch.object(window.chat_view, "show", wraps=window.chat_view.show) as mock_chat_view_show,
        patch.object(window.chat_panel, "show", wraps=window.chat_panel.show) as mock_panel_show,
    ):
        window.show_chat()
        mock_chat_view_show.assert_called_once()
        mock_panel_show.assert_not_called()


def test_show_welcome_preserves_legacy_welcome_view(test_root):
    """Verify show_welcome still raises legacy welcome_view."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    with patch.object(
        window.welcome_view, "show", wraps=window.welcome_view.show
    ) as mock_welcome_show:
        window.show_welcome()
        mock_welcome_show.assert_called_once()


def test_set_application_propagates_to_home_and_chat_views(test_root):
    """Verify set_application injects application into home_view and chat_view."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    mock_app = Mock()
    mock_app.info.return_value = {"status": "READY", "ai": True, "rag": True}

    window.set_application(mock_app)

    assert window.home_view.application is mock_app
    assert window.chat_view.application is mock_app


def test_home_view_navigation_callback(test_root):
    """Verify HomeView quick action buttons navigate via show_view."""
    window = GUIWindow(root=test_root, theme=GUITheme())
    window.build()

    with patch.object(window, "show_chat") as mock_show_chat:
        window.home_view._navigate("chat")
        mock_show_chat.assert_called_once()
