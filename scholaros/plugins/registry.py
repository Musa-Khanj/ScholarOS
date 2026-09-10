"""
ScholarOS Plugin Registry.

Tracks loaded plugins in-memory. Provides storage and retrieval without
performing any loading or lifecycle management.
"""

from __future__ import annotations

from typing import Iterator

from scholaros.plugins.base import Plugin
from scholaros.plugins.exceptions import PluginNotFoundError


class PluginRegistry:
    """
    In-memory storage for registered ScholarOS plugins.
    Responsible solely for tracking plugin instances.
    """

    def __init__(self) -> None:
        # Internal mapping by plugin name / id
        self._plugins: dict[str, Plugin] = {}
        # Secondary index by plugin id -> primary name
        self._id_to_name: dict[str, str] = {}

    def add(self, plugin: Plugin) -> None:
        """
        Store a plugin in the registry.
        """
        name = getattr(plugin.manifest, "name", plugin.name)
        self._plugins[name] = plugin
        if hasattr(plugin, "id") and plugin.id:
            self._id_to_name[plugin.id] = name

    def remove(self, name_or_id: str) -> bool:
        """
        Remove a plugin from the registry.
        Returns True if a plugin was removed.
        """
        primary_name = self._id_to_name.pop(name_or_id, name_or_id)
        removed = self._plugins.pop(primary_name, None)
        if removed is not None:
            # Also clean reverse index
            if hasattr(removed, "id"):
                self._id_to_name.pop(removed.id, None)
            return True
        return False

    def get(self, name_or_id: str) -> Plugin:
        """
        Retrieve a plugin by name or ID.
        Raises KeyError / PluginNotFoundError if not present.
        """
        if name_or_id in self._plugins:
            return self._plugins[name_or_id]

        if name_or_id in self._id_to_name:
            primary_name = self._id_to_name[name_or_id]
            return self._plugins[primary_name]

        raise KeyError(f"Plugin not found in registry: {name_or_id!r}")

    def get_optional(self, name_or_id: str, default: Plugin | None = None) -> Plugin | None:
        """
        Retrieve a plugin if present, otherwise return default.
        """
        try:
            return self.get(name_or_id)
        except KeyError:
            return default

    def contains(self, name_or_id: str) -> bool:
        """
        Return True if plugin is registered under name or ID.
        """
        return name_or_id in self._plugins or name_or_id in self._id_to_name

    def clear(self) -> None:
        """
        Remove all registered plugins.
        """
        self._plugins.clear()
        self._id_to_name.clear()

    def names(self) -> list[str]:
        """
        Return sorted list of all registered plugin names.
        """
        return sorted(self._plugins.keys())

    def ids(self) -> list[str]:
        """
        Return sorted list of all registered plugin IDs.
        """
        return sorted(getattr(p, "id", name) for name, p in self._plugins.items())

    def values(self) -> list[Plugin]:
        """
        Return list of all registered plugin instances.
        """
        return list(self._plugins.values())

    def items(self) -> list[tuple[str, Plugin]]:
        """
        Return (name, plugin) items.
        """
        return list(self._plugins.items())

    @property
    def plugins(self) -> dict[str, Plugin]:
        """
        Direct access to registered plugins dictionary.
        """
        return self._plugins

    def __len__(self) -> int:
        return len(self._plugins)

    def __iter__(self) -> Iterator[Plugin]:
        return iter(self._plugins.values())

    def __contains__(self, name_or_id: object) -> bool:
        if isinstance(name_or_id, str):
            return self.contains(name_or_id)
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(plugins={len(self._plugins)})"


__all__ = [
    "PluginRegistry",
]