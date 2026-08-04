from __future__ import annotations

from scholaros.applications.application import Application
from scholaros.applications.registry import ApplicationRegistry


class ApplicationManager:
    """
    Manages registered applications.
    """

    def __init__(
        self,
        registry: ApplicationRegistry,
    ) -> None:
        """
        Initialize the application manager.
        """

        self._registry = registry

    @property
    def registry(
        self,
    ) -> ApplicationRegistry:
        """
        Return the application registry.
        """

        return self._registry

    def register(
        self,
        application: Application,
    ) -> None:
        """
        Register an application.
        """

        self._registry.add(
            application,
        )

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister an application.
        """

        self._registry.remove(
            name,
        )

    def get(
        self,
        name: str,
    ) -> Application | None:
        """
        Return a registered application.
        """

        return self._registry.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether an application
        is registered.
        """

        return self._registry.contains(
            name,
        )

    def installed(
        self,
    ) -> list[str]:
        """
        Return registered application
        names.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        applications.
        """

        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the application
        manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"applications={len(self._registry)}"
            f")"
        )