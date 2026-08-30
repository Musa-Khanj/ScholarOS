"""
ScholarOS
GUI Builder

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Constructs the complete GUI object graph.
"""

from __future__ import annotations

from scholaros.gui.application import GUIApplication
from scholaros.gui.integration import GUIIntegration
from scholaros.gui.window import GUIWindow


class GUIBuilder:
    """
    Constructs the complete GUI object graph.
    """

    def build(self) -> GUIIntegration:
        """
        Build the GUI integration.
        """

        window = GUIWindow()

        application = GUIApplication(
            window,
        )

        integration = GUIIntegration(
            application,
        )

        integration.build()

        return integration

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return "GUIBuilder()"


def create_gui() -> GUIIntegration:
    """
    Convenience factory for creating
    the complete GUI integration.
    """

    return GUIBuilder().build()