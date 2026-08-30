"""
ScholarOS
Chat Panel

Combines the conversation view
and input bar.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .conversation_view import ConversationView
from .input_bar import InputBar


class ChatPanel:
    """
    Main chat workspace.
    """

    def __init__(
        self,
        parent: tk.Widget,
    ) -> None:

        self._frame = ttk.Frame(
            parent,
        )

        self._conversation = (
            ConversationView(
                self._frame,
            )
        )

        self._conversation.pack(
            fill="both",
            expand=True,
            pady=(0, 10),
        )

        self._input_bar = (
            InputBar(
                self._frame,
            )
        )

        self._input_bar.pack(
            fill="x",
        )

    @property
    def frame(
        self,
    ) -> ttk.Frame:
        return self._frame

    @property
    def conversation(
        self,
    ) -> ConversationView:
        return self._conversation

    @property
    def input_bar(
        self,
    ) -> InputBar:
        return self._input_bar

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