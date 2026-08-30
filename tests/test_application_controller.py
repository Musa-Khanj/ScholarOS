"""
ScholarOS
Tests for ApplicationController
"""

from __future__ import annotations

import tkinter as tk

from scholaros.applications.controller import (
    ApplicationController,
)
from scholaros.gui.window import (
    GUIWindow,
)


_root: tk.Tk | None = None


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def create_controller() -> ApplicationController:
    """
    Create an application controller.
    """

    global _root

    if _root is None:

        _root = tk.Tk()

        _root.withdraw()

    window = GUIWindow(
        root=_root,
    )

    return ApplicationController(
        window=window,
    )


# ---------------------------------------------------------
# Teardown
# ---------------------------------------------------------

def teardown_module(module):
    """
    Destroy the shared Tk root.
    """

    global _root

    if _root is not None:

        try:
            _root.destroy()

        except tk.TclError:
            pass

        _root = None


# ---------------------------------------------------------
# Construction
# ---------------------------------------------------------

def test_controller_window_property():
    """
    Verify window property.
    """

    controller = create_controller()

    assert isinstance(
        controller.window,
        GUIWindow,
    )


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------

def test_initialize_builds_window():
    """
    initialize() should build the GUI.
    """

    controller = create_controller()

    controller.initialize()

    assert controller.window.header is not None
    assert controller.window.body is not None
    assert controller.window.sidebar is not None
    assert controller.window.workspace is not None
    assert controller.window.status_bar is not None


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

def test_run_calls_mainloop():
    """
    run() should enter Tk mainloop.
    """

    controller = create_controller()

    called = {
        "value": False,
    }

    def fake_mainloop():

        called["value"] = True

    original = controller.window.root.mainloop

    try:

        controller.window.root.mainloop = (
            fake_mainloop
        )

        controller.run()

        assert called["value"]

    finally:

        controller.window.root.mainloop = (
            original
        )


# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------

def test_show_home():
    """
    Verify home navigation.
    """

    controller = create_controller()

    controller.initialize()

    controller.show_home()

    assert (
        controller.window.welcome_view
        is not None
    )


def test_show_chat():
    """
    Verify chat navigation.
    """

    controller = create_controller()

    controller.initialize()

    controller.show_chat()

    assert (
        controller.window.chat_panel
        is not None
    )


# ---------------------------------------------------------
# Placeholder Pages
# ---------------------------------------------------------

def test_show_research():
    """
    Placeholder should execute.
    """

    controller = create_controller()

    assert (
        controller.show_research()
        is None
    )


def test_show_library():
    """
    Placeholder should execute.
    """

    controller = create_controller()

    assert (
        controller.show_library()
        is None
    )


def test_show_plugins():
    """
    Placeholder should execute.
    """

    controller = create_controller()

    assert (
        controller.show_plugins()
        is None
    )


def test_show_settings():
    """
    Placeholder should execute.
    """

    controller = create_controller()

    assert (
        controller.show_settings()
        is None
    )


# ---------------------------------------------------------
# Events
# ---------------------------------------------------------

def test_chat_submit():
    """
    Placeholder chat handler.
    """

    controller = create_controller()

    assert (
        controller.on_chat_submit(
            "Hello",
        )
        is None
    )


def test_exit_requested():
    """
    Exit should destroy root.
    """

    controller = create_controller()

    called = {
        "value": False,
    }

    def fake_destroy():

        called["value"] = True

    original = controller.window.root.destroy

    try:

        controller.window.root.destroy = (
            fake_destroy
        )

        controller.on_exit_requested()

        assert called["value"]

    finally:

        controller.window.root.destroy = (
            original
        )


# ---------------------------------------------------------
# Representation
# ---------------------------------------------------------

def test_repr():
    """
    Verify repr().
    """

    controller = create_controller()

    representation = repr(
        controller,
    )

    assert representation.startswith(
        "ApplicationController("
    )

    assert "window=" in representation