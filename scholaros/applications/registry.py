from __future__ import annotations

from scholaros.applications.application import Application


class ApplicationRegistry:
    """
    Stores registered applications.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the application registry.
        """

        self._applications: dict[str, Application] = {}

    def add(
        self,
        application: Application,
    ) -> None:
        """
        Register an application.
        """

        self._applications[
            application.__class__.__name__
        ] = application

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered application.
        """

        self._applications.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Application | None:
        """
        Return a registered application.
        """

        return self._applications.get(
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

        return name in self._applications

    def names(
        self,
    ) -> list[str]:
        """
        Return registered application names.
        """

        return list(
            self._applications.keys(),
        )

    def values(
        self,
    ) -> list[Application]:
        """
        Return registered applications.
        """

        return list(
            self._applications.values(),
        )

    def items(
        self,
    ) -> list[tuple[str, Application]]:
        """
        Return registered application items.
        """

        return list(
            self._applications.items(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered applications.
        """

        self._applications.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered
        applications.
        """

        return len(
            self._applications,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"applications={len(self)}"
            f")"
        )