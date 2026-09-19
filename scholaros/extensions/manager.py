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

from typing import Any

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

    def get_optional(
        self,
        name: str,
    ) -> Extension | None:
        """
        Return the specified extension if registered, or None.
        """

        return self._extensions.get(name)

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

    def enable(
        self,
        name: str,
    ) -> None:
        """Enable an extension."""
        self.get(name).enable()

    def disable(
        self,
        name: str,
    ) -> None:
        """Disable an extension."""
        self.get(name).disable()

    def execute(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute an extension."""
        ext = self.get(name)
        if not ext.enabled:
            raise RuntimeError(f"Extension '{name}' is currently disabled.")
        return ext.execute(*args, **kwargs)

    def list_extensions(
        self,
        enabled_only: bool = False,
    ) -> list[Extension]:
        """Return list of extensions."""
        exts = list(self._extensions.values())
        if enabled_only:
            return [e for e in exts if e.enabled]
        return exts

    def get_by_extension_point(
        self,
        point: str,
        enabled_only: bool = True,
    ) -> list[Extension]:
        """Return extensions targeting a specific extension point."""
        exts = [
            e for e in self._extensions.values()
            if getattr(e, "extension_point", "general") == point
        ]
        if enabled_only:
            return [e for e in exts if e.enabled]
        return exts

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
