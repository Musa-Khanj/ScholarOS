"""
Tests for Part 8 - Plugins & Settings UX.

Validates:
1. Plugins View:
   - Registered plugins listing from PluginManager (Treeview and log text)
   - Metadata, capabilities, permissions, and sandbox policy inspection
   - Lifecycle operations: enable, disable, and discover (synchronous & asynchronous)
   - Status tracking and error surfacing
2. Settings View:
   - Configuration display and synchronization with ConfigManager
   - Secret masking and show/hide toggle for API keys
   - Input validation before saving
   - Synchronous and asynchronous configuration persistence
   - Diagnostics separating Application Connectivity, Configuration Validity,
     Provider Availability, and Provider/Model Health
   - Provider switching integration
3. End-to-end integration with bootstrap_runtime().
"""

from __future__ import annotations

import tempfile
import tkinter as tk
from pathlib import Path
from typing import Any

import pytest

from scholaros.ai.manager import AIManager
from scholaros.ai.providers.mock import MockProvider
from scholaros.bootstrap.runtime import bootstrap_runtime
from scholaros.config.manager import ConfigManager
from scholaros.gui.application import GUIApplication
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.views.workspace_views import PluginsView, SettingsView
from scholaros.gui.window import GUIWindow
from scholaros.plugins.base import Plugin
from scholaros.plugins.lifecycle import PluginState
from scholaros.plugins.manager import PluginManager
from scholaros.plugins.metadata import PluginMetadata

# ---------------------------------------------------------------------------
# Test Fixtures & Dummy Subsystems
# ---------------------------------------------------------------------------


class DummyCustomPlugin(Plugin):
    def __init__(self, plugin_id: str = "custom_tool_plugin") -> None:
        super().__init__(
            PluginMetadata(
                id=plugin_id,
                name="Custom Tool Plugin",
                version="2.1.0",
                author="ScholarOS Core Team",
                description="Provides computational mathematics and analysis tools.",
                permissions=("filesystem", "network"),
                extra={"capabilities": ["tools", "analysis"], "tags": ["math", "tools"]},
            )
        )


_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    global _root
    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            _root = tk.Tk()
            _root.withdraw()
    return _root


@pytest.fixture
def test_root():
    return get_test_root()


@pytest.fixture
def test_env():
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
        cfg_path = tmp_path / "scholaros.json"

        # Initialize ConfigManager
        cfg_mgr = ConfigManager()
        cfg_mgr.save(path=cfg_path)

        # Initialize PluginManager
        plugin_mgr = PluginManager()
        plugin = DummyCustomPlugin()
        plugin_mgr.register(plugin)

        # Initialize AIManager with provider
        ai_mgr = AIManager()
        prov = MockProvider(name="ollama")
        ai_mgr.register_provider(prov)
        ai_mgr.default_provider = "ollama"

        yield {
            "config_manager": cfg_mgr,
            "plugin_manager": plugin_mgr,
            "ai_manager": ai_mgr,
            "config_path": cfg_path,
            "plugin": plugin,
        }


# ---------------------------------------------------------------------------
# 1. Plugins View UX Tests
# ---------------------------------------------------------------------------


def test_plugins_view_initial_listing(test_root, test_env):
    """Verify PluginsView displays registered plugins in tree and log text."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        plugin_manager=test_env["plugin_manager"],
    )
    app.startup()

    view = PluginsView(parent=test_root, application=app)
    plugins = view.refresh()

    assert len(plugins) == 1
    p = plugins[0]
    assert p["id"] == "custom_tool_plugin"
    assert p["name"] == "Custom Tool Plugin"
    assert p["version"] == "2.1.0"
    assert p["author"] == "ScholarOS Core Team"
    assert "tools" in p["capabilities"]
    assert "filesystem" in p["permissions"]

    # Verify backward-compatible log text contains expected details
    log_content = view._list_text.get("1.0", "end")
    assert "Custom Tool Plugin" in log_content
    assert "v2.1.0" in log_content
    assert "Status=LOADED" in log_content

    # Verify Treeview population
    children = view._plugin_tree.get_children()
    assert len(children) == 1
    item_vals = view._plugin_tree.item(children[0])["values"]
    assert item_vals[0] == "custom_tool_plugin"
    assert item_vals[1] == "Custom Tool Plugin"


def test_plugins_view_metadata_and_sandbox_inspection(test_root, test_env):
    """Verify selecting a plugin displays its full metadata and sandbox policy."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        plugin_manager=test_env["plugin_manager"],
    )
    app.startup()

    view = PluginsView(parent=test_root, application=app)

    # Select plugin in tree
    view._plugin_tree.selection_set("custom_tool_plugin")
    view._on_tree_select()

    assert view.selected_plugin_id == "custom_tool_plugin"
    meta_content = view._meta_display.get("1.0", "end")

    assert "Custom Tool Plugin" in meta_content
    assert "custom_tool_plugin" in meta_content
    assert "ScholarOS Core Team" in meta_content
    assert "filesystem, network" in meta_content
    assert "tools, analysis" in meta_content
    assert "DefaultSandbox Enforced" in meta_content


