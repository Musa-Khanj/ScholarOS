"""
ScholarOS
GUI Home View

Version : 1.0
Status  : In Development
Python  : 3.14+

## Description

Provides the default Home page shown inside
the ScholarOS workspace.

The Home view is responsible only for
displaying its own interface.

It does not perform AI, research,
RAG, plugins, or application logic.
"""

from __future__ import annotations

from tkinter import ttk

from scholaros.gui.views import (
    GUIView,
)


class GUIHomeView(GUIView):
    """
    Default ScholarOS workspace view.
    """

    def __init__(
        self,
        parent: ttk.Frame,
    ) -> None:
        """
        Initialize the Home view.
        """

        super().__init__(
            parent=parent,
            name="home",
        )

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def build(
        self,
    ) -> None:
        """
        Build the Home interface.
        """

        if self.built:
            return

        title = ttk.Label(
            self.frame,
            text="ScholarOS",
            font=(
                "TkDefaultFont",
                22,
                "bold",
            ),
        )

        title.pack(
            pady=(40, 10),
        )

        subtitle = ttk.Label(
            self.frame,
            text=(
                "AI Research Operating System"
            ),
        )

        subtitle.pack()

        description = ttk.Label(
            self.frame,
            justify="center",
            text=(
                "Welcome to ScholarOS.\n\n"
                "Use the navigation panel to begin "
                "working with research, chat, "
                "knowledge management, plugins, "
                "and future AI capabilities."
            ),
        )

        description.pack(
            pady=30,
        )

        self._built = True

    # ---------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Refresh the Home view.

        Currently no dynamic state exists.
        """

        return None