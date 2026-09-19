"""
ScholarOS Plugin Manager.

Provides high-level orchestration for plugin discovery, validation,
loading, lifecycle management, installation, dependency resolution,
and container/event-bus/configuration integration.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

from scholaros.events.bus import EventBus
from scholaros.events.event import Event
from scholaros.plugins.base import Plugin, PluginContext
from scholaros.plugins.dependency import DependencyResolver

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager
    from scholaros.ai.provider import AIProvider
    from scholaros.extensions.extension import Extension
    from scholaros.extensions.manager import ExtensionManager
    from scholaros.tools.manager import ToolManager
    from scholaros.tools.tool import Tool
from scholaros.plugins.discovery import DiscoveredPlugin, PluginDiscovery
from scholaros.plugins.exceptions import ManifestError
from scholaros.plugins.installer import PluginInstaller
from scholaros.plugins.lifecycle import LifecycleTracker, PluginState
from scholaros.plugins.loader import PluginLoader
from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.metadata import PluginMetadata
from scholaros.plugins.permissions import PermissionManager
from scholaros.plugins.registry import PluginRegistry
from scholaros.plugins.sandbox import DefaultSandbox, PluginSandbox


# ---------------------------------------------------------------------
# Lifecycle Events
# ---------------------------------------------------------------------

class PluginDiscovered(Event):
    """Fired when a plugin is discovered in search paths."""

    def __init__(self, plugin_id: str, metadata: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(
            name="PluginDiscovered",
            payload={"plugin_id": plugin_id, "metadata": metadata or {}},
            **kwargs,
        )


class PluginLoaded(Event):
    """Fired when a plugin is loaded into memory."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginLoaded",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


class PluginStarted(Event):
    """Fired when a plugin has transitioned to STARTED / enabled."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginStarted",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


class PluginStopped(Event):
    """Fired when a plugin is stopped / disabled."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginStopped",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


class PluginUnloaded(Event):
    """Fired when a plugin is completely unloaded from the registry."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginUnloaded",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


class PluginInstalled(Event):
    """Fired when a plugin package has been successfully installed."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginInstalled",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


class PluginRemoved(Event):
    """Fired when a plugin package has been removed / uninstalled."""

    def __init__(self, plugin_id: str, **kwargs: Any) -> None:
        super().__init__(
            name="PluginRemoved",
            payload={"plugin_id": plugin_id},
            **kwargs,
        )


# ---------------------------------------------------------------------
# Plugin Manager Orchestrator
# ---------------------------------------------------------------------

