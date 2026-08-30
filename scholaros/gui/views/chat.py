"""
ScholarOS
Chat Panel

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from scholaros.gui.theme import GUITheme


class ChatPanel:
    """
    Chat workspace.
    """

    def __init__(
        self,
        parent: tk.Widget,
        theme: GUITheme,
    ) -> None:

        self._theme = theme

        self._frame = ttk.Frame(
            parent,
            padding=self._theme.padding,
        )

        self._history_frame = ttk.Frame(
            self._frame,
            padding=self._theme.padding_small,
        )

        self._history_frame.pack(
            fill="both",
            expand=True,
        )

        self._history_label = ttk.Label(
            self._history_frame,
            text="Chat History",
            font=(self._theme.font_family, self._theme.font_size)
        )

        self._history_label.pack(
            anchor="w",
        )

        self._input_frame = ttk.Frame(
            self._frame,
            padding=self._theme.padding_small,
        )

        self._input_frame.pack(
            fill="x",
            side="bottom",
        )

        self._entry = ttk.Entry(
            self._input_frame,
        )

        self._entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self._send_button = ttk.Button(
            self._input_frame,
            text="Send",
        )

        self._send_button.pack(
            side="right",
        )

    @property
    def frame(
        self,
    ) -> ttk.Frame:

        return self._frame

    @property
    def entry(
        self,
    ) -> ttk.Entry:

        return self._entry

    @property
    def send_button(
        self,
    ) -> ttk.Button:

        return self._send_button

    def show(
        self,
    ) -> None:

        self.frame.tkraise()

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}()"
        )