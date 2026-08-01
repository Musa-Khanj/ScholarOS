from scholaros.tools.loader import ToolLoader
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

        return ToolResult(
            success=True,
            output="Executed",
        )

    def enable(
        self,
    ) -> None:

        self._enabled = True

    def disable(
        self,
    ) -> None:

        self._enabled = False


def create_loader() -> ToolLoader:
    """
    Create a fresh ToolLoader.
    """

    manager = ToolManager(
        ToolRegistry(),
    )

    return ToolLoader(
        manager,
    )


def create_tool() -> DummyTool:
    """
    Create a fresh DummyTool.
    """

    return DummyTool()


def test_load():

    loader = create_loader()
    tool = create_tool()

    loader.load(tool)

    assert loader.manager.contains("dummy")


def test_unload():

    loader = create_loader()
    tool = create_tool()

    loader.load(tool)
    loader.unload("dummy")

    assert not loader.manager.contains("dummy")


def test_reload():

    loader = create_loader()
    tool = create_tool()

    loader.load(tool)
    loader.reload(tool)

    assert loader.manager.contains("dummy")


def test_discover():

    loader = create_loader()

    loader.load(create_tool())

    assert loader.discover() == [
        "dummy",
    ]


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        ToolManager,
    )


def test_repr():

    loader = create_loader()

    assert repr(loader) == (
        "ToolLoader(tools=0)"
    )