def test_plugins_view_lifecycle_enable_disable(test_root, test_env):
    """Verify enabling and disabling a plugin transitions state and updates UI."""
    plugin_mgr: PluginManager = test_env["plugin_manager"]
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        plugin_manager=plugin_mgr,
    )
    app.startup()

    view = PluginsView(parent=test_root, application=app)

    # Attempt enable without selection
    view.enable_selected_plugin()
    assert "No plugin selected" in view._status_label.cget("text")

    # Select and enable
    view._plugin_tree.selection_set("custom_tool_plugin")
    view._on_tree_select()
    view.enable_selected_plugin(async_op=False)

    assert plugin_mgr.state("custom_tool_plugin") == PluginState.STARTED
    assert "enabled" in view._status_label.cget("text").lower()
    log_content = view._list_text.get("1.0", "end")
    assert "Status=STARTED" in log_content

    # Disable
    view.disable_selected_plugin(async_op=False)
    assert plugin_mgr.state("custom_tool_plugin") == PluginState.STOPPED
    assert "disabled" in view._status_label.cget("text").lower()
    log_content_stopped = view._list_text.get("1.0", "end")
    assert "Status=STOPPED" in log_content_stopped


def test_plugins_view_discovery(test_root, test_env):
    """Verify discovering plugins delegates to PluginManager and updates status."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        plugin_manager=test_env["plugin_manager"],
    )
    app.startup()

    view = PluginsView(parent=test_root, application=app)
    discovered = view.discover_plugins(async_op=False)

    assert discovered is not None
    assert "Discovery completed" in view._status_label.cget("text")


def test_plugins_view_async_lifecycle(test_root, test_env):
    """Verify asynchronous enable and disable operations without freezing GUI."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        plugin_manager=test_env["plugin_manager"],
    )
    app.startup()

    view = PluginsView(parent=test_root, application=app)
    view._plugin_tree.selection_set("custom_tool_plugin")
    view._on_tree_select()

    done = False

    def _on_enable_done(_: Any = None) -> None:
        nonlocal done
        done = True
        test_root.quit()

    view.enable_selected_plugin(async_op=True, on_complete=_on_enable_done)

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert done is True
    assert test_env["plugin_manager"].state("custom_tool_plugin") == PluginState.STARTED
    assert "enabled" in view._status_label.cget("text").lower()


# ---------------------------------------------------------------------------
# 2. Settings View UX Tests
# ---------------------------------------------------------------------------


def test_settings_view_load_from_config(test_root, test_env):
    """Verify SettingsView populates all form controls from active ConfigManager."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
        ai_manager=test_env["ai_manager"],
    )
    app.startup()

    view = SettingsView(parent=test_root, application=app)
    view.load_from_config()

    assert view._provider_combo.get() == "ollama"
    assert view._base_url_entry.get().startswith("http")
    assert view._chat_model_entry.get() != ""
    assert view._research_model_entry.get() != ""
    assert view._rag_strategy_combo.get() in ("hybrid", "default", "semantic")
    assert int(view._rag_limit_entry.get()) > 0
    assert view._workspace_entry.get() != ""


def test_settings_view_secret_masking_toggle(test_root, test_env):
    """Verify API key secret is masked by default and toggles on checkbutton."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
    )
    view = SettingsView(parent=test_root, application=app)

    # Default: masked with "*"
    assert view._api_key_entry.cget("show") == "*"

    # Toggle to show secret
    view._show_key_var.set(True)
    view.toggle_key_visibility()
    assert view._api_key_entry.cget("show") == ""

    # Toggle back to hide secret
    view._show_key_var.set(False)
    view.toggle_key_visibility()
    assert view._api_key_entry.cget("show") == "*"


def test_settings_view_validation_rules(test_root, test_env):
    """Verify SettingsView validates form fields before persistence."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
    )
    view = SettingsView(parent=test_root, application=app)

    # 1. Invalid limit (negative)
    view._rag_limit_entry.delete(0, "end")
    view._rag_limit_entry.insert(0, "-10")
    assert view.validate_settings() is False
    assert "Validation error" in view._status_label.cget("text")

    # 2. Invalid limit (non-numeric)
    view._rag_limit_entry.delete(0, "end")
    view._rag_limit_entry.insert(0, "abc")
    assert view.validate_settings() is False

    # 3. Empty provider
    view._rag_limit_entry.delete(0, "end")
    view._rag_limit_entry.insert(0, "15")
    view._provider_combo.set("")
    assert view.validate_settings() is False
    assert "Provider cannot be empty" in view._status_label.cget("text")

    # 4. Valid inputs
    view._provider_combo.set("ollama")
    assert view.validate_settings() is True
    assert "valid" in view._status_label.cget("text").lower()


def test_settings_view_save_and_persist(test_root, test_env):
    """Verify saving settings updates ConfigManager and persists to file."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
    )
    app.startup()

    view = SettingsView(parent=test_root, application=app)

    # Modify form fields
    view._chat_model_entry.delete(0, "end")
    view._chat_model_entry.insert(0, "deepseek-r1:7b")

    view._rag_limit_entry.delete(0, "end")
    view._rag_limit_entry.insert(0, "25")

    updates = view.save_settings(async_op=False)
    assert updates is not None
    assert updates["models"]["default_chat_model"] == "deepseek-r1:7b"
    assert updates["rag"]["default_limit"] == 25

    # Verify persisted in ConfigManager
    cfg = app.get_config()
    assert cfg.models.default_chat_model == "deepseek-r1:7b"
    assert cfg.rag.default_limit == 25
    assert "successfully" in view._status_label.cget("text").lower()


