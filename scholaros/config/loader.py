"""
ScholarOS Configuration Loader.

Merges multiple configuration sources into a unified, typed configuration model.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scholaros.config.model import AppConfig
from scholaros.config.sources import (
    CliSource,
    ConfigurationSource,
    DefaultsSource,
    EnvironmentSource,
    FileSource,
)


def deep_merge(target: dict[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge dictionary source into target."""
    for key, value in source.items():
        if isinstance(value, Mapping) and key in target and isinstance(target[key], dict):
            target[key] = deep_merge(dict(target[key]), value)
        else:
            target[key] = value
    return target


class ConfigLoader:
    """
    Merges configuration sources in precedence order into an AppConfig.
    Order of precedence (later sources override earlier ones):
    1. Defaults
    2. File
    3. Environment variables
    4. CLI / manual overrides
    """

    def __init__(self, sources: list[ConfigurationSource] | None = None) -> None:
        self._sources: list[ConfigurationSource] = list(sources) if sources is not None else [
            DefaultsSource(),
            EnvironmentSource(),
        ]

    def add_source(self, source: ConfigurationSource) -> None:
        """Add a configuration source to the loader."""
        self._sources.append(source)

    @property
    def sources(self) -> list[ConfigurationSource]:
        """Return the registered configuration sources."""
        return list(self._sources)

    def load_merged_dict(self) -> dict[str, Any]:
        """Load and merge all registered sources into a combined dictionary."""
        result: dict[str, Any] = {}
        for source in self._sources:
            data = source.load()
            if data:
                deep_merge(result, data)
        return result

    def load_config(self) -> AppConfig:
        """Load all registered sources into a typed AppConfig."""
        merged = self.load_merged_dict()
        return AppConfig.from_dict(merged)

    @staticmethod
    def load(
        path: Path | str | None = None,
        sources: list[ConfigurationSource] | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> AppConfig:
        """
        Convenience factory to load configuration with defaults, optional file,
        environment variables, and optional overrides.
        """
        source_list: list[ConfigurationSource] = []
        if sources is not None:
            source_list.extend(sources)
        else:
            source_list.append(DefaultsSource())
            if path is not None:
                source_list.append(FileSource(path, optional=True))
            source_list.append(EnvironmentSource())
            if overrides:
                source_list.append(CliSource(overrides))

        loader = ConfigLoader(source_list)
        return loader.load_config()