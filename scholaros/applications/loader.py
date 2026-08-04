from __future__ import annotations

from scholaros.applications.application import Application
from scholaros.applications.manager import ApplicationManager


class ApplicationLoader:
    """
    Loads and unloads applications.
    """

    def __init__(
        self,
        manager: ApplicationManager,
    ) -> None:
        """
        Initialize the application loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> ApplicationManager:
        """
        Return the application manager.
        """

        return self._manager

    def load(
        self,
        application: Application,
    ) -> None:
        """
        Load an application.
        """

        self._manager.register(
            application,
        )

    def unload(
        self,
        name: str,
    ) -> None:
        """
        Unload an application.
        """

        self._manager.unregister(
            name,
        )

    def reload(
        self,
        application: Application,
    ) -> None:
        """
        Reload an application.
        """

        self.unload(
            application.__class__.__name__,
        )

        self.load(
            application,
        )

    def discover(
        self,
    ) -> list[str]:
        """
        Return the discovered applications.
        """

        return self._manager.installed()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"applications={len(self.manager.registry)}"
            f")"
        )