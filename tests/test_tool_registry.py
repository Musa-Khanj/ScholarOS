from scholaros.tools.manifest import ToolManifest
from scholaros.tools.registry import ToolRegistry
from scholaros.tools.result import ToolResult
from scholaros.tools.tool import Tool


class DummyTool(Tool):
    """
    Concrete implementation used for testing.
    """

    def __init__(self) -> None:

        self.manifest = ToolManifest(
            name="dummy",
            version="1.0",
            author="ScholarOS",
            description="Dummy tool",
            scholaros="1.0",
            license="MIT",
        )

    def execute(
        self,
        *args,
        **kwargs,
    ) -> ToolResult:

        return ToolResult(
            success=True,
        )

    def enable(
        self,
    ) -> None:

        pass

    def disable(
        self,
    ) -> None:

        pass


def create_registry() -> ToolRegistry:
    """
    Create a fresh ToolRegistry.
    """

    return ToolRegistry()


def create_tool() -> DummyTool:
    """
    Create a fresh DummyTool.
    """

    return DummyTool()


def test_add():

    registry = create_registry()
    tool = create_tool()

    registry.add(tool)

    assert registry.contains("dummy")


def test_get():

    registry = create_registry()
    tool = create_tool()

    registry.add(tool)

    assert registry.get("dummy") is tool


def test_remove():

    registry = create_registry()
    tool = create_tool()

    registry.add(tool)
    registry.remove("dummy")

    assert not registry.contains("dummy")


def test_names():

    registry = create_registry()

    registry.add(create_tool())

    assert registry.names() == ["dummy"]


def test_values():

    registry = create_registry()

    tool = create_tool()

    registry.add(tool)

    assert registry.values() == [tool]


def test_items():

    registry = create_registry()

    tool = create_tool()

    registry.add(tool)

    assert registry.items() == [
        ("dummy", tool),
    ]


def test_clear():

    registry = create_registry()

    registry.add(create_tool())
    registry.clear()

    assert registry.size == 0


def test_size():

    registry = create_registry()

    assert registry.size == 0

    registry.add(create_tool())

    assert registry.size == 1


def test_tools_property():

    registry = create_registry()

    registry.add(create_tool())

    assert "dummy" in registry.tools


def test_repr():

    registry = create_registry()

    assert repr(registry) == (
        "ToolRegistry(tools=0)"
    )