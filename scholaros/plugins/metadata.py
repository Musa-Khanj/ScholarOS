"""
ScholarOS Plugin Metadata.

Provides a typed, immutable metadata model for ScholarOS plugins.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from scholaros.plugins.manifest import PluginManifest


@dataclass(slots=True, frozen=True)
class PluginMetadata:
    """
    Typed, immutable metadata describing an installed or loaded plugin.
    """

    id: str
    name: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    entry_point: str | None = None
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    permissions: tuple[str, ...] = field(default_factory=tuple)
    scholaros: str = ">=1.0.0"
    license: str = "MIT"
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_manifest(cls, manifest: PluginManifest, extra: dict[str, Any] | None = None) -> PluginMetadata:
        """
        Build PluginMetadata from a PluginManifest instance.
        """
        return cls(
            id=manifest.id or manifest.name.strip().lower().replace(" ", "_"),
            name=manifest.name,
            version=manifest.version,
            author=manifest.author,
            description=manifest.description,
            entry_point=manifest.entry_point,
            dependencies=tuple(manifest.dependencies),
            permissions=tuple(manifest.permissions),
            scholaros=manifest.scholaros,
            license=manifest.license,
            extra=dict(extra or {}),
        )

    def to_manifest(self) -> PluginManifest:
        """
        Convert PluginMetadata back to a PluginManifest.
        """
        return PluginManifest(
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            scholaros=self.scholaros,
            license=self.license,
            id=self.id,
            entry_point=self.entry_point,
            dependencies=list(self.dependencies),
            permissions=list(self.permissions),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginMetadata:
        """
        Create PluginMetadata from a dictionary.
        """
        manifest = PluginManifest.from_dict(data)
        extra = {k: v for k, v in data.items() if k not in PluginManifest.__dataclass_fields__}
        return cls.from_manifest(manifest, extra=extra)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize metadata to dictionary.
        """
        res = asdict(self)
        res["dependencies"] = list(self.dependencies)
        res["permissions"] = list(self.permissions)
        return res


__all__ = [
    "PluginMetadata",
]
