"""
ScholarOS
Welcome View

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from tkinter import ttk


class WelcomeView:
    """
    Welcome screen displayed when the
    application starts.
    """

    def __init__(self, parent, theme):
        self._theme = theme

        self._frame = ttk.Frame(
            parent,
            padding=self._theme.padding_large,
        )

        self._label = ttk.Label(
            self._frame,
            text="ScholarOS is ready.",
            font=(
                self._theme.font_family,
                self._theme.heading_font_size,
                "bold",
            ),
        )

        self._label.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

    @property
    def frame(
        self,
    ) -> ttk.Frame:

        return self._frame

    @property
    def label(
        self,
    ) -> ttk.Label:

        return self._label

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