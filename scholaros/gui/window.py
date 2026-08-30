"""
ScholarOS
GUI Window

Version : 2.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the main ScholarOS desktop shell.

The window owns only the visual structure of the
application. Business logic belongs elsewhere.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from scholaros.gui.constants import (
    APPLICATION_HEIGHT,
    APPLICATION_TITLE,
    APPLICATION_WIDTH,
    DEFAULT_PADDING,
    MINIMUM_HEIGHT,
    MINIMUM_WIDTH,
    STATUS_READY_TEXT,
)
from scholaros.gui.theme import GUITheme
from scholaros.gui.views import (
    ChatPanel,
    WelcomeView,
)


class GUIWindow:
    """
    Main ScholarOS desktop shell.
    """

    def __init__(
        self,
        root: tk.Tk | None = None,
        theme: GUITheme | None = None,
    ) -> None:

        if root is not None:

            self._root = root

        elif tk._default_root is not None:

            self._root = tk._default_root

        else:

            self._root = tk.Tk()

        self._theme = (
            theme
            if theme is not None
            else GUITheme()
        )

        self._built = False

        self._header = None
        self._body = None
        self._sidebar = None
        self._workspace = None
        self._toolbar = None
        self._statusbar = None

        self._welcome_view = None
        self._chat_panel = None

    # -----------------------------------------------------
    # Properties
    # -----------------------------------------------------

    @property
    def root(
        self,
    ) -> tk.Tk:

        return self._root

    @property
    def theme(
        self,
    ) -> GUITheme:

        return self._theme

    @property
    def header(
        self,
    ):

        return self._header

    @property
    def body(
        self,
    ):

        return self._body

    @property
    def sidebar(
        self,
    ):

        return self._sidebar

    @property
    def workspace(
        self,
    ):

        return self._workspace

    @property
    def toolbar(
        self,
    ):

        return self._toolbar

    @property
    def statusbar(
        self,
    ):

        return self._statusbar

    @property
    def status_bar(
        self,
    ):

        return self._statusbar

    @property
    def welcome_view(
        self,
    ):

        return self._welcome_view

    @property
    def chat_panel(
        self,
    ):

        return self._chat_panel

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def build(
        self,
    ) -> None:

        if self._built:
            return

        self.theme.apply(
            self.root,
        )

        self._configure_window()

        self._build_header()
        self._build_body()
        self._build_statusbar()

        self._built = True

    def show(
        self,
    ) -> None:

        self.root.mainloop()

    def show_welcome(
        self,
    ) -> None:

        if self.welcome_view is not None:

            self.welcome_view.show()

    def show_chat(
        self,
    ) -> None:

        if self.chat_panel is not None:

            self.chat_panel.show()

    # -----------------------------------------------------
    # Window
    # -----------------------------------------------------

    def _configure_window(
        self,
    ) -> None:

        self.root.title(
            APPLICATION_TITLE,
        )

        self.root.geometry(
            f"{APPLICATION_WIDTH}x{APPLICATION_HEIGHT}",
        )

        self.root.minsize(
            MINIMUM_WIDTH,
            MINIMUM_HEIGHT,
        )

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    def _build_header(
        self,
    ) -> None:

        frame = ttk.Frame(
            self.root,
            padding=DEFAULT_PADDING,
        )

        frame.pack(
            fill="x",
        )

        ttk.Label(
            frame,
            text=APPLICATION_TITLE,
            style="Heading.TLabel",
        ).pack(
            anchor="w",
        )

        ttk.Label(
            frame,
            text="AI Research Operating System",
            style="SubHeading.TLabel",
        ).pack(
            anchor="w",
        )

        self._header = frame

    # -----------------------------------------------------
    # Body
    # -----------------------------------------------------

    def _build_body(
        self,
    ) -> None:

        frame = ttk.Frame(
            self.root,
            padding=DEFAULT_PADDING,
        )

        frame.pack(
            fill="both",
            expand=True,
        )

        self._body = frame

        self._build_sidebar()
        self._build_workspace()

    # -----------------------------------------------------
    # Sidebar
    # -----------------------------------------------------

    def _build_sidebar(
        self,
    ) -> None:

        frame = ttk.Frame(
            self.body,
            width=180,
            padding=DEFAULT_PADDING,
        )

        frame.pack(
            side="left",
            fill="y",
        )

        for text in (
            "🏠 Home",
            "💬 Chat",
            "📄 Research",
            "📚 Library",
            "🧩 Plugins",
            "⚙ Settings",
        ):

            ttk.Button(
                frame,
                text=text,
            ).pack(
                fill="x",
                pady=4,
            )

        self._sidebar = frame

    # -----------------------------------------------------
    # Workspace
    # -----------------------------------------------------

    def _build_workspace(
        self,
    ) -> None:

        container = ttk.Frame(
            self.body,
            padding=DEFAULT_PADDING,
        )

        container.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self._build_toolbar(
            container,
        )

        workspace = ttk.Frame(
            container,
        )

        workspace.pack(
            fill="both",
            expand=True,
        )

        self._workspace = workspace

        self._welcome_view = WelcomeView(
            parent=self._workspace,
            theme=self.theme,
        )

        self._chat_panel = ChatPanel(
            parent=self._workspace,
            theme=self.theme,
        )

        self.welcome_view.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.chat_panel.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        workspace.grid_rowconfigure(
            0,
            weight=1,
        )

        workspace.grid_columnconfigure(
            0,
            weight=1,
        )

        self.show_welcome()

    # -----------------------------------------------------
    # Toolbar
    # -----------------------------------------------------

    def _build_toolbar(
        self,
        parent: ttk.Frame,
    ) -> None:

        frame = ttk.Frame(
            parent,
        )

        frame.pack(
            fill="x",
            pady=(0, DEFAULT_PADDING),
        )

        ttk.Button(
            frame,
            text="Refresh",
        ).pack(
            side="right",
            padx=4,
        )

        ttk.Button(
            frame,
            text="About",
        ).pack(
            side="right",
            padx=4,
        )

        ttk.Button(
            frame,
            text="Exit",
            command=self.root.destroy,
        ).pack(
            side="right",
            padx=4,
        )

        self._toolbar = frame

    # -----------------------------------------------------
    # Status Bar
    # -----------------------------------------------------

    def _build_statusbar(
        self,
    ) -> None:

        status = ttk.Label(
            self.root,
            text=STATUS_READY_TEXT,
            anchor="w",
            padding=DEFAULT_PADDING,
        )

        status.pack(
            fill="x",
            side="bottom",
        )

        self._statusbar = status

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"root={self.root!r}, "
            f"theme={self.theme!r}, "
            f"welcome_view={self.welcome_view!r}, "
            f"chat_panel={self.chat_panel!r}"
            f")"
        )