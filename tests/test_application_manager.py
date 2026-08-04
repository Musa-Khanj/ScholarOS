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


def create_manager() -> ApplicationManager:

    return ApplicationManager(
        ApplicationRegistry(),
    )


def test_manager_register():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    assert manager.installed() == [
        "Application",
    ]


def test_manager_unregister():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    manager.unregister(
        "Application",
    )

    assert manager.installed() == []


def test_manager_get():

    manager = create_manager()

    application = create_application()

    manager.register(
        application,
    )

    assert (
        manager.get(
            "Application",
        )
        is application
    )


def test_manager_contains():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    assert manager.contains(
        "Application",
    )


def test_manager_installed():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    assert manager.installed() == [
        "Application",
    ]


def test_manager_clear():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    manager.clear()

    assert manager.installed() == []


def test_manager_repr():

    manager = create_manager()

    manager.register(
        create_application(),
    )

    assert (
        repr(manager)
        == "ApplicationManager(applications=1)"
    )