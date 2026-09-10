# ScholarOS Builtin Plugins

This directory contains standard builtin plugins bundled with the ScholarOS runtime.

## Structure

Builtin plugins can be defined as:
1. A standalone `.py` file containing a `Plugin` class.
2. A subdirectory containing a `manifest.json` (or `manifest.toml`) and `__init__.py` or `plugin.py`.

## Lifecycle

Builtin plugins are automatically scanned by `PluginDiscovery.discover_builtin()` and can be loaded, initialized, and enabled via `PluginManager`.
