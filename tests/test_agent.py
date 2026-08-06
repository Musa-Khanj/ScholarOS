from scholaros.collaboration.agent import (
    Agent,
)


def create_agent() -> Agent:

    return Agent(
        name="Planner",
        role="planning",
        description="Plans research tasks.",
    )


def test_name():

    agent = create_agent()

    assert (
        agent.name
        ==
        "Planner"
    )


def test_role():

    agent = create_agent()

    assert (
        agent.role
        ==
        "planning"
    )


def test_description():

    agent = create_agent()

    assert (
        agent.description
        ==
        "Plans research tasks."
    )


def test_enabled_default():

    agent = create_agent()

    assert (
        agent.enabled
        is True
    )


def test_enabled_custom():

    agent = Agent(
        name="Writer",
        role="writing",
        description="Writes reports.",
        enabled=False,
    )

    assert (
        agent.enabled
        is False
    )


def test_id_generated():

    agent = create_agent()

    assert isinstance(
        agent.id,
        str,
    )

    assert (
        len(
            agent.id,
        )
        > 0
    )


def test_unique_ids():

    first = create_agent()

    second = create_agent()

    assert (
        first.id
        != second.id
    )


def test_repr():

    agent = create_agent()

    expected = (
        "Agent("
        f"id='{agent.id}', "
        "name='Planner', "
        "role='planning'"
        ")"
    )

    assert (
        repr(
            agent,
        )
        == expected
    )