from unittest.mock import MagicMock

from scholaros.execution import Execution
from scholaros.planner import Planner
from scholaros.workflow import Workflow


def create_planner() -> Planner:

    agent = MagicMock()

    agent.execute.return_value = "Planning Complete"

    workflow = Workflow(
        agent,
    )

    execution = Execution(
        workflow,
    )

    return Planner(
        execution,
    )


def test_execution_property():

    planner = create_planner()

    assert isinstance(
        planner.execution,
        Execution,
    )


def test_plan():

    planner = create_planner()

    result = planner.plan()

    planner.execution.workflow.agent.execute.assert_called_once_with()

    assert result == "Planning Complete"


def test_repr():

    planner = create_planner()

    assert (
        repr(planner)
        == "Planner(execution=Execution)"
    )