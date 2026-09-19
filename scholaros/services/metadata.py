"""
ScholarOS Service Metadata.

Defines the metadata descriptor for services, including identity, versioning,
dependencies, tags, and capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ServiceMetadata:
    """
    Metadata describing a ScholarOS service.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "ScholarOS"
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Service name cannot be empty.")

        # Ensure dependencies and tags are tuples of strings
        if isinstance(self.dependencies, list):
            object.__setattr__(self, "dependencies", tuple(self.dependencies))
        if isinstance(self.tags, list):
            object.__setattr__(self, "tags", tuple(self.tags))
        if isinstance(self.capabilities, list):
            object.__setattr__(self, "capabilities", tuple(self.capabilities))

    def has_dependency(self, name: str) -> bool:
        """Return True if this service depends on the named service."""
        return name in self.dependencies

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to a serializable dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": list(self.dependencies),
            "tags": list(self.tags),
            "capabilities": list(self.capabilities),
            "extra": dict(self.extra),
        }


__all__ = [
    "ServiceMetadata",
]
