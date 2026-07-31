from scholaros.agents import BaseAgent


class DummyAgent(BaseAgent):
    @property
    def name(
        self,
    ) -> str:
        return "Dummy Agent"

    @property
    def description(
        self,
    ) -> str:
        return "Test agent."

    @property
    def version(
        self,
    ) -> str:
        return "1.0"

    def execute(
        self,
    ) -> object:
        return "executed"


def create_agent() -> DummyAgent:
    return DummyAgent()


def test_name_property():

    agent = create_agent()

    assert (
        agent.name
        == "Dummy Agent"
    )


def test_description_property():

    agent = create_agent()

    assert (
        agent.description
        == "Test agent."
    )


def test_version_property():

    agent = create_agent()

    assert (
        agent.version
        == "1.0"
    )


def test_execute():

    agent = create_agent()

    assert (
        agent.execute()
        == "executed"
    )


def test_repr():

    agent = create_agent()

    assert (
        repr(agent)
        == "DummyAgent(name='Dummy Agent', version='1.0')"
    )