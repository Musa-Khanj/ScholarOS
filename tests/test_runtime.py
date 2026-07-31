from unittest.mock import MagicMock

from scholaros.execution import Execution
from scholaros.memory import Memory
from scholaros.planner import Planner
from scholaros.runtime import Runtime
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

    return Runtime(
        planner=planner,
        execution=execution,
        workflow=workflow,
        memory=memory,
    )


def test_planner_property():

    runtime = create_runtime()

    assert isinstance(
        runtime.planner,
        Planner,
    )


def test_execution_property():

    runtime = create_runtime()

    assert isinstance(
        runtime.execution,
        Execution,
    )


def test_workflow_property():

    runtime = create_runtime()

    assert isinstance(
        runtime.workflow,
        Workflow,
    )


def test_memory_property():

    runtime = create_runtime()

    assert isinstance(
        runtime.memory,
        Memory,
    )


def test_run():

    runtime = create_runtime()

    result = runtime.run()

    runtime.workflow.agent.execute.assert_called_once_with()

    assert result == "Runtime Complete"


def test_repr():

    runtime = create_runtime()

    assert (
        repr(runtime)
        == (
            "Runtime("
            "planner=Planner, "
            "execution=Execution, "
            "workflow=Workflow, "
            "memory=Memory)"
        )
    )