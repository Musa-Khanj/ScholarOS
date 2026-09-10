"""
ScholarOS Plugin Loader.

Responsible strictly for importing and instantiating plugin modules
from module strings or file paths. Contains no lifecycle logic.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
import pkgutil
from types import ModuleType
from typing import Any

from scholaros.plugins.base import Plugin
from scholaros.plugins.exceptions import PluginLoadError


class PluginLoader:
    """
    Imports and instantiates ScholarOS plugins without running lifecycle methods.
    """

    def __init__(self) -> None:
        self._loaded: dict[str, Plugin] = {}

    def load(self, module_or_path: str | Path) -> Plugin:
        """
        Load a plugin from a Python module name or filesystem path.
        """
        path_obj = Path(module_or_path) if isinstance(module_or_path, (str, Path)) else None
        if path_obj is not None and (path_obj.is_file() or str(module_or_path).endswith(".py")):
            return self.load_from_file(path_obj)

        module_name = str(module_or_path)
        return self.load_from_module(module_name)

    def load_from_module(self, module_name: str) -> Plugin:
        """
        Import a Python module by name and instantiate the contained Plugin.
        """
        try:
            imported = importlib.import_module(module_name)
        except Exception as exc:
            raise PluginLoadError(f"Failed to import module {module_name!r}: {exc}") from exc

        plugin = self._find_plugin(imported)
        self._loaded[plugin.name] = plugin
        return plugin

    def load_from_file(self, file_path: str | Path) -> Plugin:
        """
        Import a Python file from the filesystem and instantiate the contained Plugin.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise PluginLoadError(f"Plugin file not found: {path}")

        module_name = f"scholaros_plugin_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Could not load module specification from {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as exc:
            raise PluginLoadError(f"Failed to load plugin from file {path}: {exc}") from exc

        plugin = self._find_plugin(module)
        self._loaded[plugin.name] = plugin
        return plugin

    def reload(self, module_name: str) -> Plugin:
        """
        Reload an existing plugin module and re-extract the plugin.
        """
        try:
            imported = importlib.import_module(module_name)
            imported = importlib.reload(imported)
        except Exception as exc:
            raise PluginLoadError(f"Failed to reload module {module_name!r}: {exc}") from exc

        plugin = self._find_plugin(imported)
        self._loaded[plugin.name] = plugin
        return plugin

    def unload(self, name: str) -> None:
        """
        Remove a plugin from the loaded module cache.
        """
        self._loaded.pop(name, None)

    def contains(self, name: str) -> bool:
        """
        Return whether a plugin is tracked in the loader cache.
        """
        return name in self._loaded

    def get(self, name: str) -> Plugin:
        """
        Return a loaded plugin from cache.
        """
        return self._loaded[name]

    def clear(self) -> None:
        """
        Clear all loaded plugins from cache.
        """
        self._loaded.clear()

    @property
    def loaded(self) -> dict[str, Plugin]:
        """
        Return all loaded plugins dictionary.
        """
        return self._loaded

    def discover(self, package: str) -> list[str]:
        """
        Discover plugin module names within a package.
        """
        try:
            imported = importlib.import_module(package)
        except ImportError:
            return []

        if not hasattr(imported, "__path__"):
            return []

        modules = [
            module.name
            for module in pkgutil.iter_modules(
                imported.__path__,
                imported.__name__ + ".",
            )
        ]
        return sorted(modules)

    def _find_plugin(self, module: ModuleType) -> Plugin:
        """
        Locate and instantiate a Plugin instance or subclass within the module.
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

        raise PluginLoadError(f"No plugin found in module '{module.__name__}'.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(plugins={len(self._loaded)})"


__all__ = [
    "PluginLoader",
]