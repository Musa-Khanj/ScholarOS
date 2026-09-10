"""
ScholarOS Plugins Subsystem.

Provides dynamic plugin discovery, loading, dependency management,
lifecycle state tracking, security sandboxing, container registration,
and event publishing.
"""

from __future__ import annotations

from scholaros.plugins.base import Plugin
from scholaros.plugins.dependency import (
    DependencyGraph,
    DependencyResolver,
)
from scholaros.plugins.discovery import (
    DiscoveredPlugin,
    PluginDiscovery,
)
from scholaros.plugins.exceptions import (
    CircularDependencyError,
    DependencyError,
    InstallationError,
    ManifestError,
    PermissionError,
    PluginError,
    PluginLifecycleError,
    PluginLoadError,
    PluginNotFoundError,
)
from scholaros.plugins.installer import PluginInstaller
from scholaros.plugins.lifecycle import (
    LifecycleTracker,
    PluginState,
)
from scholaros.plugins.loader import PluginLoader
from scholaros.plugins.manager import (
    PluginDiscovered,
    PluginInstalled,
    PluginLoaded,
    PluginManager,
    PluginRemoved,
    PluginStarted,
    PluginStopped,
    PluginUnloaded,
)
from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.metadata import PluginMetadata
from scholaros.plugins.permissions import (
    Permission,
    PermissionManager,
)
from scholaros.plugins.registry import PluginRegistry
from scholaros.plugins.sandbox import (
    DefaultSandbox,
    PluginSandbox,
)
from scholaros.plugins.service import PluginService

__all__ = [
    "CircularDependencyError",
    "DefaultSandbox",
    "DependencyError",
    "DependencyGraph",
    "DependencyResolver",
    "DiscoveredPlugin",
    "InstallationError",
    "LifecycleTracker",
    "ManifestError",
    "Permission",
    "PermissionError",
    "PermissionManager",
    "Plugin",
    "PluginDiscovered",
    "PluginDiscovery",
    "PluginError",
    "PluginInstalled",
    "PluginInstaller",
    "PluginLifecycleError",
    "PluginLoadError",
    "PluginLoaded",
    "PluginLoader",
    "PluginManager",
    "PluginManifest",
    "PluginMetadata",
    "PluginNotFoundError",
    "PluginRegistry",
    "PluginRemoved",
    "PluginSandbox",
    "PluginService",
    "PluginStarted",
    "PluginState",
    "PluginStopped",
    "PluginUnloaded",
]