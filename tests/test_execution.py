from unittest.mock import MagicMock

from scholaros.execution import Execution
from scholaros.workflow import Workflow


def create_execution() -> Execution:

    agent = MagicMock()

    agent.execute.return_value = "Execution Complete"

    workflow = Workflow(
        agent,
    )

    return Execution(
        workflow,
    )


def test_workflow_property():

    execution = create_execution()

    assert isinstance(
        execution.workflow,
        Workflow,
    )


def test_execute():

    execution = create_execution()

    result = execution.execute()

    execution.workflow.agent.execute.assert_called_once_with()

    assert result == "Execution Complete"


def test_repr():

    execution = create_execution()

    assert (
        repr(execution)
        == "Execution(workflow=Workflow)"
    )