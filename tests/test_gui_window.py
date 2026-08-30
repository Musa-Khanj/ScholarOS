"""
Tests for scholaros.gui.window
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import Mock, patch

import pytest  # type: ignore[import-not-found]

from scholaros.gui.constants import (
    APPLICATION_TITLE,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MINIMUM_WINDOW_HEIGHT,
    MINIMUM_WINDOW_WIDTH,
)
from scholaros.gui.theme import GUITheme
from scholaros.gui.window import GUIWindow

DEFAULT_WINDOW_SIZE = f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}"


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def root():
    root = Mock(spec=tk.Tk)
    root.title = Mock()
    root.geometry = Mock()
    root.minsize = Mock()
    root.mainloop = Mock()
    return root


@pytest.fixture
def theme():
    return GUITheme()


@pytest.fixture
def window(root, theme):
    return GUIWindow(root=root, theme=theme)


# ==========================================================
# Helper Functions
# ==========================================================


def create_root():
    """Create a root window for testing."""
    root = tk.Tk()
    root.withdraw()
    return root


def create_theme():
    """Create a theme for testing."""
    return Mock(spec=GUITheme)


def create_window():
    """Create a window for testing."""
    root = Mock(spec=tk.Tk)
    root.title = Mock()
    root.geometry = Mock()
    root.minsize = Mock()
    root.mainloop = Mock()
    theme = Mock(spec=GUITheme)
    theme.apply = Mock()
    return GUIWindow(root=root, theme=theme)


# ==========================================================
# Construction
# ==========================================================


def test_window_creation(window):
    assert isinstance(window, GUIWindow)


def test_root_property(window, root):
    assert window.root is root


def test_theme_property(window, theme):
    assert window.theme is theme


def test_root_identity_preserved(window, root):
    assert id(window.root) == id(root)


# ==========================================================
# Initial State
# ==========================================================


def test_header_initially_none(window):
    assert window.header is None


def test_body_initially_none(window):
    assert window.body is None


def test_sidebar_initially_none(window):
    assert window.sidebar is None


def test_workspace_initially_none(window):
    assert window.workspace is None


def test_toolbar_initially_none(window):
    assert window.toolbar is None


def test_statusbar_initially_none(window):
    assert window.statusbar is None


def test_status_bar_alias(window):
    assert window.status_bar is window.statusbar


def test_welcome_view_initially_none(window):
    assert window.welcome_view is None


def test_chat_panel_initially_none(window):
    assert window.chat_panel is None


# ==========================================================
# Window Configuration
# ==========================================================


def test_configure_window(window):
    window._configure_window()

    window.root.title.assert_called_once_with(
        APPLICATION_TITLE,
    )

    window.root.geometry.assert_called_once_with(
        DEFAULT_WINDOW_SIZE,
    )

    window.root.minsize.assert_called_once_with(
        MINIMUM_WINDOW_WIDTH,
        MINIMUM_WINDOW_HEIGHT,
    )

# ==========================================================
# Build
# ==========================================================

@patch("scholaros.gui.window.ChatPanel")
@patch("scholaros.gui.window.WelcomeView")
def test_build_applies_theme(mock_welcome, mock_chat):
    window = create_window()

    window = create_window()

    window._configure_window = Mock()
    window._build_header = Mock()
    window._build_body = Mock()
    window._build_sidebar = Mock()
    window._build_workspace = Mock()
    window._build_toolbar = Mock()
    window._build_statusbar = Mock()
    window._create_views = Mock()

    window.build()

    window.theme.apply.assert_called_once_with(window.root)


@patch("scholaros.gui.window.ChatPanel")
@patch("scholaros.gui.window.WelcomeView")
def test_build_sets_window_configuration(mock_welcome, mock_chat):
    window = create_window()

    window._configure_window = Mock()
    window._build_header = Mock()
    window._build_body = Mock()
    window._build_sidebar = Mock()
    window._build_workspace = Mock()
    window._build_toolbar = Mock()  
    window._build_statusbar = Mock()
    window._create_views = Mock()

    window.build()

    window.theme.apply.assert_called_once_with(window.root)
    window._configure_window.assert_called_once()

    window._configure_window.assert_called_once()

@patch("scholaros.gui.window.ChatPanel")
@patch("scholaros.gui.window.WelcomeView")
@patch("scholaros.gui.window.ttk.Label")
@patch("scholaros.gui.window.ttk.Button")
@patch("scholaros.gui.window.ttk.Frame")
def test_build_creates_shell(
    mock_frame,
    mock_button,
    mock_label,
    mock_welcome,
    mock_chat,
):
    frame = Mock()
    frame.pack = Mock()
    frame.grid = Mock()
    frame.grid_rowconfigure = Mock()
    frame.grid_columnconfigure = Mock()

    mock_frame.return_value = frame

    label = Mock()
    label.pack = Mock()
    mock_label.return_value = label

    button = Mock()
    button.pack = Mock()
    mock_button.return_value = button

    welcome = Mock()
    welcome.frame = Mock()
    welcome.frame.grid = Mock()
    welcome.show = Mock()

    chat = Mock()
    chat.frame = Mock()
    chat.frame.grid = Mock()
    chat.show = Mock()

    mock_welcome.return_value = welcome
    mock_chat.return_value = chat

    window = create_window()

    window.build()

    assert window.header is not None
    assert window.body is not None
    assert window.sidebar is not None
    assert window.workspace is not None
    assert window.toolbar is not None
    assert window.statusbar is not None
    assert window.welcome_view is welcome
    assert window.chat_panel is chat


@patch("scholaros.gui.window.ChatPanel")
@patch("scholaros.gui.window.WelcomeView")
@patch("scholaros.gui.window.ttk.Label")
@patch("scholaros.gui.window.ttk.Button")
@patch("scholaros.gui.window.ttk.Frame")
def test_build_only_runs_once(
    mock_frame,
    mock_button,
    mock_label,
    mock_welcome,
    mock_chat,
):
    frame = Mock()
    frame.pack = Mock()
    frame.grid = Mock()
    frame.grid_rowconfigure = Mock()
    frame.grid_columnconfigure = Mock()
    mock_frame.return_value = frame

    label = Mock()
    label.pack = Mock()
    mock_label.return_value = label

    button = Mock()
    button.pack = Mock()
    mock_button.return_value = button

    welcome = Mock()
    welcome.frame = Mock()
    welcome.frame.grid = Mock()
    welcome.show = Mock()

    chat = Mock()
    chat.frame = Mock()
    chat.frame.grid = Mock()
    chat.show = Mock()

    mock_welcome.return_value = welcome
    mock_chat.return_value = chat

    window = create_window()

    window.build()
    window.build()

    window.theme.apply.assert_called_once()
    assert mock_welcome.call_count == 1
    assert mock_chat.call_count == 1


# ==========================================================
# Show Methods
# ==========================================================

def test_show_welcome_calls_view():
    window = create_window()

    view = Mock()
    view.show = Mock()

    window._welcome_view = view

    window.show_welcome()

    view.show.assert_called_once()


def test_show_chat_calls_view():
    window = create_window()

    panel = Mock()
    panel.show = Mock()

    window._chat_panel = panel

    window.show_chat()

    panel.show.assert_called_once()


def test_show_welcome_without_view():
    window = create_window()

    window.show_welcome()


def test_show_chat_without_view():
    window = create_window()

    window.show_chat()


def test_show_runs_mainloop():
    window = create_window()

    window.show()

    window.root.mainloop.assert_called_once()


def test_show_preserves_root():
    window = create_window()
    root = window.root
    window.show()
    assert window.root is root

    window = GUIWindow(
        root=root,
        theme=create_theme(),
    )

    window.show()

    assert window.root is root

# =====================================================
# Part 3
# repr()
# =====================================================

def test_repr():
    """
    repr() contains the class name.
    """

    window = create_window()

    text = repr(window)

    assert "GUIWindow" in text
    assert "theme=" in text
    assert "welcome_view=None" in text
    assert "chat_panel=None" in text


@patch("scholaros.gui.window.ttk.Label")
@patch("scholaros.gui.window.ttk.Button")
@patch("scholaros.gui.window.ttk.Frame")
@patch("scholaros.gui.window.ChatPanel")
@patch("scholaros.gui.window.WelcomeView")
def test_repr_after_build(
    mock_welcome,
    mock_chat,
    mock_frame,
    mock_button,
    mock_label,
):
    """
    repr() remains valid after build().
    """

    frame = Mock()
    frame.pack = Mock()
    frame.grid = Mock()
    frame.grid_rowconfigure = Mock()
    frame.grid_columnconfigure = Mock()

    mock_frame.return_value = frame

    label = Mock()
    label.pack = Mock()
    mock_label.return_value = label

    button = Mock()
    button.pack = Mock()
    mock_button.return_value = button

    welcome = Mock()
    welcome.frame = Mock()
    welcome.frame.grid = Mock()

    chat = Mock()
    chat.frame = Mock()
    chat.frame.grid = Mock()

    mock_welcome.return_value = welcome
    mock_chat.return_value = chat

    window = create_window()

    window.build()

    text = repr(window)

    assert "GUIWindow" in text
    assert "theme=" in text
    assert "welcome_view=" in text
    assert "chat_panel=" in text