class PluginManager:
    """
    High-level orchestration for ScholarOS plugins.

    Coordinates:
    - Discovery (builtins, local workspace, external paths)
    - Installation / Uninstallation / Updates
    - Validation and Dependency Resolution
    - Dynamic Module Loading
    - Lifecycle State Transitions
    - Sandbox Execution and Security Permissions
    - Integration with Container, EventBus, and Configuration
    """

    def __init__(
        self,
        container: Any | None = None,
        event_bus: EventBus | None = None,
        config: Any | None = None,
        registry: PluginRegistry | None = None,
        loader: PluginLoader | None = None,
        discovery: PluginDiscovery | None = None,
        installer: PluginInstaller | None = None,
        lifecycle: LifecycleTracker | None = None,
        dependency_resolver: DependencyResolver | None = None,
        permission_manager: PermissionManager | None = None,
        sandbox: PluginSandbox | None = None,
        tool_manager: ToolManager | None = None,
        extension_manager: ExtensionManager | None = None,
        ai_manager: AIManager | None = None,
    ) -> None:
        self.container = container
        self.event_bus = event_bus
        self.config = config
        self.tool_manager = tool_manager
        self.extension_manager = extension_manager
        self.ai_manager = ai_manager

        self._registry = registry or PluginRegistry()
        self._loader = loader or PluginLoader()
        self._discovery = discovery or PluginDiscovery()
        self._installer = installer or PluginInstaller()
        self._lifecycle = lifecycle or LifecycleTracker()
        self._dependencies = dependency_resolver or DependencyResolver()
        self._permissions = permission_manager or PermissionManager(default_allow=True)
        self._sandbox = sandbox or DefaultSandbox(permission_manager=self._permissions)

        # Track registered contributions per plugin
        self._plugin_tools: dict[str, list[Tool]] = {}
        self._plugin_extensions: dict[str, list[Extension]] = {}
        self._plugin_providers: dict[str, list[AIProvider]] = {}
        self._plugin_services: dict[str, list[type]] = {}

        # Apply configuration if provided
        if self.config is not None:
            self._apply_configuration(self.config)

    def _apply_configuration(self, config: Any) -> None:
        """Read plugin configuration settings."""
        # Check for plugin search paths
        extra_paths = getattr(config, "plugin_paths", None)
        if isinstance(extra_paths, (list, tuple)):
            for p in extra_paths:
                self._discovery.add_search_path(p)

    def _create_context(self, plugin_id: str) -> PluginContext:
        """Create a PluginContext instance for the specified plugin."""
        plugin = self._registry.get_optional(plugin_id)
        metadata_dict = plugin.metadata.to_dict() if plugin is not None else {}
        return PluginContext(
            plugin_id=plugin_id,
            container=self.container,
            event_bus=self.event_bus,
            tool_manager=self.tool_manager,
            extension_manager=self.extension_manager,
            ai_manager=self.ai_manager,
            config=self.config,
            metadata=metadata_dict,
        )

    def _register_contributions(self, plugin: Plugin) -> None:
        """Register tools, extensions, providers, and services contributed by a plugin."""
        plugin_id = plugin.id

        # 1. Tools
        tools, _ = self._sandbox.execute_safe(plugin.get_tools, default=[])
        if tools and self.tool_manager is not None:
            self._plugin_tools[plugin_id] = []
            for tool in tools:
                self.tool_manager.register(tool)
                self._plugin_tools[plugin_id].append(tool)

        # 2. Extensions
        extensions, _ = self._sandbox.execute_safe(plugin.get_extensions, default=[])
        if extensions and self.extension_manager is not None:
            self._plugin_extensions[plugin_id] = []
            for ext in extensions:
                self.extension_manager.register(ext)
                self._plugin_extensions[plugin_id].append(ext)

        # 3. AI Providers
        providers, _ = self._sandbox.execute_safe(plugin.get_providers, default=[])
        if providers and self.ai_manager is not None:
            self._plugin_providers[plugin_id] = []
            for prov in providers:
                self.ai_manager.register_provider(prov)
                self._plugin_providers[plugin_id].append(prov)

        # 4. Services
        services, _ = self._sandbox.execute_safe(plugin.get_services, default=[])
        if services and self.container is not None:
            self._plugin_services[plugin_id] = []
            for svc in services:
                if isinstance(svc, tuple) and len(svc) == 2:
                    iface, impl_or_inst = svc
                    if isinstance(impl_or_inst, type):
                        self.container.add_singleton(iface, impl_or_inst)
                    else:
                        self.container.add_instance(iface, impl_or_inst)
                    self._plugin_services[plugin_id].append(iface)
                elif isinstance(svc, type):
                    self.container.add_singleton(svc, svc)
                    self._plugin_services[plugin_id].append(svc)
                else:
                    svc_type = type(svc)
                    self.container.add_instance(svc_type, svc)
                    self._plugin_services[plugin_id].append(svc_type)

    def _unregister_contributions(self, plugin_id: str) -> None:
        """Unregister all contributions made by a plugin."""
        # 1. Tools
        tools = self._plugin_tools.pop(plugin_id, [])
        if self.tool_manager is not None:
            for tool in tools:
                try:
                    self.tool_manager.unregister(tool.name)
                except Exception:
                    pass

        # 2. Extensions
        extensions = self._plugin_extensions.pop(plugin_id, [])
        if self.extension_manager is not None:
            for ext in extensions:
                try:
                    self.extension_manager.unregister(ext.name)
                except Exception:
                    pass

        # 3. AI Providers
        providers = self._plugin_providers.pop(plugin_id, [])
        if self.ai_manager is not None:
            for prov in providers:
                try:
                    self.ai_manager.registry.unregister(prov.name)
                except Exception:
                    pass

        # 4. Services
        services = self._plugin_services.pop(plugin_id, [])
        if self.container is not None and hasattr(self.container, "registry"):
            for svc_iface in services:
                try:
                    self.container.registry.unregister(svc_iface)
                except Exception:
                    pass

    def get_plugin_tools(self, plugin_id: str) -> list[Tool]:
        """Return tools registered by the given plugin."""
        return list(self._plugin_tools.get(plugin_id, []))

    def get_plugin_extensions(self, plugin_id: str) -> list[Extension]:
        """Return extensions registered by the given plugin."""
        return list(self._plugin_extensions.get(plugin_id, []))

    def get_plugin_providers(self, plugin_id: str) -> list[AIProvider]:
        """Return AI providers registered by the given plugin."""
        return list(self._plugin_providers.get(plugin_id, []))

    def get_plugin_services(self, plugin_id: str) -> list[type]:
        """Return service types registered by the given plugin."""
        return list(self._plugin_services.get(plugin_id, []))

    def _emit(self, event: Event) -> None:
        """Publish an event to the EventBus if available."""
        if self.event_bus is not None:
            self.event_bus.publish(event)

    # ---------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------

    def discover(self, paths: Iterable[str | Path] | None = None) -> list[DiscoveredPlugin]:
        """
        Discover plugins in builtin, local, and optional extra paths.
        """
        if paths:
            for path_entry in paths:
                self._discovery.add_search_path(path_entry)

        discovered = self._discovery.discover_all()
        for plugin in discovered:
            self._lifecycle.register_discovered(plugin.id)
            self._emit(PluginDiscovered(plugin_id=plugin.id, metadata=plugin.manifest.to_dict()))

        return discovered


    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self, target: PluginManifest | PluginMetadata | Plugin) -> bool:
        """
        Validate plugin manifest or metadata structure.
        """
        if isinstance(target, Plugin):
            meta = target.metadata
        elif isinstance(target, PluginManifest):
            meta = PluginMetadata.from_manifest(target)
        elif isinstance(target, PluginMetadata):
            meta = target
        else:
            raise TypeError(f"Invalid target for validation: {type(target).__name__}")

        if not meta.name or not meta.name.strip():
            raise ManifestError("Plugin name is required.")

        if not meta.id or not meta.id.strip():
            raise ManifestError("Plugin id is required.")

        return True

    # ---------------------------------------------------------
    # Loading & Registration
    # ---------------------------------------------------------

    def load(self, source: str | Path | Plugin) -> Plugin:
        """
        Load a plugin from an instance, module name, or filesystem path.
        """
        if isinstance(source, Plugin):
            plugin = source
        else:
            plugin = self._loader.load(source)

        self.validate(plugin)

        # Validate security permissions
        self._permissions.validate_plugin(plugin.id, plugin.metadata.permissions)

        # Store in registry
        self._registry.add(plugin)

        # Register dependencies in dependency graph
        self._dependencies.add(plugin.id, plugin.metadata.dependencies)

        # Update lifecycle to LOADED
        self._lifecycle.transition_to(plugin.id, PluginState.LOADED)
        ctx = self._create_context(plugin.id)
        self._sandbox.execute_safe(plugin.on_load, ctx)
        self._emit(PluginLoaded(plugin_id=plugin.id))

        return plugin

    def register(self, plugin: Plugin) -> None:
        """
        Register an already instantiated plugin.
        """
        self.load(plugin)

    def unload(self, name_or_id: str) -> None:
        """
        Unload a plugin, stopping it if active, shutting it down, and unregistering.
        """
        plugin = self._registry.get_optional(name_or_id)
        if plugin is None:
            return

        plugin_id = plugin.id

        # Stop first if active
        if self._lifecycle.is_active(plugin_id):
            self.disable(plugin_id)
        else:
            self._unregister_contributions(plugin_id)

        ctx = self._create_context(plugin_id)
        self._sandbox.execute_safe(plugin.on_unload, ctx)

        # Teardown / shutdown
        plugin.shutdown()

        # Update lifecycle to UNLOADED
        self._lifecycle.transition_to(plugin_id, PluginState.UNLOADED)
        self._registry.remove(name_or_id)
        self._dependencies.graph.remove_plugin(plugin_id)

        self._emit(PluginUnloaded(plugin_id=plugin_id))

    def unregister(self, name_or_id: str) -> None:
        """Legacy alias for unload."""
        self.unload(name_or_id)

    # ---------------------------------------------------------
    # Lifecycle: Enable & Disable
    # ---------------------------------------------------------

    def enable(self, name_or_id: str) -> None:
        """
        Enable (initialize and start) a loaded plugin.
        """
        plugin = self._registry.get(name_or_id)
        plugin_id = plugin.id

        # Verify dependencies
        available = {p.id for p in self._registry.values()}
        self._dependencies.graph.validate_dependencies(available)

        # Initialize if not already initialized
        current_state = self._lifecycle.get_state(plugin_id)
        if current_state == PluginState.LOADED:
            self._lifecycle.transition_to(plugin_id, PluginState.INITIALIZED)
            self._sandbox.execute(plugin.initialize)

        # Register plugin contributions
        self._register_contributions(plugin)

        # Start plugin
        self._lifecycle.transition_to(plugin_id, PluginState.STARTED)
        ctx = self._create_context(plugin_id)
        self._sandbox.execute_safe(plugin.on_enable, ctx)
        self._sandbox.execute(plugin.start)
        plugin.enable()  # trigger legacy enable hook if defined

        self._emit(PluginStarted(plugin_id=plugin_id))

    def disable(self, name_or_id: str) -> None:
        """
        Disable (stop) a running plugin.
        """
        plugin = self._registry.get(name_or_id)
        plugin_id = plugin.id

        if not self._lifecycle.is_active(plugin_id):
            return

        ctx = self._create_context(plugin_id)
        self._sandbox.execute_safe(plugin.on_disable, ctx)

        self._lifecycle.transition_to(plugin_id, PluginState.STOPPED)
        self._sandbox.execute(plugin.stop)
        plugin.disable()  # trigger legacy disable hook if defined

        # Unregister contributions
        self._unregister_contributions(plugin_id)

        self._emit(PluginStopped(plugin_id=plugin_id))

    # ---------------------------------------------------------
    # Batch Lifecycle Management
    # ---------------------------------------------------------

    def start_all(self) -> None:
        """
        Start all loaded plugins in topological dependency order.
        """
        plugins_dict = {p.id: p.metadata.dependencies for p in self._registry.values()}
        order = self._dependencies.resolve(plugins_dict)

        for p_id in order:
            if not self._lifecycle.is_active(p_id):
                self.enable(p_id)

    def stop_all(self) -> None:
        """
        Stop all running plugins in reverse dependency order.
        """
        plugins_dict = {p.id: p.metadata.dependencies for p in self._registry.values()}
        self._dependencies.graph.clear()
        for p_id, deps in plugins_dict.items():
            self._dependencies.add(p_id, deps)
        shutdown_order = self._dependencies.graph.resolve_shutdown_order()

        for p_id in shutdown_order:
            if self._lifecycle.is_active(p_id):
                self.disable(p_id)

    # ---------------------------------------------------------
    # Installation & Uninstallation
    # ---------------------------------------------------------

    def install(self, source: str | Path) -> PluginMetadata:
        """
        Install a plugin package or file to the plugins directory.
        """
        meta = self._installer.install(source)
        self._emit(PluginInstalled(plugin_id=meta.id))
        return meta

    def uninstall(self, name_or_id: str) -> bool:
        """
        Uninstall a plugin from the filesystem and unload it.
        """
        plugin = self._registry.get_optional(name_or_id)
        target_id = plugin.id if plugin is not None else name_or_id

        self.unload(target_id)
        removed = self._installer.uninstall(target_id)
        if removed:
            self._emit(PluginRemoved(plugin_id=target_id))
        return removed

    # ---------------------------------------------------------
    # Inspection & Registry Forwarding
    # ---------------------------------------------------------

    def get(self, name_or_id: str) -> Plugin:
        """Return a registered plugin."""
        return self._registry.get(name_or_id)

    def contains(self, name_or_id: str) -> bool:
        """Return True if plugin is registered."""
        return self._registry.contains(name_or_id)

    def installed(self) -> list[str]:
        """Return names of all registered plugins."""
        return self._registry.names()

    def state(self, name_or_id: str) -> PluginState:
        """Return current lifecycle state of a plugin."""
        plugin = self._registry.get_optional(name_or_id)
        target_id = plugin.id if plugin is not None else name_or_id
        return self._lifecycle.get_state(target_id)

    def clear(self) -> None:
        """Unload and clear all plugins."""
        for name in list(self._registry.names()):
            self.unload(name)
        self._registry.clear()
        self._lifecycle.clear()
        self._plugin_tools.clear()
        self._plugin_extensions.clear()
        self._plugin_providers.clear()
        self._plugin_services.clear()

    @property
    def plugins(self) -> dict[str, Plugin]:
        """Return registered plugins dictionary."""
        return self._registry.plugins

    @property
    def registry(self) -> PluginRegistry:
        """Return the plugin registry."""
        return self._registry

    @property
    def loader(self) -> PluginLoader:
        """Return the plugin loader."""
        return self._loader

    @property
    def discovery(self) -> PluginDiscovery:
        """Return the discovery service."""
        return self._discovery

    @property
    def installer(self) -> PluginInstaller:
        """Return the plugin installer."""
        return self._installer

    @property
    def lifecycle(self) -> LifecycleTracker:
        """Return the lifecycle tracker."""
        return self._lifecycle

    @property
    def permissions(self) -> PermissionManager:
        """Return the permission manager."""
        return self._permissions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(plugins={len(self._registry)})"


__all__ = [
    "PluginDiscovered",
    "PluginInstalled",
    "PluginLoaded",
    "PluginManager",
    "PluginRemoved",
    "PluginStarted",
    "PluginStopped",
    "PluginUnloaded",
]
