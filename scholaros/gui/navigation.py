"""
ScholarOS
GUI Navigation

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from scholaros.gui.workspace import GUIWorkspace


class GUINavigation:
    """
    Coordinates workspace navigation.
    """

    def __init__(
        self,
        workspace: GUIWorkspace,
    ) -> None:

        self._workspace = workspace

    @property
    def workspace(
        self,
    ) -> GUIWorkspace:
        """
        Return the managed workspace.
        """

        return self._workspace

    def show(
        self,
        name: str,
    ) -> None:
        """
        Display a workspace view.
        """

        self.workspace.show(
            name,
        )

    def home(
        self,
    ) -> None:

        self.show("Home")

    def chat(
        self,
    ) -> None:

        self.show("Chat")

    def research(
        self,
    ) -> None:

        self.show("Research")

    def library(
        self,
    ) -> None:

        self.show("Library")

    def plugins(
        self,
    ) -> None:

        self.show("Plugins")

    def settings(
        self,
    ) -> None:

        self.show("Settings")

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"workspace={self.workspace!r}"
            f")"
        )