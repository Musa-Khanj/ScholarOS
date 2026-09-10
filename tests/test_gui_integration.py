"""
Tests for scholaros.gui.integration
"""

from __future__ import annotations

import tkinter as tk

from scholaros.gui.application import GUIApplication
from scholaros.gui.integration import GUIIntegration
from scholaros.gui.window import GUIWindow

#
# ============================================================
# Fixtures
# ============================================================
#

_root: tk.Tk | None = None


def create_integration() -> GUIIntegration:
    """
    Create a GUIIntegration instance.
    """

    global _root

    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            _root = tk.Tk()
            _root.withdraw()
            
    # Clear any existing children from previous tests
    for child in list(_root.winfo_children()):
        try:
            child.destroy()
        except tk.TclError:
            pass

    window = GUIWindow(
        _root,
    )

    application = GUIApplication(
        window,
    )

    return GUIIntegration(
        application,
    )


def teardown_module(module):
    """
    Do not destroy the shared Tk root to prevent 
    Tcl interpreter corruption across multiple 
    test modules in the same pytest session.
    """
    pass


#
# ============================================================
# Construction
# ============================================================
#


def test_integration_creation():
    """
    GUIIntegration can be created.
    """

    integration = create_integration()

    assert isinstance(
        integration,
        GUIIntegration,
    )


def test_application_property():
    """
    application property returns GUIApplication.
    """

    integration = create_integration()

    assert isinstance(
        integration.application,
        GUIApplication,
    )


def test_window_property():
    """
    window property returns GUIWindow.
    """

    integration = create_integration()

    assert isinstance(
        integration.window,
        GUIWindow,
    )


def test_window_identity():
    """
    window property preserves identity.
    """

    integration = create_integration()

    assert (
        integration.window
        is integration.application.window
    )


#
# ============================================================
# Build
# ============================================================
#


def test_build_delegates_to_application():
    """
    build() delegates to GUIApplication.build().
    """

    integration = create_integration()

    called = {
        "value": False,
    }

    original = (
        integration.application.build
    )

    def fake_build():

        called["value"] = True

    try:

        integration.application.build = (
            fake_build
        )

        integration.build()

    finally:

        integration.application.build = (
            original
        )

    assert called["value"]


#
# ============================================================
# Run
# ============================================================
#


def test_run_delegates_to_application():
    """
    run() delegates to GUIApplication.run().
    """

    integration = create_integration()

    called = {
        "value": False,
    }

    original = (
        integration.application.run
    )

    def fake_run():

        called["value"] = True

    try:

        integration.application.run = (
            fake_run
        )

        integration.run()

    finally:

        integration.application.run = (
            original
        )

    assert called["value"]


#
# ============================================================
# Identity
# ============================================================
#


def test_application_identity():
    """
    application property preserves identity.
    """

    integration = create_integration()

    application = integration.application

    assert (
        integration.application
        is application
    )


def test_build_preserves_application():
    """
    build() never replaces application.
    """

    integration = create_integration()

    application = integration.application

    original = (
        integration.application.build
    )

    try:

        integration.application.build = (
            lambda: None
        )

        integration.build()

    finally:

        integration.application.build = (
            original
        )

    assert (
        integration.application
        is application
    )


def test_run_preserves_application():
    """
    run() never replaces application.
    """

    integration = create_integration()

    application = integration.application

    original = (
        integration.application.run
    )

    try:

        integration.application.run = (
            lambda: None
        )

        integration.run()

    finally:

        integration.application.run = (
            original
        )

    assert (
        integration.application
        is application
    )


#
# ============================================================
# Representation
# ============================================================
#


def test_repr():
    """
    repr() is developer friendly.
    """

    integration = create_integration()

    representation = repr(
        integration,
    )

    assert (
        representation.startswith(
            "GUIIntegration("
        )
    )

    assert (
        "application="
        in representation
    )


def test_repr_after_build():
    """
    repr() remains valid after build().
    """

    integration = create_integration()

    original = (
        integration.application.build
    )

    try:

        integration.application.build = (
            lambda: None
        )

        integration.build()

    finally:

        integration.application.build = (
            original
        )

    assert (
        repr(
            integration,
        ).startswith(
            "GUIIntegration("
        )
    )