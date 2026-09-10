"""
ScholarOS Built-in Plugin Service.

Provides plugin lifecycle management, sandboxed execution, and plugin hooks.
"""

from __future__ import annotations

from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service


class PluginService(Service):
    """Built-in Plugin Service."""

    def __init__(self, metadata: ServiceMetadata | None = None) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="PluginService",
                version="1.0.0",
                description="ScholarOS Built-in Plugin Service",
                capabilities=("plugin_loader", "plugin_sandbox", "extension_hooks"),
                tags=("plugin", "system"),
            )
        super().__init__(metadata=metadata)


__all__ = [
    "PluginService",
]
