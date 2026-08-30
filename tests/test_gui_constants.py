"""
ScholarOS
GUI Constants Tests

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from scholaros.gui.constants import (
    APPLICATION_TITLE,
    APPLICATION_VERSION,
    CHAT_VIEW,
    DEFAULT_PADDING,
    DEFAULT_SPACING,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_WINDOW_WIDTH,
    HEADER_HEIGHT,
    HOME_VIEW,
    KNOWLEDGE_VIEW,
    MINIMUM_WINDOW_HEIGHT,
    MINIMUM_WINDOW_WIDTH,
    REPORTS_VIEW,
    RESEARCH_VIEW,
    SETTINGS_VIEW,
    SIDEBAR_WIDTH,
    STATUS_BAR_HEIGHT,
    TOOLBAR_HEIGHT,
)

# ==========================================================
# Application
# ==========================================================


def test_application_title():
    """
    Application title is correct.
    """

    assert (
        APPLICATION_TITLE
        == "ScholarOS"
    )


def test_application_version():
    """
    Application version is defined.
    """

    assert (
        APPLICATION_VERSION
        == "1.0"
    )


# ==========================================================
# Window
# ==========================================================


def test_default_window_width():
    """
    Default window width is correct.
    """

    assert (
        DEFAULT_WINDOW_WIDTH
        == 1280
    )


def test_default_window_height():
    """
    Default window height is correct.
    """

    assert (
        DEFAULT_WINDOW_HEIGHT
        == 800
    )


def test_default_window_size():
    """
    Window size string is generated correctly.
    """

    assert (
        DEFAULT_WINDOW_SIZE
        == (
            f"{DEFAULT_WINDOW_WIDTH}x"
            f"{DEFAULT_WINDOW_HEIGHT}"
        )
    )


def test_minimum_window_width():
    """
    Minimum width is correct.
    """

    assert (
        MINIMUM_WINDOW_WIDTH
        == 800
    )


def test_minimum_window_height():
    """
    Minimum height is correct.
    """

    assert (
        MINIMUM_WINDOW_HEIGHT
        == 600
    )


# ==========================================================
# Layout
# ==========================================================


def test_sidebar_width():
    """
    Sidebar width is correct.
    """

    assert (
        SIDEBAR_WIDTH
        == 240
    )


def test_header_height():
    """
    Header height is correct.
    """

    assert (
        HEADER_HEIGHT
        == 56
    )


def test_toolbar_height():
    """
    Toolbar height is correct.
    """

    assert (
        TOOLBAR_HEIGHT
        == 40
    )


def test_status_bar_height():
    """
    Status bar height is correct.
    """

    assert (
        STATUS_BAR_HEIGHT
        == 24
    )


def test_default_padding():
    """
    Default padding is correct.
    """

    assert (
        DEFAULT_PADDING
        == 12
    )


def test_default_spacing():
    """
    Default spacing is correct.
    """

    assert (
        DEFAULT_SPACING
        == 8
    )


# ==========================================================
# Navigation
# ==========================================================


def test_home_view():
    """
    Home view identifier is correct.
    """

    assert (
        HOME_VIEW
        == "home"
    )


def test_chat_view():
    """
    Chat view identifier is correct.
    """

    assert (
        CHAT_VIEW
        == "chat"
    )


def test_research_view():
    """
    Research view identifier is correct.
    """

    assert (
        RESEARCH_VIEW
        == "research"
    )


def test_knowledge_view():
    """
    Knowledge view identifier is correct.
    """

    assert (
        KNOWLEDGE_VIEW
        == "knowledge"
    )


def test_reports_view():
    """
    Reports view identifier is correct.
    """

    assert (
        REPORTS_VIEW
        == "reports"
    )


def test_settings_view():
    """
    Settings view identifier is correct.
    """

    assert (
        SETTINGS_VIEW
        == "settings"
    )