"""
ScholarOS
GUI Chat View

Version : 1.0
Status  : In Development
Python  : 3.14+

## Description

Provides the Chat workspace view.

This view is responsible only for the
graphical interface.

It does not communicate with AI,
research, RAG, plugins, or the
application layer.
"""

from __future__ import annotations

from tkinter import ttk

from scholaros.gui.views import (
    GUIView,
)


class GUIChatView(GUIView):
    """
    Chat workspace view.
    """

    def __init__(
        self,
        parent: ttk.Frame,
    ) -> None:
        super().__init__(
            parent=parent,
            name="chat",
        )

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def build(
        self,
    ) -> None:
        """
        Build the Chat interface.
        """

        if self.built:
            return

        title = ttk.Label(
            self.frame,
            text="Chat",
            font=(
                "TkDefaultFont",
                20,
                "bold",
            ),
        )

        title.pack(
            anchor="w",
            padx=20,
            pady=(20, 10),
        )

        description = ttk.Label(
            self.frame,
            text=(
                "ScholarOS conversational interface.\n"
                "Future AI conversations will appear here."
            ),
        )

        description.pack(
            anchor="w",
            padx=20,
            pady=(0, 20),
        )

        conversation = ttk.Frame(
            self.frame,
        )

        conversation.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10,
        )

        ttk.Label(
            conversation,
            text="No conversation started.",
        ).pack(
            pady=30,
        )

        input_frame = ttk.Frame(
            self.frame,
        )

        input_frame.pack(
            fill="x",
            padx=20,
            pady=20,
        )

        self._input = ttk.Entry(
            input_frame,
        )

        self._input.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self._send = ttk.Button(
            input_frame,
            text="Send",
        )

        self._send.pack(
            side="left",
            padx=(10, 0),
        )

        self._built = True

    # ---------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Refresh the Chat view.
        """

        return None