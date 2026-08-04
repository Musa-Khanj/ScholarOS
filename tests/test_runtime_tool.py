from unittest.mock import MagicMock

from scholaros.applications.manager import ApplicationManager
from scholaros.applications.registry import ApplicationRegistry
from scholaros.execution import Execution
from scholaros.memory import Memory
from scholaros.planner import Planner
from scholaros.plugins.manager import PluginManager
from scholaros.runtime import Runtime
from scholaros.tools.manager import ToolManager
from scholaros.tools.registry import ToolRegistry
from scholaros.workflow import Workflow


def create_runtime() -> Runtime:

    agent = MagicMock()

    agent.execute.return_value = "Runtime Complete"

    workflow = Workflow(
        agent,
    )

    execution = Execution(
        workflow,
    )

    planner = Planner(
        execution,
    )

    memory = Memory()

    plugins = PluginManager()

    tools = ToolManager(
        ToolRegistry(),
    )

    applications = ApplicationManager(
        ApplicationRegistry(),
    )

    return Runtime(
        planner=planner,
        execution=execution,
        workflow=workflow,
        memory=memory,
        plugins=plugins,
        tools=tools,
        applications=applications,
    )


def test_runtime_contains_tool_manager():

    runtime = create_runtime()

    assert isinstance(
        runtime.tools,
        ToolManager,
    )


def test_runtime_returns_same_tool_manager():

    runtime = create_runtime()

    assert runtime.tools is runtime.tools


def test_runtime_has_empty_tools():

    runtime = create_runtime()

    assert runtime.tools.installed() == []


def test_runtime_keeps_existing_components():

    runtime = create_runtime()

    assert isinstance(
        runtime.planner,
        Planner,
    )

    assert isinstance(
        runtime.execution,
        Execution,
    )

    assert isinstance(
        runtime.workflow,
        Workflow,
    )

    assert isinstance(
        runtime.memory,
        Memory,
    )

    assert isinstance(
        runtime.plugins,
        PluginManager,
    )

    assert isinstance(
        runtime.applications,
        ApplicationManager,
    )


def test_runtime_run():

    runtime = create_runtime()

    assert runtime.run() == "Runtime Complete"


def test_runtime_repr():

    runtime = create_runtime()

    assert (
        repr(runtime)
        == (
            "Runtime("
            "planner=Planner, "
            "execution=Execution, "
            "workflow=Workflow, "
            "memory=Memory, "
            "plugins=PluginManager, "
            "tools=ToolManager, "
            "applications=ApplicationManager)"
        )
    )