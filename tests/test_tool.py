from scholaros.tools.manifest import ToolManifest
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


def create_tool() -> DummyTool:
    """
    Create a fresh DummyTool.
    """

    return DummyTool()


def test_manifest():

    tool = create_tool()

    assert tool.manifest.name == "dummy"
    assert tool.manifest.version == "1.0"
    assert tool.manifest.author == "ScholarOS"
    assert tool.manifest.description == "Dummy tool"
    assert tool.manifest.scholaros == "1.0"
    assert tool.manifest.license == "MIT"


def test_name_property():

    tool = create_tool()

    assert tool.name == "dummy"


def test_version_property():

    tool = create_tool()

    assert tool.version == "1.0"


def test_description_property():

    tool = create_tool()

    assert tool.description == "Dummy tool"


def test_execute():

    tool = create_tool()

    result = tool.execute()

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.output == "Executed"
    assert result.error is None


def test_enable():

    tool = create_tool()

    tool.enable()

    assert tool._enabled is True


def test_disable():

    tool = create_tool()

    tool.enable()
    tool.disable()

    assert tool._enabled is False


def test_result_defaults():

    result = ToolResult(
        success=True,
    )

    assert result.output is None
    assert result.error is None
    assert result.metadata == {}


def test_repr():

    tool = create_tool()

    assert repr(tool) == (
        "DummyTool("
        "name='dummy', "
        "version='1.0'"
        ")"
    )