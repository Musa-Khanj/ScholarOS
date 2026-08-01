"""
ScholarOS
Plugin Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manages the lifecycle of plugins while
delegating all storage responsibilities
to the PluginRegistry.
"""

from __future__ import annotations

from scholaros.plugins.base import Plugin
from scholaros.plugins.registry import PluginRegistry


class PluginManager:
    """
    Manages plugin lifecycle operations.

    Plugin storage is delegated to the
    PluginRegistry.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the plugin manager.
        """

        self._registry = PluginRegistry()

    def register(
        self,
        plugin: Plugin,
    ) -> None:
        """
        Register a plugin.
        """

        self._registry.add(plugin)

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a plugin.
        """

        self._registry.remove(name)

    def get(
        self,
        name: str,
    ) -> Plugin:
        """
        Return the specified plugin.
        """

        return self._registry.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the specified plugin
        is registered.
        """

        return self._registry.contains(name)

    def installed(
        self,
    ) -> list[str]:
        """
        Return the names of all registered
        plugins.
        """

        return self._registry.names()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered plugins.
        """

        self._registry.clear()

    @property
    def plugins(
        self,
    ) -> dict[str, Plugin]:
        """
        Return the registered plugins.
        """

        return self._registry.plugins

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the PluginManager.
        """

        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self._registry.plugins)}"
            f")"
        )