def test_settings_view_async_save(test_root, test_env):
    """Verify asynchronous configuration update and save."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
    )
    app.startup()

    view = SettingsView(parent=test_root, application=app)
    view._chat_model_entry.delete(0, "end")
    view._chat_model_entry.insert(0, "llama3.3:70b")

    done = False

    def _on_save_done(_: Any = None) -> None:
        nonlocal done
        done = True
        test_root.quit()

    view.save_settings(async_op=True, on_complete=_on_save_done)

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert done is True
    assert app.get_config().models.default_chat_model == "llama3.3:70b"


def test_settings_view_diagnostics_separation(test_root, test_env):
    """Verify diagnostics clearly distinguishes connectivity, validity, availability, and health."""
    app = GUIApplication(
        window=GUIWindow(root=test_root),
        config_manager=test_env["config_manager"],
        ai_manager=test_env["ai_manager"],
        plugin_manager=test_env["plugin_manager"],
    )
    app.startup()

    view = SettingsView(parent=test_root, application=app)

    # Direct diagnostics check on application
    diag = app.get_diagnostics()
    assert diag["app_connected"] is True
    assert diag["config_valid"] is True
    assert "ollama" in diag["available_providers"]
    assert diag["active_provider"] == "ollama"
    assert diag["provider_healthy"] is True
    assert diag["provider_health_status"].upper() == "HEALTHY"

    # UI Refresh and rendering
    view.refresh()
    display_text = view._info_display.get("1.0", "end")

    # Layer 1: Application Connectivity
    assert "Runtime: Connected" in display_text
    # Layer 2: Configuration Validity
    assert "Config Validity: Valid" in display_text
    # Layer 3: Provider Availability
    assert "Available Providers: ollama" in display_text
    # Layer 4: Provider Health
    assert "Provider Health: HEALTHY" in display_text


def test_settings_view_apply_provider_switching(test_root, test_env):
    """Verify switching active provider updates application and refreshes telemetry."""
    ai_mgr: AIManager = test_env["ai_manager"]
    ai_mgr.register_provider(MockProvider(name="openai"))

    app = GUIApplication(
        window=GUIWindow(root=test_root),
        ai_manager=ai_mgr,
        config_manager=test_env["config_manager"],
    )
    app.startup()

    view = SettingsView(parent=test_root, application=app)
    view._provider_combo.set("openai")
    view.apply_provider()

    assert ai_mgr.default_provider == "openai"
    assert "openai" in view._info_display.get("1.0", "end").lower()


# ---------------------------------------------------------------------------
# 3. Full Production Integration via bootstrap_runtime()
# ---------------------------------------------------------------------------


def test_bootstrap_runtime_plugins_settings_integration(test_root, test_env):
    """Verify PluginsView and SettingsView fully function in bootstrapped production runtime."""
    runtime = bootstrap_runtime(config_path=test_env["config_path"])

    # Register a runtime plugin
    runtime.plugin_manager.register(DummyCustomPlugin("runtime_boost_plugin"))

    builder = GUIBuilder()
    integration = builder.build(services=runtime, container=runtime.container, root=test_root)
    integration.application.startup()

    window = integration.window

    # 1. Test PluginsView in production window
    window.show_plugins()
    plugins_view: PluginsView = window.plugins_view
    assert plugins_view is not None

    plugins = plugins_view.refresh()
    assert any(p["id"] == "runtime_boost_plugin" for p in plugins)

    plugins_view._plugin_tree.selection_set("runtime_boost_plugin")
    plugins_view._on_tree_select()
    plugins_view.enable_selected_plugin(async_op=False)

    assert runtime.plugin_manager.state("runtime_boost_plugin") == PluginState.STARTED
    assert "Status=STARTED" in plugins_view._list_text.get("1.0", "end")

    # 2. Test SettingsView in production window
    window.show_settings()
    settings_view: SettingsView = window.settings_view
    assert settings_view is not None

    diag = settings_view.run_diagnostics(async_op=False)
    assert diag is not None
    assert diag["app_connected"] is True
    assert diag["config_valid"] is True

    info_content = settings_view._info_display.get("1.0", "end")
    assert "Runtime: Connected" in info_content
    assert "Config Validity: Valid" in info_content
    assert "Application layer: Offline / Mock" not in info_content
