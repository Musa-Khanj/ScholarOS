from scholaros.agents import BaseAgent
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


class DummyAgent(BaseAgent):

    @property
    def name(
        self,
    ) -> str:

        return "dummy"

    @property
    def description(
        self,
    ) -> str:

        return "Dummy agent"

    @property
    def version(
        self,
    ) -> str:

        return "1.0"

    def execute(
        self,
    ) -> object:

        return "ok"


def create_runtime() -> Runtime:

    agent = DummyAgent()

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


def test_runtime_contains_plugin_manager():

    runtime = create_runtime()

    assert isinstance(
        runtime.plugins,
        PluginManager,
    )


def test_runtime_returns_same_plugin_manager():

    runtime = create_runtime()

    assert runtime.plugins is runtime.plugins


def test_runtime_has_empty_plugins():

    runtime = create_runtime()

    assert runtime.plugins.installed() == []


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
        runtime.tools,
        ToolManager,
    )

    assert isinstance(
        runtime.applications,
        ApplicationManager,
    )


def test_runtime_run():

    runtime = create_runtime()

    assert runtime.run() == "ok"


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