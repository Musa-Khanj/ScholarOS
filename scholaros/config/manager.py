"""
ScholarOS Configuration Manager.

High-level configuration service coordinating sources, loading, settings,
validation, dynamic updates, and file persistence (JSON & TOML).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import tomllib

from scholaros.config.loader import ConfigLoader, deep_merge
from scholaros.config.model import AppConfig
from scholaros.config.settings import Settings
from scholaros.config.sources import (
    CliSource,
    ConfigurationSource,
    FileSource,
)


def _format_toml_value(val: Any) -> str:
    """Format a single primitive value as a TOML token."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(val, list):
        items = [_format_toml_value(x) for x in val if not isinstance(x, dict)]
        return f"[{', '.join(items)}]"
    if val is None:
        return '""'
    return f'"{str(val)}"'


def _dict_to_toml(data: dict[str, Any], prefix: str = "") -> str:
    """Serialize a nested dictionary to standard TOML string format."""
    lines: list[str] = []
    tables: list[tuple[str, dict[str, Any]]] = []

    for k, v in data.items():
        if isinstance(v, dict):
            tables.append((k, v))
        else:
            lines.append(f"{k} = {_format_toml_value(v)}")

    for k, v in tables:
        section_name = f"{prefix}.{k}" if prefix else k
        lines.append("")
        lines.append(f"[{section_name}]")
        sub_content = _dict_to_toml(v, prefix=section_name)
        if sub_content.strip():
            lines.append(sub_content.strip())

    return "\n".join(lines).strip() + "\n"


class ConfigManager:
    """
    High-level configuration service for ScholarOS.
    Coordinates configuration loading, validation, dynamic updates, and persistence.
    """

    def __init__(self, loader: ConfigLoader | None = None) -> None:
        self._loader = loader or ConfigLoader()
        self._config = self._loader.load_config()
        self._settings = Settings.from_config(self._config)
        self._last_path: Path | None = None

    def load(self, path: Path | str | None = None, **overrides: Any) -> AppConfig:
        """
        Load configuration from an optional file path and overrides.
        """
        if path is not None:
            path_obj = Path(path)
            self._last_path = path_obj
            self._loader.add_source(FileSource(path_obj, optional=True))
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

    def validate(self) -> None:
        """Validate current configuration tree."""
        self._config.validate()

    def update(
        self,
        updates: dict[str, Any],
        validate: bool = True,
        persist: bool = False,
        persist_path: Path | str | None = None,
    ) -> AppConfig:
        """
        Merge updates into current configuration, validate, and optionally persist.
        """
        raw = self._config.to_dict(mask_secrets=False)
        merged = deep_merge(raw, updates)
        new_config = AppConfig.from_dict(merged)

        if validate:
            new_config.validate()

        self._config = new_config
        self._settings = Settings.from_config(self._config)

        if persist:
            self.save(path=persist_path)

        return self._config

    def save(
        self,
        path: Path | str | None = None,
        format: str | None = None,
        mask_secrets: bool = False,
    ) -> Path:
        """
        Persist current configuration to disk as JSON or TOML.
        """
        target = Path(path) if path is not None else (self._last_path or Path("configs/scholaros.json"))
        target.parent.mkdir(parents=True, exist_ok=True)

        # Detect format from extension if not specified
        resolved_format = format.lower() if format else (
            "toml" if target.suffix.lower() == ".toml" else "json"
        )

        data = self._config.to_dict(mask_secrets=mask_secrets)

        if resolved_format == "toml":
            toml_text = _dict_to_toml(data)
            # Verify TOML is valid
            tomllib.loads(toml_text)
            target.write_text(toml_text, encoding="utf-8")
        else:
            with target.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        self._last_path = target
        return target

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
