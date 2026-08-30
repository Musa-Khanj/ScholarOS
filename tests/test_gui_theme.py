"""
ScholarOS
GUI Theme Tests

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import Mock, patch

import pytest

from scholaros.gui.theme import (
    DEFAULT_THEME,
    GUITheme,
)

# ==========================================================
# Construction
# ==========================================================


def test_theme_creation():
    """
    GUITheme can be created.
    """

    theme = GUITheme()

    assert isinstance(
        theme,
        GUITheme,
    )


def test_default_theme_instance():
    """
    DEFAULT_THEME is a GUITheme.
    """

    assert isinstance(
        DEFAULT_THEME,
        GUITheme,
    )


# ==========================================================
# Colors
# ==========================================================


def test_background_color():
    """
    Background color is correct.
    """

    assert (
        DEFAULT_THEME.background
        == "#1E1E1E"
    )


def test_surface_color():
    """
    Surface color is correct.
    """

    assert (
        DEFAULT_THEME.surface
        == "#252526"
    )


def test_primary_color():
    """
    Primary color is correct.
    """

    assert (
        DEFAULT_THEME.primary
        == "#007ACC"
    )


def test_secondary_color():
    """
    Secondary color is correct.
    """

    assert (
        DEFAULT_THEME.secondary
        == "#3A96DD"
    )


def test_accent_color():
    """
    Accent color is correct.
    """

    assert (
        DEFAULT_THEME.accent
        == "#00BCF2"
    )


def test_text_color():
    """
    Text color is correct.
    """

    assert (
        DEFAULT_THEME.text
        == "#FFFFFF"
    )


def test_secondary_text_color():
    """
    Secondary text color is correct.
    """

    assert (
        DEFAULT_THEME.text_secondary
        == "#C8C8C8"
    )


def test_border_color():
    """
    Border color is correct.
    """

    assert (
        DEFAULT_THEME.border
        == "#3C3C3C"
    )


def test_success_color():
    """
    Success color is correct.
    """

    assert (
        DEFAULT_THEME.success
        == "#16A34A"
    )


def test_warning_color():
    """
    Warning color is correct.
    """

    assert (
        DEFAULT_THEME.warning
        == "#F59E0B"
    )


def test_error_color():
    """
    Error color is correct.
    """

    assert (
        DEFAULT_THEME.error
        == "#DC2626"
    )


# ==========================================================
# Typography
# ==========================================================


def test_font_family_exists():
    """
    Font family is defined.
    """

    assert (
        DEFAULT_THEME.font_family
        != ""
    )


def test_font_size_positive():
    """
    Font size is positive.
    """

    assert (
        DEFAULT_THEME.font_size
        > 0
    )


def test_title_font_size():
    """
    Title font is larger than body.
    """

    assert (
        DEFAULT_THEME.title_font_size
        > DEFAULT_THEME.font_size
    )


def test_heading_font_size():
    """
    Heading font is larger than body.
    """

    assert (
        DEFAULT_THEME.heading_font_size
        > DEFAULT_THEME.font_size
    )


def test_small_font_size():
    """
    Small font is smaller than body.
    """

    assert (
        DEFAULT_THEME.small_font_size
        < DEFAULT_THEME.font_size
    )


# ==========================================================
# Layout
# ==========================================================


def test_window_width():
    """
    Window width is positive.
    """

    assert (
        DEFAULT_THEME.window_width
        > 0
    )


def test_window_height():
    """
    Window height is positive.
    """

    assert (
        DEFAULT_THEME.window_height
        > 0
    )


def test_sidebar_width():
    """
    Sidebar width is positive.
    """

    assert (
        DEFAULT_THEME.sidebar_width
        > 0
    )


def test_header_height():
    """
    Header height is positive.
    """

    assert (
        DEFAULT_THEME.header_height
        > 0
    )


def test_toolbar_height():
    """
    Toolbar height is positive.
    """

    assert (
        DEFAULT_THEME.toolbar_height
        > 0
    )


def test_status_bar_height():
    """
    Status bar height is positive.
    """

    assert (
        DEFAULT_THEME.status_bar_height
        > 0
    )


def test_padding_order():
    """
    Padding sizes increase.
    """

    assert (
        DEFAULT_THEME.padding_small
        < DEFAULT_THEME.padding
        < DEFAULT_THEME.padding_large
    )


def test_spacing_order():
    """
    Spacing sizes increase.
    """

    assert (
        DEFAULT_THEME.spacing_small
        < DEFAULT_THEME.spacing
        < DEFAULT_THEME.spacing_large
    )


# ==========================================================
# Immutability
# ==========================================================


def test_theme_is_immutable():
    """
    GUITheme is immutable.
    """

    with pytest.raises(
        FrozenInstanceError,
    ):

        DEFAULT_THEME.background = (
            "#000000"
        )


# ==========================================================
# Representation
# ==========================================================


def test_theme_repr():
    """
    repr() is developer-friendly.
    """

    representation = repr(
        DEFAULT_THEME,
    )

    assert (
        representation.startswith(
            "GUITheme("
        )
    )


def test_theme_repr_contains_background():
    """
    repr() contains the background field.
    """

    assert (
        "background="
        in repr(
            DEFAULT_THEME,
        )
    )


@patch("tkinter.ttk.Style")
def test_apply_creates_style(
    mock_style,
):
    theme = GUITheme()

    root = Mock()

    theme.apply(root)

    mock_style.assert_called_once_with(root)


@patch("tkinter.ttk.Style")
def test_apply_configures_root(
    mock_style,
):
    theme = GUITheme()

    root = Mock()

    theme.apply(root)

    root.configure.assert_called_once_with(
        background=theme.background,
    )


@patch("tkinter.ttk.Style")
def test_apply_sets_theme(
    mock_style,
):
    theme = GUITheme()

    root = Mock()

    style = mock_style.return_value

    theme.apply(root)

    style.theme_use.assert_called_once_with(
        "clam",
    )


@patch("tkinter.ttk.Style")
def test_apply_configures_styles(
    mock_style,
):
    theme = GUITheme()

    root = Mock()

    style = mock_style.return_value

    theme.apply(root)

    assert style.configure.call_count >= 5