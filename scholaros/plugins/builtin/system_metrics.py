"""
ScholarOS System Metrics Builtin Plugin.
"""

from __future__ import annotations

from scholaros.plugins.base import Plugin
from scholaros.plugins.manifest import PluginManifest


class SystemMetricsPlugin(Plugin):
    """
    Builtin plugin providing core system metrics.
    """

    manifest = PluginManifest(
        name="System Metrics",
        version="1.0.0",
        author="ScholarOS Core Team",
        description="Monitors and reports ScholarOS runtime metrics.",
        scholaros=">=1.0.0",
        license="Apache-2.0",
        id="system_metrics",
        permissions=["container"],
    )

    def __init__(self) -> None:
        super().__init__(self.manifest)
        self.is_active = False

    def initialize(self) -> None:
        self.is_active = False

    def start(self) -> None:
        self.is_active = True

    def stop(self) -> None:
        self.is_active = False

    def shutdown(self) -> None:
        self.is_active = False


__all__ = [
    "SystemMetricsPlugin",
]
