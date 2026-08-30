"""
ScholarOS
GUI Views

Version : 1.0
Status  : In Development
Python  : 3.14+

Provides reusable workspace views.

Views are purely visual.

No application logic belongs here.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from scholaros.gui.chat import GUIChat


class GUIView:
    """
    Base workspace view.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        description: str,
    ) -> None:

        self._frame = ttk.Frame(
            parent,
            padding=30,
        )

        ttk.Label(
            self._frame,
            text=title,
            font=(
                "TkDefaultFont",
                22,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            self._frame,
            text=description,
            justify="left",
        ).pack(
            anchor="w",
        )

    @property
    def frame(
        self,
    ) -> ttk.Frame:
        return self._frame


class HomeView(GUIView):

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        super().__init__(
            parent,
            "Home",
            "Welcome to ScholarOS.",
        )


class ChatView:

    def __init__(
        self,
        parent,
    ):

        self._chat = GUIChat(parent)

        self._chat.build()

    @property
    def frame(self):

        return self._chat.frame

    @property
    def chat(self):

        return self._chat


class ResearchView(GUIView):

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        super().__init__(
            parent,
            "Research",
            "Research workspace.",
        )


class LibraryView(GUIView):

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        super().__init__(
            parent,
            "Library",
            "Document library.",
        )


class PluginsView(GUIView):

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        super().__init__(
            parent,
            "Plugins",
            "Installed plugins.",
        )


class SettingsView(GUIView):

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        super().__init__(
            parent,
            "Settings",
            "Application settings.",
        )