"""
ScholarOS Plugin Manifest.

Represents the declarative specification of a plugin and provides
parsers to read manifests from dictionaries, JSON, and TOML files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any
import sys

from scholaros.plugins.exceptions import ManifestError

if sys.version_info >= (3, 11):
    import tomllib
else:
    tomllib = None  # type: ignore[assignment]


@dataclass(slots=True)
class PluginManifest:
    """
    Declarative specification of a ScholarOS plugin.

    Parameters
    ----------
    name:
        Human-readable name of the plugin.
    version:
        Semantic version string.
    author:
        Author or maintainer name/email.
    description:
        Short summary of plugin functionality.
    scholaros:
        Target ScholarOS compatibility constraint.
    license:
        License identifier (e.g. MIT, Apache-2.0).
    id:
        Unique identifier for the plugin. Defaults to name.
    entry_point:
        Import path or module:attribute pointing to the Plugin class or instance.
    dependencies:
        List of plugin IDs or package names required by this plugin.
    permissions:
        List of required system permissions (e.g. filesystem, network).
    """

    name: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    scholaros: str = ">=1.0.0"
    license: str = "MIT"
    id: str = ""
    entry_point: str | None = None
    dependencies: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    providers: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize attributes and ensure default identifier."""
        if not self.name or not self.name.strip():
            raise ManifestError("Plugin manifest 'name' must be a non-empty string.")

        if not self.id:
            self.id = self.name.strip().lower().replace(" ", "_")

        for attr in ("dependencies", "permissions", "tools", "services", "providers", "extensions", "tags"):
            val = getattr(self, attr)
            if isinstance(val, (tuple, set)):
                setattr(self, attr, list(val))
            elif not isinstance(val, list):
                setattr(self, attr, [str(val)] if val else [])

    def to_dict(self) -> dict[str, Any]:
        """Serialize manifest to a standard dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginManifest:
        """
        Create a PluginManifest from a dictionary.
        """
        if not isinstance(data, dict):
            raise ManifestError(f"Expected dict for manifest, got {type(data).__name__}.")

        name = data.get("name")
        if not name or not isinstance(name, str):
            raise ManifestError("Manifest missing required 'name' field.")

        def _to_list(val: Any) -> list[str]:
            if isinstance(val, (str, bytes)):
                return [str(val)]
            if isinstance(val, (list, tuple, set)):
                return [str(x) for x in val]
            return []

        return cls(
            name=name,
            version=str(data.get("version", "1.0.0")),
            author=str(data.get("author", "")),
            description=str(data.get("description", "")),
            scholaros=str(data.get("scholaros", ">=1.0.0")),
            license=str(data.get("license", "MIT")),
            id=str(data.get("id", "")),
            entry_point=data.get("entry_point"),
            dependencies=_to_list(data.get("dependencies")),
            permissions=_to_list(data.get("permissions")),
            tools=_to_list(data.get("tools")),
            services=_to_list(data.get("services")),
            providers=_to_list(data.get("providers")),
            extensions=_to_list(data.get("extensions")),
            tags=_to_list(data.get("tags")),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> PluginManifest:
        """
        Read and construct a PluginManifest from a file path (JSON, TOML, or YAML).
        """
        manifest_path = Path(path)
        if not manifest_path.is_file():
            raise ManifestError(f"Manifest file not found: {manifest_path}")

        try:
            content = manifest_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ManifestError(f"Failed to read manifest file {manifest_path}: {exc}") from exc

        suffix = manifest_path.suffix.lower()
        try:
            if suffix == ".json":
                data = json.loads(content)
            elif suffix in (".toml", ".tml"):
                if tomllib is not None:
                    data = tomllib.loads(content)
                else:
                    raise ManifestError("TOML support requires Python 3.11+ or tomllib.")
            elif suffix in (".yaml", ".yml"):
                try:
                    import yaml  # type: ignore[import-not-found]
                    data = yaml.safe_load(content)
                except ImportError:
                    data = json.loads(content)
            else:
                try:
                    data = json.loads(content)
                except Exception:
                    if tomllib is not None:
                        data = tomllib.loads(content)
                    else:
                        raise ManifestError(f"Unsupported manifest file extension: {suffix}")
        except Exception as exc:
            raise ManifestError(f"Failed to parse manifest at {manifest_path}: {exc}") from exc

        if not isinstance(data, dict):
            raise ManifestError(f"Manifest data in {manifest_path} must be a mapping/dict.")

        return cls.from_dict(data)


__all__ = [
    "PluginManifest",
]
