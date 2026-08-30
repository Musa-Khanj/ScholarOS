"""
ScholarOS
Conversation View

Displays conversation history.
"""

from __future__ import annotations

import tkinter as tk


class ConversationView:
    """
    Read-only conversation display.
    """

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        self._text = tk.Text(
            parent,
            wrap="word",
            state="disabled",
        )

    @property
    def widget(
        self,
    ) -> tk.Text:
        """
        Return underlying widget.
        """

        return self._text

    def pack(
        self,
        **kwargs,
    ) -> None:
        """
        Pack widget.
        """

        self.widget.pack(**kwargs)

    def clear(
        self,
    ) -> None:
        """
        Remove all text.
        """

        self.widget.configure(
            state="normal",
        )

        self.widget.delete(
            "1.0",
            tk.END,
        )

        self.widget.configure(
            state="disabled",
        )

    def append(
        self,
        text: str,
    ) -> None:
        """
        Append text.
        """

        self.widget.configure(
            state="normal",
        )

        self.widget.insert(
            tk.END,
            text + "\n",
        )

        self.widget.see(
            tk.END,
        )

        self.widget.configure(
            state="disabled",
        )

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}()"
        )