"""
Tests for the expanded ScholarOS Plugin Subsystem.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import zipfile

import pytest

from scholaros.container.container import Container
from scholaros.core.container import ServiceContainer
from scholaros.events.bus import EventBus
from scholaros.events.event import Event
from scholaros.plugins import (
    CircularDependencyError,
    DefaultSandbox,
    DependencyError,
    DependencyGraph,
    DependencyResolver,
    DiscoveredPlugin,
    InstallationError,
    LifecycleTracker,
    ManifestError,
    Permission,
    PermissionError,
    PermissionManager,
    Plugin,
    PluginDiscovered,
    PluginDiscovery,
    PluginInstalled,
    PluginInstaller,
    PluginLifecycleError,
    PluginLoadError,
    PluginLoaded,
    PluginLoader,
    PluginManager,
    PluginManifest,
    PluginMetadata,
    PluginRegistry,
    PluginRemoved,
    PluginSandbox,
    PluginService,
    PluginStarted,
    PluginState,
    PluginStopped,
    PluginUnloaded,
)


# ---------------------------------------------------------------------
# Test Helper Plugins
# ---------------------------------------------------------------------

class SamplePlugin(Plugin):
    """Simple plugin implementation for testing."""

    def __init__(self, name: str = "sample", deps: list[str] | None = None, perms: list[str] | None = None) -> None:
        manifest = PluginManifest(
            name=name,
            version="1.2.0",
            author="Tester",
            description="Test Plugin",
            dependencies=deps or [],
            permissions=perms or [],
        )
        super().__init__(manifest)
        self.init_called = False
        self.start_called = False
        self.stop_called = False
        self.shutdown_called = False

    def initialize(self) -> None:
        self.init_called = True

    def start(self) -> None:
        self.start_called = True

    def stop(self) -> None:
        self.stop_called = True

    def shutdown(self) -> None:
        self.shutdown_called = True


# ---------------------------------------------------------------------
# 1. Manifest & Metadata Tests
# ---------------------------------------------------------------------

def test_manifest_creation_and_defaults():
    manifest = PluginManifest(name="alpha")
    assert manifest.name == "alpha"
    assert manifest.id == "alpha"
    assert manifest.version == "1.0.0"
    assert manifest.dependencies == []
    assert manifest.permissions == []

    # Invalid empty name
    with pytest.raises(ManifestError):
        PluginManifest(name="")


def test_manifest_from_dict():
    data = {
        "name": "Beta Plugin",
        "id": "beta_custom",
        "version": "2.0.0",
        "author": "ScholarOS Dev",
        "description": "Beta test plugin",
        "dependencies": ["alpha"],
        "permissions": ["network", "ai"],
    }
    manifest = PluginManifest.from_dict(data)
    assert manifest.id == "beta_custom"
    assert manifest.dependencies == ["alpha"]
    assert "network" in manifest.permissions
    assert manifest.to_dict()["name"] == "Beta Plugin"


def test_manifest_from_file_json(tmp_path: Path):
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        json.dumps({
            "name": "File Plugin",
            "version": "1.0.0",
            "permissions": ["filesystem"],
        }),
        encoding="utf-8",
    )
    manifest = PluginManifest.from_file(manifest_file)
    assert manifest.name == "File Plugin"
    assert manifest.permissions == ["filesystem"]


def test_metadata_roundtrip():
    manifest = PluginManifest(
        name="Gamma",
        version="1.0.0",
        dependencies=["alpha"],
        permissions=["container"],
    )
    metadata = PluginMetadata.from_manifest(manifest, extra={"custom_field": 42})
    assert metadata.name == "Gamma"
    assert metadata.dependencies == ("alpha",)
    assert metadata.permissions == ("container",)
    assert metadata.extra["custom_field"] == 42

    reconstructed_manifest = metadata.to_manifest()
    assert reconstructed_manifest.name == manifest.name
    assert reconstructed_manifest.dependencies == ["alpha"]


# ---------------------------------------------------------------------
# 2. Lifecycle Tracker Tests
# ---------------------------------------------------------------------

def test_lifecycle_transitions():
    tracker = LifecycleTracker()
    plugin_id = "test_plugin"

    assert tracker.get_state(plugin_id) == PluginState.UNLOADED

    # DISCOVERED
    tracker.register_discovered(plugin_id)
    assert tracker.get_state(plugin_id) == PluginState.DISCOVERED

    # LOADED
    tracker.transition_to(plugin_id, PluginState.LOADED)
    assert tracker.get_state(plugin_id) == PluginState.LOADED

    # INITIALIZED
    tracker.transition_to(plugin_id, PluginState.INITIALIZED)
    assert tracker.get_state(plugin_id) == PluginState.INITIALIZED

    # STARTED
    tracker.transition_to(plugin_id, PluginState.STARTED)
    assert tracker.is_active(plugin_id)

    # STOPPED
    tracker.transition_to(plugin_id, PluginState.STOPPED)
    assert not tracker.is_active(plugin_id)

    # Restart (STOPPED -> STARTED)
    tracker.transition_to(plugin_id, PluginState.STARTED)
    assert tracker.is_active(plugin_id)

    # STOPPED -> UNLOADED
    tracker.transition_to(plugin_id, PluginState.STOPPED)
    tracker.transition_to(plugin_id, PluginState.UNLOADED)
    assert tracker.get_state(plugin_id) == PluginState.UNLOADED


def test_lifecycle_invalid_transition():
    tracker = LifecycleTracker()
    plugin_id = "test_plugin"

    tracker.register_discovered(plugin_id)
    # Direct DISCOVERED -> STARTED is not allowed
    with pytest.raises(PluginLifecycleError):
        tracker.transition_to(plugin_id, PluginState.STARTED)


# ---------------------------------------------------------------------
# 3. Dependency Graph & Resolution Tests
# ---------------------------------------------------------------------

def test_dependency_resolution_order():
    resolver = DependencyResolver()
    plugins = {
        "core": [],
        "auth": ["core"],
        "api": ["core", "auth"],
        "analytics": ["api"],
    }
    order = resolver.resolve(plugins)
    assert order.index("core") < order.index("auth")
    assert order.index("auth") < order.index("api")
    assert order.index("api") < order.index("analytics")

    # Reverse shutdown order
    shutdown_order = resolver.graph.resolve_shutdown_order()
    assert shutdown_order == list(reversed(order))


def test_circular_dependency_detection():
    graph = DependencyGraph()
    graph.add_plugin("a", ["b"])
    graph.add_plugin("b", ["c"])
    graph.add_plugin("c", ["a"])

    with pytest.raises(CircularDependencyError):
        graph.resolve_order()


def test_self_dependency_detection():
    graph = DependencyGraph()
    with pytest.raises(CircularDependencyError):
        graph.add_plugin("self_dep", ["self_dep"])


def test_missing_dependency():
    graph = DependencyGraph()
    graph.add_plugin("app", ["non_existent"])
    with pytest.raises(DependencyError):
        graph.validate_dependencies(["app"])


# ---------------------------------------------------------------------
# 4. Permissions Tests
# ---------------------------------------------------------------------

def test_permissions_manager():
    pm = PermissionManager(default_allow=False)
    plugin_id = "ai_agent"

    # Initially not allowed
    assert not pm.has_permission(plugin_id, Permission.AI)
    with pytest.raises(PermissionError):
        pm.check(plugin_id, Permission.AI)

    # Grant AI permission
    pm.grant(plugin_id, [Permission.AI, Permission.NETWORK])
    assert pm.has_permission(plugin_id, Permission.AI)
    assert pm.has_permission(plugin_id, "network")
    assert not pm.has_permission(plugin_id, Permission.FILESYSTEM)

    # Validate plugin permissions
    pm.validate_plugin(plugin_id, [Permission.AI])
    with pytest.raises(PermissionError):
        pm.validate_plugin(plugin_id, [Permission.FILESYSTEM])

    # Revoke
    pm.revoke(plugin_id, [Permission.AI])
    assert not pm.has_permission(plugin_id, Permission.AI)


# ---------------------------------------------------------------------
# 5. Sandbox Tests
# ---------------------------------------------------------------------

def test_default_sandbox():
    pm = PermissionManager(default_allow=False)
    pm.grant("sandbox_test", [Permission.RESEARCH])

    sandbox = DefaultSandbox(plugin_id="sandbox_test", permission_manager=pm)
    assert sandbox.is_allowed("research")
    assert not sandbox.is_allowed("filesystem")

    result = sandbox.execute(lambda x, y: x + y, 5, 10)
    assert result == 15


# ---------------------------------------------------------------------
# 6. Discovery Tests
# ---------------------------------------------------------------------

def test_discover_builtin():
    discovery = PluginDiscovery()
    builtins = discovery.discover_builtin()
    assert isinstance(builtins, list)
    # Check that system_metrics builtin plugin is discovered
    ids = [b.id for b in builtins]
    assert "system_metrics" in ids


def test_discover_directory(tmp_path: Path):
    # Create mock plugin folder with manifest
    plugin_dir = tmp_path / "custom_tool"
    plugin_dir.mkdir()
    (plugin_dir / "manifest.json").write_text(
        json.dumps({"name": "Custom Tool", "id": "custom_tool"}),
        encoding="utf-8",
    )

    discovery = PluginDiscovery()
    discovered = discovery.discover_directory(tmp_path)
    assert len(discovered) == 1
    assert discovered[0].id == "custom_tool"


# ---------------------------------------------------------------------
# 7. Installer Tests
# ---------------------------------------------------------------------

def test_installer_file_and_uninstall(tmp_path: Path):
    install_target = tmp_path / "installed_plugins"
    installer = PluginInstaller(target_dir=install_target)

    # Create dummy source plugin file
    src_file = tmp_path / "my_plugin.py"
    src_file.write_text("# dummy plugin", encoding="utf-8")

    meta = installer.install(src_file)
    assert meta.id == "my_plugin"
    assert installer.is_installed("my_plugin")

    # Uninstall
    removed = installer.uninstall("my_plugin")
    assert removed
    assert not installer.is_installed("my_plugin")


def test_installer_zip(tmp_path: Path):
    install_target = tmp_path / "installed_plugins"
    installer = PluginInstaller(target_dir=install_target)

    # Create zip source
    zip_path = tmp_path / "packaged_plugin.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("manifest.json", json.dumps({"name": "Packaged", "id": "packaged"}))
        z.writestr("__init__.py", "# package init")

    meta = installer.install(zip_path)
    assert meta.id == "packaged"
    assert installer.is_installed("packaged")


# ---------------------------------------------------------------------
# 8. PluginManager & EventBus Integration Tests
# ---------------------------------------------------------------------

def test_plugin_manager_lifecycle_and_events():
    event_bus = EventBus()
    events_received: list[Event] = []

    for evt_name in (
        "PluginDiscovered",
        "PluginLoaded",
        "PluginStarted",
        "PluginStopped",
        "PluginUnloaded",
    ):
        event_bus.subscribe(evt_name, lambda e: events_received.append(e))

    manager = PluginManager(event_bus=event_bus)

    # Discovery
    manager.discover()
    discovered_event_names = [e.name for e in events_received]
    assert "PluginDiscovered" in discovered_event_names

    # Load
    plugin = SamplePlugin("sample_test")
    manager.load(plugin)
    assert manager.contains("sample_test")
    assert manager.state("sample_test") == PluginState.LOADED
    assert any(e.name == "PluginLoaded" and e.payload.get("plugin_id") == "sample_test" for e in events_received)

    # Enable (INITIALIZE -> START)
    manager.enable("sample_test")
    assert plugin.init_called
    assert plugin.start_called
    assert manager.state("sample_test") == PluginState.STARTED
    assert any(e.name == "PluginStarted" for e in events_received)

    # Disable (STOP)
    manager.disable("sample_test")
    assert plugin.stop_called
    assert manager.state("sample_test") == PluginState.STOPPED
    assert any(e.name == "PluginStopped" for e in events_received)

    # Unload (UNLOAD)
    manager.unload("sample_test")
    assert plugin.shutdown_called
    assert not manager.contains("sample_test")
    assert any(e.name == "PluginUnloaded" for e in events_received)


def test_plugin_manager_batch_start_stop():
    manager = PluginManager()

    base_plugin = SamplePlugin("base_lib")
    app_plugin = SamplePlugin("app_lib", deps=["base_lib"])

    manager.load(base_plugin)
    manager.load(app_plugin)

    # Start all in dependency order
    manager.start_all()
    assert base_plugin.start_called
    assert app_plugin.start_called

    # Stop all
    manager.stop_all()
    assert base_plugin.stop_called
    assert app_plugin.stop_called


# ---------------------------------------------------------------------
# 9. PluginService & Container Integration Tests
# ---------------------------------------------------------------------

def test_plugin_service_container_registration():
    container = Container()
    manager = PluginManager()
    service = PluginService.configure_container(container, manager=manager)

    resolved_manager = container.resolve(PluginManager)
    assert resolved_manager is manager

    resolved_registry = container.resolve(PluginRegistry)
    assert resolved_registry is manager.registry

    resolved_service = container.resolve(PluginService)
    assert resolved_service is service


def test_plugin_service_core_container_registration():
    core_container = ServiceContainer()
    manager = PluginManager()
    service = PluginService.configure_container(core_container, manager=manager)

    assert core_container.resolve(PluginManager) is manager
    assert core_container.resolve(PluginService) is service


def test_plugin_service_lifecycle():
    manager = PluginManager()
    plugin = SamplePlugin("service_test")
    manager.load(plugin)

    service = PluginService(manager=manager)
    assert not service.is_running

    service.start()
    assert service.is_running
    assert plugin.start_called

    service.stop()
    assert not service.is_running
    assert plugin.stop_called
