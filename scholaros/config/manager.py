from __future__ import annotations

from pathlib import Path

from scholaros.config.loader import ConfigLoader
from scholaros.config.models import AppConfig


class ConfigManager:

    def __init__(self) -> None:
        self._config = AppConfig()

    def load(self, path: Path) -> None:
        self._config = ConfigLoader.load(path)

    @property
    def config(self) -> AppConfig:
        return self._config