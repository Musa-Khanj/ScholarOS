from __future__ import annotations

from scholaros.gui.application import GUIApplication
from scholaros.gui.window import GUIWindow


class GUIIntegration:
    """
    Integrates the GUI layers.
    """

    def __init__(
        self,
        application: GUIApplication,
    ) -> None:

        self._application = application

    @property
    def application(
        self,
    ) -> GUIApplication:

        return self._application

    @property
    def window(
        self,
    ) -> GUIWindow:

        return self.application.window

    def build(
        self,
    ) -> None:

        self.application.build()

    def run(
        self,
    ) -> None:

        self.application.run()

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"application={self.application!r}"
            f")"
        )