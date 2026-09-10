"""
ScholarOS Configuration Sources.

Abstractions for configuration providers (defaults, files, environment, CLI overrides).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
import json
from pathlib import Path
from typing import Any
import tomllib

from scholaros.config.defaults import get_default_config_dict
from scholaros.config.environment import load_environment
from scholaros.config.exceptions import ConfigurationError


class ConfigSource(str, Enum):
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    COMMAND_LINE = "command-line"


class ConfigurationSource(ABC):
    """
    Abstract base class for configuration providers.
    """

    @property
    @abstractmethod
    def source_type(self) -> ConfigSource:
        """Return the source type classification."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable source name."""
        raise NotImplementedError

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Load and return configuration data dictionary."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, type={self.source_type.value!r})"


class DefaultsSource(ConfigurationSource):
    """Configuration provider supplying centralized application default values."""

    @property
    def source_type(self) -> ConfigSource:
        return ConfigSource.DEFAULT

    @property
    def name(self) -> str:
        return "defaults"

    def load(self) -> dict[str, Any]:
        return get_default_config_dict()


class FileSource(ConfigurationSource):
    """Configuration provider loading settings from TOML or JSON files."""

    def __init__(self, path: Path | str, optional: bool = True) -> None:
        self._path = Path(path)
        self._optional = optional

    @property
    def source_type(self) -> ConfigSource:
        return ConfigSource.FILE

    @property
    def name(self) -> str:
        return f"file:{self._path.name}"

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            if self._optional:
                return {}
            raise ConfigurationError(f"Configuration file not found: {self._path}")

        try:
            if self._path.suffix.lower() == ".json":
                with self._path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                with self._path.open("rb") as f:
                    data = tomllib.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as exc:
            if self._optional:
                return {}
            raise ConfigurationError(f"Failed to parse config file {self._path}: {exc}") from exc


class EnvironmentSource(ConfigurationSource):
    """Configuration provider loading prefixed variables from os.environ."""

    def __init__(self, prefix: str = "SCHOLAROS_") -> None:
        self._prefix = prefix

    @property
    def source_type(self) -> ConfigSource:
        return ConfigSource.ENVIRONMENT

    @property
    def name(self) -> str:
        return f"env:{self._prefix}"

    def load(self) -> dict[str, Any]:
        return load_environment(prefix=self._prefix)


class CliSource(ConfigurationSource):
    """Configuration provider for command-line arguments and runtime overrides."""

    def __init__(self, overrides: dict[str, Any] | None = None) -> None:
        self._overrides = overrides or {}

    @property
    def source_type(self) -> ConfigSource:
        return ConfigSource.COMMAND_LINE

    @property
    def name(self) -> str:
        return "cli-overrides"

    def load(self) -> dict[str, Any]:
        return dict(self._overrides)