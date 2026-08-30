"""
ScholarOS
Sidebar Button
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class SidebarButton:
    """
    Reusable navigation button.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command=None,
    ) -> None:

        self._button = ttk.Button(
            parent,
            text=text,
            command=command,
        )

    @property
    def widget(
        self,
    ) -> ttk.Button:
        return self._button

    def pack(
        self,
        **kwargs,
    ) -> None:
        self.widget.pack(**kwargs)

    def configure(
        self,
        **kwargs,
    ) -> None:
        self.widget.configure(
            **kwargs,
        )

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"text={self.widget.cget('text')!r}"
            f")"
        )