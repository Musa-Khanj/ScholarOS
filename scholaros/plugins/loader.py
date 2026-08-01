"""
ScholarOS
Plugin Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loads, unloads, reloads, and discovers
ScholarOS plugins.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from scholaros.plugins.base import Plugin


class PluginLoader:
    """
    Loads and discovers ScholarOS plugins.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the plugin loader.
        """

        self._loaded: dict[str, Plugin] = {}

    def load(
        self,
        module: str,
    ) -> Plugin:
        """
        Load a plugin from a Python module.
        """

        imported = importlib.import_module(module)

        plugin = self._find_plugin(imported)

        self._loaded[plugin.manifest.name] = plugin

        return plugin

    def unload(
        self,
        name: str,
    ) -> None:
        """
        Unload a plugin.
        """

        self._loaded.pop(name, None)

    def reload(
        self,
        module: str,
    ) -> Plugin:
        """
        Reload a plugin module.
        """

        imported = importlib.import_module(module)
        imported = importlib.reload(imported)

        plugin = self._find_plugin(imported)

        self._loaded[plugin.manifest.name] = plugin

        return plugin

    def discover(
        self,
        package: str,
    ) -> list[str]:
        """
        Discover plugins inside a package.
        """

        imported = importlib.import_module(package)

        modules = [
            module.name
            for module in pkgutil.iter_modules(
                imported.__path__,
                imported.__name__ + ".",
            )
        ]

        return sorted(modules)

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a plugin is loaded.
        """

        return name in self._loaded

    def get(
        self,
        name: str,
    ) -> Plugin:
        """
        Return a loaded plugin.
        """

        return self._loaded[name]

    def clear(
        self,
    ) -> None:
        """
        Remove all loaded plugins.
        """

        self._loaded.clear()

    @property
    def loaded(
        self,
    ) -> dict[str, Plugin]:
        """
        Return loaded plugins.
        """

        return self._loaded

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self._loaded)}"
            f")"
        )

    def _find_plugin(
        self,
        module: ModuleType,
    ) -> Plugin:
        """
        Locate a plugin instance or plugin class.
        """

        for _, obj in inspect.getmembers(module):

            if isinstance(obj, Plugin):
                return obj

            if (
                inspect.isclass(obj)
                and issubclass(obj, Plugin)
                and obj is not Plugin
            ):
                return obj()

        raise LookupError(
            f"No plugin found in module '{module.__name__}'."
        )