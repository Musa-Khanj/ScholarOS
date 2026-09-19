from unittest.mock import MagicMock

from scholaros.applications.application import Application
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


def create_application() -> Application:

    agent = MagicMock()

    agent.execute.return_value = "Application Complete"

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

    runtime = Runtime(
        planner=planner,
        execution=execution,
        workflow=workflow,
        memory=memory,
        plugins=plugins,
        tools=tools,
        applications=applications,
    )

    return Application(
        runtime,
    )


def test_application_runtime_property():

    application = create_application()

    assert isinstance(
        application.runtime,
        Runtime,
    )


def test_application_run():

    application = create_application()

    assert (
        application.run()
        == "Application Complete"
    )


def test_application_repr():

    application = create_application()

    assert (
        repr(application)
        == (
            "Application("
            "runtime=Runtime)"
        )
    )
