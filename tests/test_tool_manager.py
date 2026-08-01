from scholaros.tools.manager import ToolManager
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

        self._enabled = False

    def execute(
        self,
        *args,
        **kwargs,
    ) -> ToolResult:
        """
        Execute the tool.
        """

        return ToolResult(
            success=True,
            output="Executed",
        )

    def enable(
        self,
    ) -> None:
        """
        Enable the tool.
        """

        self._enabled = True

    def disable(
        self,
    ) -> None:
        """
        Disable the tool.
        """

        self._enabled = False


def create_manager() -> ToolManager:
    """
    Create a fresh ToolManager.
    """

    return ToolManager(
        ToolRegistry(),
    )


def create_tool() -> DummyTool:
    """
    Create a fresh DummyTool.
    """

    return DummyTool()


def test_register():

    manager = create_manager()
    tool = create_tool()

    manager.register(tool)

    assert manager.contains("dummy")


def test_get():

    manager = create_manager()
    tool = create_tool()

    manager.register(tool)

    assert manager.get("dummy") is tool


def test_unregister():

    manager = create_manager()
    tool = create_tool()

    manager.register(tool)
    manager.unregister("dummy")

    assert not manager.contains("dummy")


def test_installed():

    manager = create_manager()

    manager.register(create_tool())

    assert manager.installed() == [
        "dummy",
    ]


def test_enable():

    manager = create_manager()
    tool = create_tool()

    manager.register(tool)
    manager.enable("dummy")

    assert tool._enabled is True


def test_disable():

    manager = create_manager()
    tool = create_tool()

    manager.register(tool)
    manager.enable("dummy")
    manager.disable("dummy")

    assert tool._enabled is False


def test_execute():

    manager = create_manager()

    manager.register(create_tool())

    result = manager.execute("dummy")

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.output == "Executed"


def test_clear():

    manager = create_manager()

    manager.register(create_tool())
    manager.clear()

    assert manager.installed() == []


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        ToolRegistry,
    )


def test_repr():

    manager = create_manager()

    assert repr(manager) == (
        "ToolManager(tools=0)"
    )