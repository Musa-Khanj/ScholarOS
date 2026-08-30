"""
ScholarOS
GUI Launcher

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from scholaros.gui.builder import (
    GUIBuilder,
)


class GUILauncher:
    """
    Launches the ScholarOS GUI.
    """

    def __init__(
        self,
        builder: GUIBuilder | None = None,
    ) -> None:

        self._builder = (
            builder
            if builder is not None
            else GUIBuilder()
        )

    @property
    def builder(
        self,
    ) -> GUIBuilder:
        """
        Return the configured builder.
        """

        return self._builder

    def launch(
        self,
    ) -> None:
        """
        Build and launch the GUI.
        """

        integration = self.builder.build()

        integration.run()

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"builder={self.builder!r}"
            f")"
        )


def launch_gui() -> None:
    """
    Convenience launcher for the GUI.
    """

    GUILauncher().launch()