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


def test_registry_add():

    registry = ApplicationRegistry()

    application = create_application()

    registry.add(
        application,
    )

    assert len(
        registry,
    ) == 1


def test_registry_get():

    registry = ApplicationRegistry()

    application = create_application()

    registry.add(
        application,
    )

    assert (
        registry.get(
            "Application",
        )
        is application
    )


def test_registry_contains():

    registry = ApplicationRegistry()

    registry.add(
        create_application(),
    )

    assert registry.contains(
        "Application",
    )


def test_registry_remove():

    registry = ApplicationRegistry()

    registry.add(
        create_application(),
    )

    registry.remove(
        "Application",
    )

    assert not registry.contains(
        "Application",
    )


def test_registry_names():

    registry = ApplicationRegistry()

    registry.add(
        create_application(),
    )

    assert registry.names() == [
        "Application",
    ]


def test_registry_values():

    registry = ApplicationRegistry()

    application = create_application()

    registry.add(
        application,
    )

    assert registry.values() == [
        application,
    ]


def test_registry_items():

    registry = ApplicationRegistry()

    application = create_application()

    registry.add(
        application,
    )

    assert registry.items() == [
        (
            "Application",
            application,
        ),
    ]


def test_registry_clear():

    registry = ApplicationRegistry()

    registry.add(
        create_application(),
    )

    registry.clear()

    assert len(
        registry,
    ) == 0


def test_registry_repr():

    registry = ApplicationRegistry()

    registry.add(
        create_application(),
    )

    assert (
        repr(
            registry,
        )
        == "ApplicationRegistry(applications=1)"
    )