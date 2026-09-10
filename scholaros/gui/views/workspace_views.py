"""
ScholarOS
GUI Workspace Views

Version : 1.0
Status  : In Development
Python  : 3.14+

Provides reusable workspace views.
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
        title: str = "",
        description: str = "",
        name: str = "",
    ) -> None:

        self._parent = parent
        self._name = name or title.lower()
        self._built = False

        self._frame = ttk.Frame(
            parent,
            padding=30,
        )

        if title:
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

        if description:
            ttk.Label(
                self._frame,
                text=description,
                justify="left",
            ).pack(
                anchor="w",
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def built(self) -> bool:
        return self._built

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
        parent: tk.Widget,
    ) -> None:

        self._chat = GUIChat(parent)

        self._chat.build()

    @property
    def frame(self) -> ttk.Frame:

        return self._chat.frame

    @property
    def chat(self) -> GUIChat:

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
