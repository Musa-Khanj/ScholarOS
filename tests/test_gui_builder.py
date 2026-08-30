"""
Tests for scholaros.gui.builder
"""

from __future__ import annotations

from scholaros.gui.application import GUIApplication
from scholaros.gui.builder import (
    GUIBuilder,
    create_gui,
)
from scholaros.gui.integration import GUIIntegration
from scholaros.gui.window import GUIWindow

#
# ============================================================
# Construction
# ============================================================
#


def test_builder_creation():
    """
    GUIBuilder can be created.
    """

    builder = GUIBuilder()

    assert isinstance(
        builder,
        GUIBuilder,
    )


#
# ============================================================
# Build
# ============================================================
#


def test_build_returns_integration():
    """
    build() returns GUIIntegration.
    """

    builder = GUIBuilder()

    integration = builder.build()

    assert isinstance(
        integration,
        GUIIntegration,
    )


def test_build_creates_application():
    """
    build() creates GUIApplication.
    """

    builder = GUIBuilder()

    integration = builder.build()

    assert isinstance(
        integration.application,
        GUIApplication,
    )


def test_build_creates_window():
    """
    build() creates GUIWindow.
    """

    builder = GUIBuilder()

    integration = builder.build()

    assert isinstance(
        integration.application.window,
        GUIWindow,
    )


def test_build_returns_new_instance():
    """
    Every build returns a new integration.
    """

    builder = GUIBuilder()

    first = builder.build()

    second = builder.build()

    assert first is not second


def test_build_returns_new_application():
    """
    Every build returns
    a new application.
    """

    builder = GUIBuilder()

    first = builder.build()

    second = builder.build()

    assert (
        first.application
        is not second.application
    )


def test_build_returns_new_window():
    """
    Every build returns
    a new window.
    """

    builder = GUIBuilder()

    first = builder.build()

    second = builder.build()

    assert (
        first.application.window
        is not second.application.window
    )


#
# ============================================================
# Integration Build
# ============================================================
#


def test_build_calls_integration_build():
    """
    GUIBuilder delegates to
    GUIIntegration.build().
    """

    builder = GUIBuilder()

    original = GUIIntegration.build

    called = {
        "value": False,
    }

    def fake_build(
        self,
    ):

        called["value"] = True

    try:

        GUIIntegration.build = (
            fake_build
        )

        builder.build()

    finally:

        GUIIntegration.build = (
            original
        )

    assert called["value"]


#
# ============================================================
# Factory
# ============================================================
#


def test_create_gui_returns_integration():
    """
    create_gui() returns
    GUIIntegration.
    """

    integration = create_gui()

    assert isinstance(
        integration,
        GUIIntegration,
    )


def test_create_gui_creates_application():
    """
    Factory creates application.
    """

    integration = create_gui()

    assert isinstance(
        integration.application,
        GUIApplication,
    )


def test_create_gui_creates_window():
    """
    Factory creates window.
    """

    integration = create_gui()

    assert isinstance(
        integration.application.window,
        GUIWindow,
    )


#
# ============================================================
# Representation
# ============================================================
#


def test_builder_repr():
    """
    repr() is valid.
    """

    builder = GUIBuilder()

    representation = repr(
        builder,
    )

    assert (
        representation.startswith(
            "GUIBuilder"
        )
    )