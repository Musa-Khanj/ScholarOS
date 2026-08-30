"""
ScholarOS
GUI Chat

Version : 1.0
Status  : In Development

Chat workspace implementation.

Contains only GUI widgets.

No AI logic belongs here.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class GUIChat:
    """
    Chat workspace.
    """

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        self._parent = parent

        self._frame = ttk.Frame(parent)

        self._history = None
        self._input = None
        self._send_button = None

    @property
    def frame(self):
        return self._frame

    @property
    def history(self):
        return self._history

    @property
    def input(self):
        return self._input

    @property
    def send_button(self):
        return self._send_button

    def build(self) -> None:

        self._build_history()

        self._build_input()

    def _build_history(self):

        history = tk.Text(
            self.frame,
            wrap="word",
            state="disabled",
        )

        history.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(10, 5),
        )

        self._history = history

    def _build_input(self):

        container = ttk.Frame(
            self.frame,
        )

        container.pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )

        entry = tk.Text(
            container,
            height=3,
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        button = ttk.Button(
            container,
            text="Send",
        )

        button.pack(
            side="left",
            padx=(8, 0),
        )

        self._input = entry
        self._send_button = button

    def clear(self):

        self.history.configure(
            state="normal",
        )

        self.history.delete(
            "1.0",
            "end",
        )

        self.history.configure(
            state="disabled",
        )

    def append_message(
        self,
        sender: str,
        message: str,
    ) -> None:

        self.history.configure(
            state="normal",
        )

        self.history.insert(
            "end",
            f"{sender}: {message}\n\n",
        )

        self.history.configure(
            state="disabled",
        )

        self.history.see("end")