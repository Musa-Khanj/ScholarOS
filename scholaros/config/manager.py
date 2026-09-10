"""
ScholarOS Configuration Manager.

High-level configuration service coordinating sources, loading, and settings.
Designed to be exposed to and registered inside the application container.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scholaros.config.loader import ConfigLoader
from scholaros.config.model import AppConfig
from scholaros.config.settings import Settings
from scholaros.config.sources import (
    CliSource,
    ConfigurationSource,
    FileSource,
)


class ConfigManager:
    """
    High-level configuration service for ScholarOS.
    Coordinates configuration loading and provides access to typed models and immutable settings.
    """

    def __init__(self, loader: ConfigLoader | None = None) -> None:
        self._loader = loader or ConfigLoader()
        self._config = self._loader.load_config()
        self._settings = Settings.from_config(self._config)

    def load(self, path: Path | str | None = None, **overrides: Any) -> AppConfig:
        """
        Load configuration from an optional file path and overrides.
        """
        if path is not None:
            self._loader.add_source(FileSource(path, optional=True))
        if overrides:
            self._loader.add_source(CliSource(overrides))

        self._config = self._loader.load_config()
        self._settings = Settings.from_config(self._config)
        return self._config

    def add_source(self, source: ConfigurationSource) -> None:
        """Add an additional configuration source and refresh."""
        self._loader.add_source(source)
        self.reload()

    def reload(self) -> AppConfig:
        """Reload configuration from all registered sources."""
        self._config = self._loader.load_config()
        self._settings = Settings.from_config(self._config)
        return self._config

    @property
    def config(self) -> AppConfig:
        """Return the mutable typed configuration model."""
        return self._config

    @property
    def settings(self) -> Settings:
        """Return the immutable runtime settings snapshot."""
        return self._settings

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value by key or dotted attribute."""
        return self._settings.get(key, default)

    def to_settings(self) -> Settings:
        """Return an immutable settings snapshot."""
        return self._settings

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"app_name={self._config.app_name!r}, "
            f"env={self._config.environment!r})"
        )