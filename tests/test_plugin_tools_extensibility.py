"""
Tests for Milestone 10K - Tools & Plugin System Extensibility.

Validates:
- FunctionTool creation, execution, error handling, and enable/disable
- Extension and ExtensionManager extension-point routing and execution
- Plugin component contribution (Tools, Extensions, AIProviders, Services)
- PluginContext propagation with runtime managers
- PluginManager component registration on enable() and clean unregistration on disable()/unload()
- DefaultSandbox execute_safe error isolation
"""

from __future__ import annotations

from typing import Any
import pytest

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.manager import AIManager
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamChunk, StreamingIterator
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.extensions.extension import Extension
from scholaros.extensions.manager import ExtensionManager
from scholaros.plugins import (
    DefaultSandbox,
    Plugin,
    PluginContext,
    PluginManager,
    PluginManifest,
    PluginState,
)
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.tools import (
    FunctionTool,
    Tool,
    ToolManager,
    ToolResult,
)


# ---------------------------------------------------------------------------
# Test Helpers & Fixtures
# ---------------------------------------------------------------------------

class DummyAIProvider(AIProvider):
    """Test AI provider for plugin contributions."""

    def __init__(self, name: str = "mock_provider") -> None:
        super().__init__(name=name)

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=f"Echo from {self.name}: {request.prompt}",
            model=request.model or "mock-model",
        )

    async def generate_async(self, request: AIRequest) -> AIResponse:
        return self.generate(request)

    def stream(self, request: AIRequest) -> StreamingIterator:
        chunk = StreamChunk(delta=f"Echo from {self.name}: {request.prompt}")
        return StreamingIterator(iter([chunk]))

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3]],
            model=request.model or "test-model",
            dimensions=3,
        )

    def health(self) -> ServiceHealth:
        return ServiceHealth(service_name=self.name, status=HealthStatus.HEALTHY, details="OK")


