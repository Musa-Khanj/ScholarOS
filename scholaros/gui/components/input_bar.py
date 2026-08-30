"""
ScholarOS
Input Bar

Prompt entry and send button.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class InputBar:
    """
    User prompt entry area.
    """

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        self._frame = ttk.Frame(
            parent,
        )

        self._input = tk.Text(
            self._frame,
            height=4,
            wrap="word",
        )

        self._send = ttk.Button(
            self._frame,
            text="Send",
        )

        self._input.pack(
            fill="x",
            expand=True,
            side="left",
            padx=(0, 8),
        )

        self._send.pack(
            side="right",
        )

    @property
    def frame(
        self,
    ) -> ttk.Frame:
        return self._frame

    @property
    def input(
        self,
    ) -> tk.Text:
        return self._input

    @property
    def send_button(
        self,
    ) -> ttk.Button:
        return self._send

    def pack(
        self,
        **kwargs,
    ) -> None:
        self.frame.pack(**kwargs)

    def get_text(
        self,
    ) -> str:
        return (
            self.input.get(
                "1.0",
                tk.END,
            ).strip()
        )

    def clear(
        self,
    ) -> None:
        self.input.delete(
            "1.0",
            tk.END,
        )

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}()"
        )