"""
ScholarOS
Hook Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registers and manages ScholarOS hooks.
"""

from __future__ import annotations

from scholaros.hooks.hook import Hook


class HookManager:
    """
    Manages registered hooks.
    """

    def __init__(
        self,
    ) -> None:

        self._hooks: dict[str, Hook] = {}

    def register(
        self,
        hook: Hook,
    ) -> None:
        """
        Register a hook.
        """

        self._hooks[hook.name] = hook

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a hook.
        """

        self._hooks.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Hook:
        """
        Return the specified hook.
        """

        return self._hooks[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether the hook
        is registered.
        """

        return name in self._hooks

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered hook names.
        """

        return sorted(
            self._hooks,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered hooks.
        """

        self._hooks.clear()

    @property
    def hooks(
        self,
    ) -> dict[str, Hook]:
        """
        Return registered hooks.
        """

        return self._hooks

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"hooks={len(self._hooks)}"
            f")"
        )