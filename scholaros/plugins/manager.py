from __future__ import annotations

from scholaros.plugins.base import Plugin


class PluginManager:

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.manifest.name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> Plugin:
        return self._plugins[name]

    def installed(self) -> list[str]:
        return sorted(self._plugins)