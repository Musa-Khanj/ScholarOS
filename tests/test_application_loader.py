from unittest.mock import MagicMock

from scholaros.applications.application import Application
from scholaros.applications.loader import ApplicationLoader
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


def create_loader() -> ApplicationLoader:

    return ApplicationLoader(
        ApplicationManager(
            ApplicationRegistry(),
        ),
    )


def test_loader_load():

    loader = create_loader()

    loader.load(
        create_application(),
    )

    assert loader.discover() == [
        "Application",
    ]


def test_loader_unload():

    loader = create_loader()

    loader.load(
        create_application(),
    )

    loader.unload(
        "Application",
    )

    assert loader.discover() == []


def test_loader_reload():

    loader = create_loader()

    application = create_application()

    loader.load(
        application,
    )

    loader.reload(
        application,
    )

    assert loader.discover() == [
        "Application",
    ]


def test_loader_discover():

    loader = create_loader()

    loader.load(
        create_application(),
    )

    assert loader.discover() == [
        "Application",
    ]


def test_loader_repr():

    loader = create_loader()

    loader.load(
        create_application(),
    )

    assert (
        repr(loader)
        == "ApplicationLoader(applications=1)"
    )