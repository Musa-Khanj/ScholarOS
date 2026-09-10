"""
ScholarOS Plugin Discovery.

Scans builtin directories, local project paths, and external directories
for plugin manifests and modules.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import pkgutil
from typing import Iterable

from scholaros.plugins.manifest import PluginManifest


@dataclass(slots=True)
class DiscoveredPlugin:
    """
    Metadata representation of a discovered plugin before loading.
    """

    id: str
    name: str
    path: Path
    manifest: PluginManifest
    is_builtin: bool = False
    entry_point: str | None = None


class PluginDiscovery:
    """
    Discovers plugins across builtin, local, and external filesystem locations.
    """

    def __init__(
        self,
        search_paths: Iterable[str | Path] | None = None,
        builtin_dir: Path | None = None,
        local_dir: Path | None = None,
    ) -> None:
        self.builtin_dir = (
            Path(builtin_dir)
            if builtin_dir is not None
            else Path(__file__).resolve().parent / "builtin"
        )
        self.local_dir = (
            Path(local_dir)
            if local_dir is not None
            else Path.cwd() / "plugins"
        )
        self.search_paths: list[Path] = [
            Path(p).resolve() for p in (search_paths or [])
        ]

    def add_search_path(self, path: str | Path) -> None:
        """Add an external plugin directory to search."""
        p = Path(path).resolve()
        if p not in self.search_paths:
            self.search_paths.append(p)

    def discover_builtin(self) -> list[DiscoveredPlugin]:
        """Discover all plugins in the builtin directory."""
        if not self.builtin_dir.is_dir():
            return []
        return self.discover_directory(self.builtin_dir, is_builtin=True)

    def discover_local(self) -> list[DiscoveredPlugin]:
        """Discover plugins in the local project plugins directory."""
        if not self.local_dir.is_dir():
            return []
        return self.discover_directory(self.local_dir, is_builtin=False)

    def discover_directory(
        self,
        directory: Path | str,
        is_builtin: bool = False,
    ) -> list[DiscoveredPlugin]:
        """
        Scan a directory for plugin packages (subdirectories with manifest/python file)
        or standalone Python plugin files.
        """
        dir_path = Path(directory).resolve()
        if not dir_path.is_dir():
            return []

        discovered: list[DiscoveredPlugin] = []

        for item in dir_path.iterdir():
            if item.name.startswith((".", "__")):
                continue

            manifest: PluginManifest | None = None
            entry_point: str | None = None

            if item.is_dir():
                # Look for manifest.json, manifest.toml, or plugin.json
                for manifest_name in ("manifest.json", "manifest.toml", "plugin.json"):
                    manifest_file = item / manifest_name
                    if manifest_file.is_file():
                        try:
                            manifest = PluginManifest.from_file(manifest_file)
                            break
                        except Exception:
                            pass

                # If no manifest file, check for __init__.py or main.py
                if manifest is None:
                    init_file = item / "__init__.py"
                    plugin_py = item / "plugin.py"
                    target_py = init_file if init_file.is_file() else (plugin_py if plugin_py.is_file() else None)
                    if target_py:
                        name = item.name.replace("_", " ").title()
                        manifest = PluginManifest(name=name, id=item.name.lower())
                        entry_point = str(target_py)
                else:
                    if manifest.entry_point:
                        entry_point = str(item / manifest.entry_point)
                    else:
                        init_file = item / "__init__.py"
                        entry_point = str(init_file) if init_file.is_file() else str(item)

            elif item.is_file() and item.suffix == ".py":
                # Standalone plugin file
                name = item.stem.replace("_", " ").title()
                manifest = PluginManifest(name=name, id=item.stem.lower())
                entry_point = str(item)

            if manifest is not None:
                discovered.append(
                    DiscoveredPlugin(
                        id=manifest.id,
                        name=manifest.name,
                        path=item,
                        manifest=manifest,
                        is_builtin=is_builtin,
                        entry_point=entry_point,
                    )
                )

        return discovered

    def discover_package(self, package_name: str) -> list[str]:
        """
        Discover plugin module names within a Python package.
        """
        try:
            imported = importlib.import_module(package_name)
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

    def discover_all(self) -> list[DiscoveredPlugin]:
        """
        Discover all plugins from builtin, local, and external directories.
        """
        results: dict[str, DiscoveredPlugin] = {}

        # 1. Builtins first
        for plugin in self.discover_builtin():
            results[plugin.id] = plugin

        # 2. Local plugins (can override or complement)
        for plugin in self.discover_local():
            results[plugin.id] = plugin

        # 3. External paths
        for path in self.search_paths:
            for plugin in self.discover_directory(path):
                results[plugin.id] = plugin

        return list(results.values())


__all__ = [
    "DiscoveredPlugin",
    "PluginDiscovery",
]
