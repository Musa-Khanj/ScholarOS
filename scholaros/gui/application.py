from __future__ import annotations

from scholaros.gui.window import GUIWindow


class GUIApplication:
    """
    Represents the GUI application.

    Coordinates the GUI window.
    """

    def __init__(
        self,
        window: GUIWindow,
    ) -> None:

        self._window = window

    @property
    def window(
        self,
    ) -> GUIWindow:

        return self._window

    def build(
        self,
    ) -> None:

        self.window.build()

    def run(
        self,
    ) -> None:

        self.window.show()

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"window={self.window!r}"
            f")"
        )