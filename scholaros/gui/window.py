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

from typing import Any
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

        elif getattr(tk, "_default_root", None) is not None:
            self._root = getattr(tk, "_default_root")

        else:
            self._root = tk.Tk()

        self._theme = theme if theme is not None else GUITheme()

        self._built = False

        self._header: ttk.Frame | None = None
        self._body: ttk.Frame | None = None
        self._sidebar: ttk.Frame | None = None
        self._workspace: ttk.Frame | None = None
        self._toolbar: ttk.Frame | None = None
        self._statusbar: ttk.Label | None = None

        self._welcome_view: WelcomeView | None = None
        self._chat_panel: ChatPanel | None = None
        self._home_view: Any | None = None
        self._chat_view: Any | None = None
        self._research_view: Any | None = None
        self._library_view: Any | None = None
        self._plugins_view: Any | None = None
        self._settings_view: Any | None = None
        self._current_status: str = STATUS_READY_TEXT
        self._application: Any | None = None

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

    @property
    def home_view(
        self,
    ) -> Any | None:
        return self._home_view

    @property
    def chat_view(
        self,
    ) -> Any | None:
        return self._chat_view

    @property
    def research_view(
        self,
    ) -> Any | None:
        return self._research_view

    @property
    def library_view(
        self,
    ) -> Any | None:
        return self._library_view

    @property
    def plugins_view(
        self,
    ) -> Any | None:
        return self._plugins_view

    @property
    def settings_view(
        self,
    ) -> Any | None:
        return self._settings_view

    @property
    def application(
        self,
    ) -> Any | None:
        """Return the bound GUIApplication instance if injected."""
        return self._application

    def set_application(
        self,
        application: Any,
    ) -> None:
        """Inject GUIApplication reference and propagate to child views."""
        self._application = application
        for view in (
            self._welcome_view,
            self._chat_panel,
            self._home_view,
            self._chat_view,
            self._research_view,
            self._library_view,
            self._plugins_view,
            self._settings_view,
        ):
            if view is not None:
                if hasattr(view, "set_application"):
                    view.set_application(application)
                elif hasattr(view, "application"):
                    try:
                        setattr(view, "application", application)
                    except Exception:
                        pass

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

    def show_home(
        self,
    ) -> None:
        if self._home_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import HomeView

            try:
                self._home_view = HomeView(
                    parent=self._workspace,
                    application=self._application,
                    on_navigate=self.show_view,
                )
                if hasattr(self._home_view, "frame") and hasattr(self._home_view.frame, "grid"):
                    self._home_view.frame.grid(row=0, column=0, sticky="nsew")
            except Exception:
                pass

        if self._home_view is not None:
            if hasattr(self._home_view, "refresh"):
                try:
                    self._home_view.refresh()
                except Exception:
                    pass
            if hasattr(self._home_view, "show"):
                self._home_view.show()
            elif hasattr(self._home_view, "frame") and hasattr(self._home_view.frame, "tkraise"):
                self._home_view.frame.tkraise()
        else:
            self.show_welcome()

    def show_welcome(
        self,
    ) -> None:

        if self.welcome_view is not None:
            self.welcome_view.show()

    def show_chat(
        self,
    ) -> None:
        if self._chat_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import ChatView

            try:
                self._chat_view = ChatView(
                    parent=self._workspace,
                    application=self._application,
                )
                if hasattr(self._chat_view, "frame") and hasattr(self._chat_view.frame, "grid"):
                    self._chat_view.frame.grid(row=0, column=0, sticky="nsew")
            except Exception:
                pass

        if self._chat_view is not None:
            if hasattr(self._chat_view, "show"):
                self._chat_view.show()
            elif hasattr(self._chat_view, "frame") and hasattr(self._chat_view.frame, "tkraise"):
                self._chat_view.frame.tkraise()
        elif self.chat_panel is not None:
            self.chat_panel.show()

    def show_research(
        self,
    ) -> None:
        if self._research_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import ResearchView

            self._research_view = ResearchView(
                parent=self._workspace, application=self._application
            )
            if hasattr(self._research_view, "frame") and hasattr(self._research_view.frame, "grid"):
                self._research_view.frame.grid(row=0, column=0, sticky="nsew")
        if self._research_view is not None:
            if hasattr(self._research_view, "show"):
                self._research_view.show()
            elif hasattr(self._research_view, "frame") and hasattr(
                self._research_view.frame, "tkraise"
            ):
                self._research_view.frame.tkraise()

    def show_library(
        self,
    ) -> None:
        if self._library_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import LibraryView

            self._library_view = LibraryView(parent=self._workspace, application=self._application)
            if hasattr(self._library_view, "frame") and hasattr(self._library_view.frame, "grid"):
                self._library_view.frame.grid(row=0, column=0, sticky="nsew")
        if self._library_view is not None:
            if hasattr(self._library_view, "show"):
                self._library_view.show()
            elif hasattr(self._library_view, "frame") and hasattr(
                self._library_view.frame, "tkraise"
            ):
                self._library_view.frame.tkraise()

    def show_plugins(
        self,
    ) -> None:
        if self._plugins_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import PluginsView

            self._plugins_view = PluginsView(parent=self._workspace, application=self._application)
            if hasattr(self._plugins_view, "frame") and hasattr(self._plugins_view.frame, "grid"):
                self._plugins_view.frame.grid(row=0, column=0, sticky="nsew")
        if self._plugins_view is not None:
            if hasattr(self._plugins_view, "show"):
                self._plugins_view.show()
            elif hasattr(self._plugins_view, "frame") and hasattr(
                self._plugins_view.frame, "tkraise"
            ):
                self._plugins_view.frame.tkraise()

    def show_settings(
        self,
    ) -> None:
        if self._settings_view is None and self._workspace is not None:
            from scholaros.gui.views.workspace_views import SettingsView

            self._settings_view = SettingsView(
                parent=self._workspace, application=self._application
            )
            if hasattr(self._settings_view, "frame") and hasattr(self._settings_view.frame, "grid"):
                self._settings_view.frame.grid(row=0, column=0, sticky="nsew")
        if self._settings_view is not None:
            if hasattr(self._settings_view, "show"):
                self._settings_view.show()
            elif hasattr(self._settings_view, "frame") and hasattr(
                self._settings_view.frame, "tkraise"
            ):
                self._settings_view.frame.tkraise()

    def show_view(
        self,
        name: str,
    ) -> None:
        """Route view switching by canonical name."""
        canonical = name.strip().lower()
        mapping = {
            "home": self.show_home,
            "welcome": self.show_welcome,
            "chat": self.show_chat,
            "research": self.show_research,
            "library": self.show_library,
            "knowledge": self.show_library,
            "plugins": self.show_plugins,
            "settings": self.show_settings,
        }
        handler = mapping.get(canonical, self.show_home)
        handler()

    def set_status(
        self,
        message: str,
        error: bool = False,
    ) -> None:
        """Update the status bar message and optional error indication."""
        self._current_status = message
        if self._statusbar is not None:
            try:
                self._statusbar.configure(text=message)
            except Exception:
                pass

    def get_status(
        self,
    ) -> str:
        """Return the current status bar message."""
        return getattr(self, "_current_status", STATUS_READY_TEXT)

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

        button_definitions = (
            ("🏠 Home", self.show_home),
            ("💬 Chat", self.show_chat),
            ("📄 Research", self.show_research),
            ("📚 Library", self.show_library),
            ("🧩 Plugins", self.show_plugins),
            ("⚙ Settings", self.show_settings),
        )

        for text, command in button_definitions:
            ttk.Button(
                frame,
                text=text,
                command=command,
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

        try:
            from scholaros.gui.views.workspace_views import ChatView, HomeView

            self._home_view = HomeView(
                parent=self._workspace,
                application=self._application,
                on_navigate=self.show_view,
            )
            if hasattr(self._home_view, "frame") and hasattr(self._home_view.frame, "grid"):
                self._home_view.frame.grid(
                    row=0,
                    column=0,
                    sticky="nsew",
                )

            self._chat_view = ChatView(
                parent=self._workspace,
                application=self._application,
            )
            if hasattr(self._chat_view, "frame") and hasattr(self._chat_view.frame, "grid"):
                self._chat_view.frame.grid(
                    row=0,
                    column=0,
                    sticky="nsew",
                )
        except Exception:
            pass

        workspace.grid_rowconfigure(
            0,
            weight=1,
        )

        workspace.grid_columnconfigure(
            0,
            weight=1,
        )

        self.show_home()

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
            f"chat_panel={self.chat_panel!r}, "
            f"home_view={self.home_view!r}, "
            f"chat_view={self.chat_view!r}"
            f")"
        )
