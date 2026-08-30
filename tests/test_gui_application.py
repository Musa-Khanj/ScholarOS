"""
Tests for scholaros.gui.application
"""

from __future__ import annotations

from unittest.mock import Mock

from scholaros.gui.application import GUIApplication
from scholaros.gui.window import GUIWindow

#
# ============================================================
# Fixtures
# ============================================================
#


def create_application() -> GUIApplication:
    """
    Create a GUIApplication.
    """

    window = Mock(spec=GUIWindow)

    return GUIApplication(window)


#
# ============================================================
# Construction
# ============================================================
#


def test_application_creation():

    application = create_application()

    assert isinstance(
        application,
        GUIApplication,
    )


def test_application_window_property():

    application = create_application()

    assert isinstance(
        application.window,
        Mock,
    )


def test_window_identity_preserved():

    application = create_application()

    window = application.window

    assert application.window is window


#
# ============================================================
# Build
# ============================================================
#


def test_build_delegates_to_window():

    application = create_application()

    application.build()

    application.window.build.assert_called_once()


#
# ============================================================
# Run
# ============================================================
#


def test_run_delegates_to_window():

    application = create_application()

    application.run()

    application.window.show.assert_called_once()


def test_run_preserves_window():

    application = create_application()

    window = application.window

    application.run()

    assert application.window is window


#
# ============================================================
# Representation
# ============================================================
#


def test_application_repr():

    application = create_application()

    representation = repr(application)

    assert representation.startswith(
        "GUIApplication("
    )


def test_application_repr_contains_window():

    application = create_application()

    representation = repr(application)

    assert "window=" in representation


def test_repr_after_build():

    application = create_application()

    application.build()

    assert repr(application).startswith(
        "GUIApplication("
    )


#
# ============================================================
# Stability
# ============================================================
#


def test_multiple_build_calls():

    application = create_application()

    application.build()
    application.build()

    assert application.window.build.call_count == 2


def test_multiple_run_calls():

    application = create_application()

    application.run()
    application.run()

    assert application.window.show.call_count == 2