"""
ScholarOS
GUI Workspace

Version : 1.0
Status  : In Development
Python  : 3.14+

## Description

Provides the central workspace manager for
the ScholarOS graphical interface.

The workspace is responsible for managing
GUI views and switching between them.

It does not perform application logic,
research, AI, plugins, or business logic.
"""

from __future__ import annotations

from tkinter import ttk

from scholaros.gui.chat_view import GUIChatView
from scholaros.gui.home_view import GUIHomeView
from scholaros.gui.views import (
    ChatView,
    HomeView,
    LibraryView,
    PluginsView,
    ResearchView,
    SettingsView,
)


class GUIWorkspace:
    """
    Manages the ScholarOS workspace.

    The workspace owns a container frame and
    controls which registered view is
    currently visible.
    """

    def __init__(
        self,
        parent: ttk.Frame,
    ) -> None:
        """
        Initialize the workspace.

        Parameters
        ----------
        parent:
            Parent widget that owns the
            workspace container.
        """

        self._parent = parent

        self._container = ttk.Frame(
            parent,
        )

        self._container.pack(
            fill="both",
            expand=True,
        )

        self._views: dict[str, object] = {}

        self._current_name: str | None = None

        self._current_view: object | None = None

        self._views: dict[str, object] = {}

        self._active = None

    def create_default_views(
        self,
    ) -> None:
        """
        Create the default workspace views.
        """

        self.add_view(
            GUIHomeView(
                self.frame,
            )
        )

        self.add_view(
            GUIChatView(
                self.frame,
            )
        )

        self.show(
            "home",
        )

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------


    @property
    def parent(
        self,
    ) -> ttk.Frame:
        """
        Return the parent widget.
        """

        return self._parent

    @property
    def container(
        self,
    ) -> ttk.Frame:
        """
        Return the workspace container.
        """

        return self._container

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def register(
        self,
        name: str,
        view: object,
    ) -> None:
        """
        Register a workspace view.

        Parameters
        ----------
        name:
            Unique view name.

        view:
            View instance.
        """

        self._views[name] = view

    def registered_views(
        self,
    ) -> tuple[str, ...]:
        """
        Return registered view names.
        """

        return tuple(
            self._views.keys()
        )

    def current(
        self,
    ) -> object | None:
        """
        Return the current view.
        """

        return self._current_view

    def current_name(
        self,
    ) -> str | None:
        """
        Return the current view name.
        """

        return self._current_name

    def clear(
        self,
    ) -> None:

        if self._active is not None:

            self._active.frame.pack_forget()

            self._active = None

    def show(
        self,
        name: str,
    ) -> None:
        """
        Display a workspace.
        """

        if not self._views:
            self._create_views()

        if self._active is not None:

            self._active.frame.pack_forget()

        self._active = self._views[name]

        self._active.frame.pack(
            fill="both",
            expand=True,
        )


    @property
    def active(
        self,
    ):
        """
        Return the active view.
        """

        return self._active


    def _create_views(
        self,
    ) -> None:
        """
        Create every workspace view.
        """

        self._views = {
            "Home": HomeView(self.frame),
            "Chat": ChatView(self.frame),
            "Research": ResearchView(self.frame),
            "Library": LibraryView(self.frame),
            "Plugins": PluginsView(self.frame),
            "Settings": SettingsView(self.frame),
        }

    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"views={len(self._views)}, "
            f"current={self._current_name!r}"
            f")"
        )