class DummyExtension(Extension):
    """Test extension for plugin contributions."""

    def __init__(self, name: str = "test_ext", point: str = "analytics") -> None:
        self._name = name
        self._point = point
        self._enabled = True
        self.invocations: list[tuple[Any, ...]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"Dummy extension {self._name}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def extension_point(self) -> str:
        return self._point

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        self.invocations.append((args, kwargs))
        return f"result_from_{self._name}"


class DummyService:
    """Sample service registered by plugin."""

    def __init__(self) -> None:
        self.active = True


class RichExtensibilityPlugin(Plugin):
    """Plugin that contributes tools, extensions, providers, and services."""

    def __init__(self, plugin_id: str = "rich_plugin") -> None:
        manifest = PluginManifest(
            name=plugin_id,
            version="1.0.0",
            author="ScholarOS",
            description="Extensibility test plugin",
            tools=["add_numbers"],
            services=["DummyService"],
            providers=["mock_provider"],
            extensions=["test_ext"],
        )
        super().__init__(manifest)

        self.loaded_context: PluginContext | None = None
        self.enabled_context: PluginContext | None = None
        self.disabled_context: PluginContext | None = None
        self.unloaded_context: PluginContext | None = None

        self._tool = FunctionTool.from_function(
            func=lambda a, b: a + b,
            name="add_numbers",
            description="Adds two numbers.",
        )
        self._extension = DummyExtension(name="test_ext", point="research_pipeline")
        self._provider = DummyAIProvider(name="mock_provider")
        self._service = DummyService()

    def on_load(self, context: PluginContext) -> None:
        self.loaded_context = context

    def on_enable(self, context: PluginContext) -> None:
        self.enabled_context = context

    def on_disable(self, context: PluginContext) -> None:
        self.disabled_context = context

    def on_unload(self, context: PluginContext) -> None:
        self.unloaded_context = context

    def get_tools(self) -> list[Tool]:
        return [self._tool]

    def get_extensions(self) -> list[Extension]:
        return [self._extension]

    def get_providers(self) -> list[AIProvider]:
        return [self._provider]

    def get_services(self) -> list[Any]:
        return [self._service]


class CrashingPlugin(Plugin):
    """Plugin that raises exceptions in lifecycle hooks and get_tools."""

    def __init__(self) -> None:
        manifest = PluginManifest(
            name="crashing_plugin",
            version="1.0.0",
            author="Chaos",
            description="Intentionally crashes",
        )
        super().__init__(manifest)

    def on_load(self, context: PluginContext) -> None:
        raise RuntimeError("Load explosion!")

    def on_enable(self, context: PluginContext) -> None:
        raise ValueError("Enable explosion!")

    def get_tools(self) -> list[Tool]:
        raise KeyError("Tools missing!")


# ---------------------------------------------------------------------------
# 1. FunctionTool Tests
# ---------------------------------------------------------------------------

def test_function_tool_execution():
    """Verify FunctionTool executes functions and wraps result in ToolResult."""
    def multiply(x: int, y: int) -> int:
        """Multiplies x by y."""
        return x * y

    tool = FunctionTool.from_function(multiply)
    assert tool.name == "multiply"
    assert "Multiplies x by y" in tool.manifest.description
    assert tool.is_enabled is True

    # Execution
    res = tool.execute(3, 4)
    assert isinstance(res, ToolResult)
    assert res.success is True
    assert res.output == 12
    assert res.error is None


def test_function_tool_error_handling():
    """Verify FunctionTool catches exceptions and returns error ToolResult."""
    def fail_fn(a: int) -> float:
        return a / 0

    tool = FunctionTool.from_function(fail_fn, name="divider")
    res = tool.execute(10)
    assert res.success is False
    assert res.error is not None
    assert "division by zero" in str(res.error).lower()


def test_function_tool_enable_disable():
    """Verify enable and disable state on FunctionTool."""
    tool = FunctionTool(func=lambda: "hello", name="greeter")
    assert tool.is_enabled is True

    tool.disable()
    assert tool.is_enabled is False

    # Executing disabled tool via ToolManager returns disabled error
    tm = ToolManager()
    tm.register(tool)
    res = tm.execute("greeter")
    assert res.success is False
    assert "disabled" in str(res.error).lower()

    # Re-enable
    tm.enable("greeter")
    assert tool.is_enabled is True
    res2 = tm.execute("greeter")
    assert res2.success is True
    assert res2.output == "hello"


def test_tool_manager_list_and_get():
    """Verify listing and retrieval in ToolManager."""
    tm = ToolManager()
    t1 = FunctionTool(func=lambda: 1, name="tool1")
    t2 = FunctionTool(func=lambda: 2, name="tool2")
    tm.register(t1)
    tm.register(t2)

    t2.disable()
    assert len(tm.list_tools(enabled_only=False)) == 2
    assert len(tm.list_tools(enabled_only=True)) == 1
    assert tm.get_tool("tool1") is t1
    assert tm.get_tool("nonexistent") is None


# ---------------------------------------------------------------------------
# 2. Extension & ExtensionManager Tests
# ---------------------------------------------------------------------------

def test_extension_manager_lifecycle_and_execution():
    """Verify ExtensionManager registers, queries by extension point, and executes extensions."""
    em = ExtensionManager()
    ext1 = DummyExtension(name="ext_a", point="rag_prefilter")
    ext2 = DummyExtension(name="ext_b", point="rag_prefilter")
    ext3 = DummyExtension(name="ext_c", point="agent_postprocess")

    em.register(ext1)
    em.register(ext2)
    em.register(ext3)

    # Query by extension point
    rag_exts = em.get_by_extension_point("rag_prefilter")
    assert len(rag_exts) == 2
    assert {e.name for e in rag_exts} == {"ext_a", "ext_b"}

    # Execute extension
    result = em.execute("ext_a", "arg1", key="value")
    assert result == "result_from_ext_a"
    assert len(ext1.invocations) == 1

    # Disable extension
    em.disable("ext_a")
    assert ext1.enabled is False
    assert len(em.get_by_extension_point("rag_prefilter", enabled_only=True)) == 1

    with pytest.raises(RuntimeError, match="disabled"):
        em.execute("ext_a")


# ---------------------------------------------------------------------------
# 3. Full Plugin Extensibility & Manager Integration Tests
# ---------------------------------------------------------------------------

def test_plugin_component_registration_and_lifecycle():
    """
    Verify PluginManager correctly registers contributed tools, extensions,
    providers, and services on enable(), and cleanly unregisters them on disable().
    """
    container = Container()
    event_bus = EventBus()
    tool_manager = ToolManager()
    extension_manager = ExtensionManager()
    ai_manager = AIManager(event_bus=event_bus)

    pm = PluginManager(
        container=container,
        event_bus=event_bus,
        tool_manager=tool_manager,
        extension_manager=extension_manager,
        ai_manager=ai_manager,
    )

    plugin = RichExtensibilityPlugin("rich_ext")

    # 1. Load phase
    loaded = pm.load(plugin)
    assert loaded.id == "rich_ext"
    assert pm.state("rich_ext") == PluginState.LOADED
    assert plugin.loaded_context is not None
    assert plugin.loaded_context.tool_manager is tool_manager
    assert plugin.loaded_context.extension_manager is extension_manager
    assert plugin.loaded_context.ai_manager is ai_manager

    # At LOADED phase, contributions are NOT yet registered
    assert tool_manager.get_tool("add_numbers") is None
    assert extension_manager.get_optional("test_ext") is None
    assert not ai_manager.registry.contains("mock_provider")

    # 2. Enable phase
    pm.enable("rich_ext")
    assert pm.state("rich_ext") == PluginState.STARTED
    assert plugin.enabled_context is not None

    # Verify contributions are registered in their target subsystems
    assert tool_manager.get_tool("add_numbers") is not None
    assert tool_manager.execute("add_numbers", 10, 20).output == 30

    assert extension_manager.get("test_ext") is not None
    assert extension_manager.execute("test_ext") == "result_from_test_ext"

    assert ai_manager.registry.contains("mock_provider")
    resp = ai_manager.select_provider(requested_provider="mock_provider").generate(
        AIRequest(prompt="hello")
    )
    assert "Echo from mock_provider" in resp.content

    assert container.registry.contains(DummyService)
    assert isinstance(container.resolve(DummyService), DummyService)

    # Verify query methods on PluginManager
    assert len(pm.get_plugin_tools("rich_ext")) == 1
    assert len(pm.get_plugin_extensions("rich_ext")) == 1
    assert len(pm.get_plugin_providers("rich_ext")) == 1
    assert len(pm.get_plugin_services("rich_ext")) == 1

    # 3. Disable phase
    pm.disable("rich_ext")
    assert pm.state("rich_ext") == PluginState.STOPPED
    assert plugin.disabled_context is not None

    # Contributions should be cleanly removed from subsystems
    assert tool_manager.get_tool("add_numbers") is None
    assert extension_manager.get_optional("test_ext") is None
    assert not ai_manager.registry.contains("mock_provider")
    assert not container.registry.contains(DummyService)

    # Tracking lists in PluginManager should be cleared
    assert len(pm.get_plugin_tools("rich_ext")) == 0
    assert len(pm.get_plugin_extensions("rich_ext")) == 0

    # 4. Unload phase
    pm.unload("rich_ext")
    assert pm.state("rich_ext") == PluginState.UNLOADED
    assert plugin.unloaded_context is not None
    assert "rich_ext" not in pm.installed()


def test_sandbox_error_isolation():
    """Verify PluginSandbox execute_safe catches exceptions and logs errors without crashing."""
    sandbox = DefaultSandbox()
    assert sandbox.error_count == 0

    def bad_function(val: int) -> int:
        if val < 0:
            raise ValueError("Negative number")
        return val * 2

    # Normal safe execution
    res, err = sandbox.execute_safe(bad_function, 5)
    assert res == 10
    assert err is None
    assert sandbox.error_count == 0

    # Failing safe execution
    res, err = sandbox.execute_safe(bad_function, -1, default=999)
    assert res == 999
    assert isinstance(err, ValueError)
    assert sandbox.error_count == 1
    assert sandbox.last_error is err
    assert len(sandbox.errors) == 1

    sandbox.clear_errors()
    assert sandbox.error_count == 0


def test_crashing_plugin_resilience():
    """
    Verify PluginManager safely handles a crashing plugin during on_load and enable
    without blowing up or corrupting manager state.
    """
    tm = ToolManager()
    pm = PluginManager(tool_manager=tm)
    plugin = CrashingPlugin()

    # Load should safely execute on_load via execute_safe
    pm.load(plugin)
    assert pm.state("crashing_plugin") == PluginState.LOADED

    # Enable should safely handle get_tools and on_enable errors
    pm.enable("crashing_plugin")
    assert pm.state("crashing_plugin") == PluginState.STARTED
    # Tool was not registered because get_tools raised an error
    assert len(tm.list_tools()) == 0

    # Clean unload
    pm.unload("crashing_plugin")
    assert pm.state("crashing_plugin") == PluginState.UNLOADED
