"""
ScholarOS
Extension Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registers and manages ScholarOS
extensions.
"""

from __future__ import annotations

from scholaros.extensions.extension import Extension


class ExtensionManager:
    """
    Manages registered extensions.
    """

    def __init__(
        self,
    ) -> None:

        self._extensions: dict[str, Extension] = {}

    def register(
        self,
        extension: Extension,
    ) -> None:
        """
        Register an extension.
        """

        self._extensions[
            extension.name
        ] = extension

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister an extension.
        """

        self._extensions.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Extension:
        """
        Return the specified extension.
        """

        return self._extensions[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether the specified
        extension is registered.
        """

        return (
            name
            in self._extensions
        )

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered extension
        names.
        """

        return sorted(
            self._extensions,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        extensions.
        """

        self._extensions.clear()

    @property
    def extensions(
        self,
    ) -> dict[str, Extension]:
        """
        Return the registered
        extensions.
        """

        return self._extensions

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        ExtensionManager.
        """

        return (
            f"{self.__class__.__name__}("
            f"extensions="
            f"{len(self._extensions)}"
            f")"
        )