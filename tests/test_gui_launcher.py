"""
ScholarOS
GUI Launcher Tests

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from scholaros.gui.builder import GUIBuilder
from scholaros.gui.launcher import (
    GUILauncher,
    launch_gui,
)

#
# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
#

def create_launcher() -> GUILauncher:
    """
    Create a launcher with a mocked builder.
    """

    builder = Mock(
        spec=GUIBuilder,
    )

    integration = Mock()

    builder.build.return_value = (
        integration
    )

    return GUILauncher(
        builder,
    )


#
# ---------------------------------------------------------
# Construction
# ---------------------------------------------------------
#

def test_launcher_builder_property():
    """
    Verify builder property.
    """

    builder = Mock(
        spec=GUIBuilder,
    )

    launcher = GUILauncher(
        builder,
    )

    assert (
        launcher.builder
        is builder
    )


#
# ---------------------------------------------------------
# Launch
# ---------------------------------------------------------
#

def test_launch_calls_builder():
    """
    launch() should call builder.build().
    """

    launcher = create_launcher()

    launcher.launch()

    launcher.builder.build.assert_called_once()


def test_launch_runs_integration():
    """
    launch() should run the built integration.
    """

    launcher = create_launcher()

    integration = (
        launcher.builder.build.return_value
    )

    launcher.launch()

    integration.run.assert_called_once()


#
# ---------------------------------------------------------
# Convenience API
# ---------------------------------------------------------
#

@patch(
    "scholaros.gui.launcher.GUILauncher",
)
def test_launch_gui_uses_launcher(
    mock_launcher,
):
    """
    launch_gui() should create
    a launcher and invoke launch().
    """

    launcher = Mock()

    mock_launcher.return_value = (
        launcher
    )

    launch_gui()

    mock_launcher.assert_called_once_with()

    launcher.launch.assert_called_once()


#
# ---------------------------------------------------------
# Representation
# ---------------------------------------------------------
#

def test_launcher_repr():
    """
    Verify repr().
    """

    launcher = create_launcher()

    representation = repr(
        launcher,
    )

    assert (
        representation.startswith(
            "GUILauncher("
        )
    )

    assert (
        "builder="
        in representation
    )