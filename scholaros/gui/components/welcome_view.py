"""
ScholarOS
Welcome View
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class WelcomeView:
    """
    Initial welcome screen.
    """

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        self._frame = ttk.Frame(
            parent,
            padding=40,
        )

        ttk.Label(
            self._frame,
            text="ScholarOS",
            font=(
                "TkDefaultFont",
                24,
                "bold",
            ),
        ).pack(
            pady=(0, 10),
        )

        ttk.Label(
            self._frame,
            text=(
                "How can I help you today?"
            ),
            font=(
                "TkDefaultFont",
                12,
            ),
        ).pack()

    @property
    def frame(
        self,
    ) -> ttk.Frame:
        return self._frame

    def pack(
        self,
        **kwargs,
    ) -> None:
        self.frame.pack(**kwargs)

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}()"
        )