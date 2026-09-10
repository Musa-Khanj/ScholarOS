"""
ScholarOS Plugin Exceptions.

Defines all exceptions used across the ScholarOS plugin subsystem.
"""

from __future__ import annotations

from scholaros.core.exceptions import PluginError


class PluginLoadError(PluginError, LookupError):
    """Raised when a plugin fails to be imported or loaded."""


class ManifestError(PluginError):
    """Raised when a plugin manifest is invalid, corrupt, or missing required fields."""


class DependencyError(PluginError):
    """Raised when plugin dependencies cannot be satisfied."""


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected in the plugin graph."""


class PermissionError(PluginError):
    """Raised when a plugin violates or lacks required security permissions."""


class InstallationError(PluginError):
    """Raised when a plugin installation, update, or uninstallation fails."""


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin cannot be found in the registry or discovery paths."""


class PluginLifecycleError(PluginError):
    """Raised when an invalid plugin lifecycle transition is attempted."""


__all__ = [
    "CircularDependencyError",
    "DependencyError",
    "InstallationError",
    "ManifestError",
    "PermissionError",
    "PluginError",
    "PluginLifecycleError",
    "PluginLoadError",
    "PluginNotFoundError",
]
