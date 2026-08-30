"""
ScholarOS
GUI Theme

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Centralized visual theme for ScholarOS.

The theme contains the application's color
palette, typography, spacing, and sizing
values. It is intentionally independent of
Tkinter widgets so it can be easily tested.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from scholaros.gui.constants import (
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    HEADER_HEIGHT,
    SIDEBAR_WIDTH,
    STATUS_BAR_HEIGHT,
    TOOLBAR_HEIGHT,
)


@dataclass(
    frozen=True,
    slots=True,
)
class GUITheme:
    """
    Immutable ScholarOS visual theme.
    """
    def apply(
        self,
        root: tk.Tk,
    ) -> None:
        """
        Apply the ScholarOS theme.
        """

        style = ttk.Style(root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        root.configure(
            background=self.background,
        )

        style.configure(
            ".",
            background=self.background,
            foreground=self.text,
            font=(
                self.font_family,
                self.font_size,
            ),
        )

        style.configure(
            "TFrame",
            background=self.background,
        )

        style.configure(
            "TLabel",
            background=self.background,
            foreground=self.text,
            font=(
                self.font_family,
                self.font_size,
            ),
        )

        style.configure(
            "Heading.TLabel",
            background=self.background,
            foreground=self.text,
            font=(
                self.font_family,
                self.title_font_size,
                "bold",
            ),
        )

        style.configure(
            "SubHeading.TLabel",
            background=self.background,
            foreground=self.text_secondary,
            font=(
                self.font_family,
                self.heading_font_size,
            ),
        )

        style.configure(
            "Status.TLabel",
            background=self.surface,
            foreground=self.text_secondary,
            font=(
                self.font_family,
                self.small_font_size,
            ),
        )

        style.configure(
            "TButton",
            padding=self.padding_small,
            font=(
                self.font_family,
                self.font_size,
            ),
        )

    # -------------------------------------------------
    # Colors
    # -------------------------------------------------

    background: str = "#1E1E1E"
    surface: str = "#252526"

    primary: str = "#007ACC"
    secondary: str = "#3A96DD"

    accent: str = "#00BCF2"

    text: str = "#FFFFFF"
    text_secondary: str = "#C8C8C8"

    border: str = "#3C3C3C"

    success: str = "#16A34A"
    warning: str = "#F59E0B"
    error: str = "#DC2626"

    # -------------------------------------------------
    # Typography
    # -------------------------------------------------

    font_family: str = DEFAULT_FONT_FAMILY

    font_size: int = DEFAULT_FONT_SIZE

    title_font_size: int = 18
    heading_font_size: int = 14
    small_font_size: int = 10

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    window_width: int = DEFAULT_WINDOW_WIDTH
    window_height: int = DEFAULT_WINDOW_HEIGHT

    sidebar_width: int = SIDEBAR_WIDTH

    header_height: int = HEADER_HEIGHT
    toolbar_height: int = TOOLBAR_HEIGHT
    status_bar_height: int = STATUS_BAR_HEIGHT

    padding_small: int = 4
    padding: int = 8
    padding_large: int = 16

    spacing_small: int = 4
    spacing: int = 8
    spacing_large: int = 16


DEFAULT_THEME = GUITheme()