from unittest.mock import MagicMock

from scholaros.workflow import Workflow


def create_workflow() -> Workflow:

    agent = MagicMock()

    agent.execute.return_value = "Workflow Complete"

    return Workflow(
        agent,
    )


def test_agent_property():

    workflow = create_workflow()

    assert workflow.agent is not None


def test_run():

    workflow = create_workflow()

    result = workflow.run()

    workflow.agent.execute.assert_called_once_with()

    assert result == "Workflow Complete"


def test_repr():

    workflow = create_workflow()

    representation = repr(
        workflow,
    )

    assert "Workflow" in representation