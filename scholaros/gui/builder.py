"""
ScholarOS GUI Builder.

Constructs the complete desktop shell object graph, wiring
Window -> Application -> Services -> Core.
"""

from __future__ import annotations

from typing import Any

from scholaros.gui.application import GUIApplication
from scholaros.gui.integration import GUIIntegration
from scholaros.gui.window import GUIWindow


class GUIBuilder:
    """
    Constructs the complete GUI object graph.
    """

    def build(
        self,
        services: Any | None = None,
        container: Any | None = None,
        window: GUIWindow | None = None,
        theme: Any | None = None,
        root: Any | None = None,
        **kwargs: Any,
    ) -> GUIIntegration:
        """
        Build the GUI integration.
        """
        win = window or GUIWindow(root=root, theme=theme)

        application = GUIApplication(
            window=win,
            services=services,
            container=container,
            **kwargs,
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


def create_gui(
    services: Any | None = None,
    container: Any | None = None,
    window: GUIWindow | None = None,
    **kwargs: Any,
) -> GUIIntegration:
    """
    Convenience factory for creating the complete GUI integration.
    """
    return GUIBuilder().build(
        services=services,
        container=container,
        window=window,
        **kwargs,
    )


def create_application(
    window: GUIWindow | None = None,
    services: Any | None = None,
    container: Any | None = None,
    **kwargs: Any,
) -> GUIApplication:
    """
    Convenience factory for creating a GUIApplication instance.
    """
    win = window or GUIWindow()
    return GUIApplication(
        window=win,
        services=services,
        container=container,
        **kwargs,
    )
