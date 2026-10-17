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
from typing import Any


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

        # Visual styling tags for user/assistant separation and citations
        history.tag_configure(
            "sender_you",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#0d6efd",
        )
        history.tag_configure(
            "sender_scholaros",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#198754",
        )
        history.tag_configure(
            "sender_system",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#dc3545",
        )
        history.tag_configure(
            "citations",
            font=("TkDefaultFont", 9, "italic"),
            foreground="#6c757d",
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

        # Bind Enter to invoke send button, Shift+Enter for multiline
        entry.bind("<Return>", self._on_enter_pressed)
        entry.bind("<Shift-Return>", self._on_shift_enter)

        self._input = entry
        self._send_button = button

    def _on_enter_pressed(self, event: tk.Event[Any]) -> str:
        """Trigger send button on Enter without inserting a newline."""
        if self._send_button is not None:
            self._send_button.invoke()
        return "break"

    def _on_shift_enter(self, event: tk.Event[Any]) -> None:
        """Allow Shift+Enter to insert a normal newline in multi-line prompts."""
        return None

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
        citations: list[Any] | tuple[Any, ...] | None = None,
    ) -> None:

        self.history.configure(
            state="normal",
        )

        tag = f"sender_{sender.lower()}"
        if hasattr(self.history, "tag_names") and tag in self.history.tag_names():
            self.history.insert(
                "end",
                f"{sender}: ",
                tag,
            )
        else:
            self.history.insert(
                "end",
                f"{sender}: ",
            )

        self.history.insert(
            "end",
            f"{message}\n\n",
        )

        if citations and isinstance(citations, (list, tuple)):
            clean_cites = [str(c) for c in citations if c is not None and str(c).strip()]
            if clean_cites:
                cite_str = ", ".join(clean_cites)
                self.history.insert(
                    "end",
                    f"  📚 Sources: {cite_str}\n\n",
                    "citations",
                )

        self.history.configure(
            state="disabled",
        )

        self.history.see("end")
