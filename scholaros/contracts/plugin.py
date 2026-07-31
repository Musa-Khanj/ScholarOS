from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scholaros.plugins.manifest import PluginManifest


class Plugin(ABC):

    manifest: PluginManifest

    @abstractmethod
    def install(self) -> None:
        ...

    @abstractmethod
    def uninstall(self) -> None:
        ...

    @abstractmethod
    def enable(self) -> None:
        ...

    @abstractmethod
    def disable(self) -> None:
        ...