"""
ScholarOS
Plugin Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Maintains the collection of registered
plugins. The registry is responsible only
for storing and retrieving plugins.
"""

from __future__ import annotations

from scholaros.plugins.base import Plugin


class PluginRegistry:
    """
    Stores registered plugins.

    This class is responsible only for
    plugin storage. Lifecycle management
    belongs to PluginManager.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize an empty plugin registry.
        """

        self._plugins: dict[str, Plugin] = {}

    def add(
        self,
        plugin: Plugin,
    ) -> None:
        """
        Add a plugin to the registry.
        """

        self._plugins[plugin.manifest.name] = plugin

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a plugin from the registry.
        """

        self._plugins.pop(name, None)

    def get(
        self,
        name: str,
    ) -> Plugin:
        """
        Return the requested plugin.
        """

        return self._plugins[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the plugin exists.
        """

        return name in self._plugins

    def clear(
        self,
    ) -> None:
        """
        Remove every registered plugin.
        """

        self._plugins.clear()

    def names(
        self,
    ) -> list[str]:
        """
        Return all plugin names.
        """

        return sorted(self._plugins)

    def values(
        self,
    ) -> list[Plugin]:
        """
        Return all registered plugins.
        """

        return list(self._plugins.values())

    def items(
        self,
    ) -> list[tuple[str, Plugin]]:
        """
        Return registry items.
        """

        return list(self._plugins.items())

    @property
    def plugins(
        self,
    ) -> dict[str, Plugin]:
        """
        Return the registered plugins.
        """

        return self._plugins

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self._plugins)}"
            f")"
        )