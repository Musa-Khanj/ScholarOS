"""
ScholarOS Plugin Base.

Defines the abstract base interface for ScholarOS plugins.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.metadata import PluginMetadata

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager
    from scholaros.events.bus import EventBus
    from scholaros.extensions.manager import ExtensionManager
    from scholaros.tools.manager import ToolManager


@dataclass(slots=True)
class PluginContext:
    """
    Runtime execution context provided to plugins by PluginManager.
    """

    plugin_id: str
    container: Any | None = None
    event_bus: EventBus | None = None
    tool_manager: ToolManager | None = None
    extension_manager: ExtensionManager | None = None
    ai_manager: AIManager | None = None
    config: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Plugin(ABC):
    """
    Abstract base class for all ScholarOS plugins.

    Lifecycle interface:
    - initialize(): Initialize plugin state, load configuration, prepare resources.
    - start(): Start plugin workers, register background services, listen to events.
    - stop(): Gracefully halt active operations and pause services.
    - shutdown(): Teardown, flush buffers, release file handles and connections.
    """

    manifest: PluginManifest | None = None
    _metadata: PluginMetadata | None = None

    def __init__(self, metadata: PluginMetadata | PluginManifest | None = None) -> None:
        """
        Initialize the plugin with optional metadata or manifest.
        """
        if metadata is not None:
            if isinstance(metadata, PluginManifest):
                self.manifest = metadata
                self._metadata = PluginMetadata.from_manifest(metadata)
            elif isinstance(metadata, PluginMetadata):
                self._metadata = metadata
                self.manifest = metadata.to_manifest()
            else:
                raise TypeError(f"Expected PluginMetadata or PluginManifest, got {type(metadata).__name__}")
        elif self.manifest is not None:
            self._metadata = PluginMetadata.from_manifest(self.manifest)

    # ---------------------------------------------------------
    # Metadata & Manifest Access
    # ---------------------------------------------------------

    @property
    def metadata(self) -> PluginMetadata:
        """Return the typed metadata for this plugin."""
        if self._metadata is not None:
            return self._metadata

        if getattr(self, "manifest", None) is not None and isinstance(self.manifest, PluginManifest):
            self._metadata = PluginMetadata.from_manifest(self.manifest)
            return self._metadata

        # Fallback default metadata using class name
        name = self.__class__.__name__
        self._metadata = PluginMetadata(
            id=name.lower(),
            name=name,
            version="1.0.0",
            description=f"{name} plugin",
        )
        return self._metadata

    @metadata.setter
    def metadata(self, value: PluginMetadata | PluginManifest) -> None:
        if isinstance(value, PluginManifest):
            self.manifest = value
            self._metadata = PluginMetadata.from_manifest(value)
        elif isinstance(value, PluginMetadata):
            self._metadata = value
            self.manifest = value.to_manifest()
        else:
            raise TypeError(f"Expected PluginMetadata or PluginManifest, got {type(value).__name__}")

    @property
    def id(self) -> str:
        """Return the plugin unique identifier."""
        return self.metadata.id

    @property
    def name(self) -> str:
        """Return the human-readable plugin name."""
        return self.metadata.name

    @property
    def version(self) -> str:
        """Return the plugin version string."""
        return self.metadata.version

    # ---------------------------------------------------------
    # Lifecycle Hooks
    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Prepare resources, configuration, and dependencies before running.
        """

    def start(self) -> None:
        """
        Activate plugin services and background tasks.
        """

    def stop(self) -> None:
        """
        Deactivate plugin services, stopping background operations.
        """

    def shutdown(self) -> None:
        """
        Release all resources, close connections, and clean up.
        """

    # ---------------------------------------------------------
    # Extensibility Contribution Hooks
    # ---------------------------------------------------------

    def get_tools(self) -> list[Any]:
        """
        Return Tool instances provided by this plugin.
        These tools are automatically registered into ToolManager when enabled.
        """
        return []

    def get_services(self) -> list[tuple[type, Any] | Any]:
        """
        Return service bindings or instances provided by this plugin.
        """
        return []

    def get_providers(self) -> list[Any]:
        """
        Return AIProvider instances provided by this plugin.
        These providers are automatically registered into AIManager when enabled.
        """
        return []

    def get_extensions(self) -> list[Any]:
        """
        Return Extension instances provided by this plugin.
        These extensions are automatically registered into ExtensionManager when enabled.
        """
        return []

    # ---------------------------------------------------------
    # Contextual Lifecycle Hooks
    # ---------------------------------------------------------

    def on_load(self, context: PluginContext) -> None:
        """Called when the plugin is loaded into memory."""

    def on_enable(self, context: PluginContext) -> None:
        """Called when the plugin is enabled."""

    def on_disable(self, context: PluginContext) -> None:
        """Called when the plugin is disabled."""

    def on_unload(self, context: PluginContext) -> None:
        """Called when the plugin is unloaded."""

    # ---------------------------------------------------------
    # Backward Compatibility Hooks
    # ---------------------------------------------------------

    def install(self) -> None:
        """Legacy install hook."""

    def uninstall(self) -> None:
        """Legacy uninstall hook."""

    def enable(self) -> None:
        """Legacy enable hook - defaults to start()."""
        self.start()

    def disable(self) -> None:
        """Legacy disable hook - defaults to stop()."""
        self.stop()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, version={self.version!r})"


__all__ = [
    "Plugin",
    "PluginContext",
]
