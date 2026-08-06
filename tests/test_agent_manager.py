from scholaros.collaboration.agent import (
    Agent,
)
from scholaros.collaboration.agent_manager import (
    AgentManager,
)
from scholaros.collaboration.agent_registry import (
    AgentRegistry,
)


def create_manager() -> AgentManager:

    return AgentManager()


def create_agent(
    name: str = "Planner",
) -> Agent:

    return Agent(
        name=name,
        role="planning",
        description="Plans research tasks.",
    )


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        AgentRegistry,
    )


def test_create():

    manager = create_manager()

    agent = manager.create(
        name="Planner",
        role="planning",
        description="Plans research tasks.",
    )

    assert isinstance(
        agent,
        Agent,
    )

    assert (
        agent.name
        ==
        "Planner"
    )

    assert (
        agent.role
        ==
        "planning"
    )

    assert (
        agent.description
        ==
        "Plans research tasks."
    )

    assert (
        agent.enabled
        is True
    )

    assert (
        agent
        in manager
    )


def test_create_with_enabled_false():

    manager = create_manager()

    agent = manager.create(
        name="Writer",
        role="writing",
        description="Writes reports.",
        enabled=False,
    )

    assert (
        agent.enabled
        is False
    )


def test_register():

    manager = create_manager()

    agent = create_agent()

    manager.register(
        agent,
    )

    assert (
        manager.agents()
        ==
        [
            agent,
        ]
    )


def test_unregister():

    manager = create_manager()

    agent = create_agent()

    manager.register(
        agent,
    )

    manager.unregister(
        agent,
    )

    assert (
        manager.agents()
        == []
    )


def test_clear():

    manager = create_manager()

    manager.register(
        create_agent(
            "Planner",
        ),
    )

    manager.register(
        create_agent(
            "Writer",
        ),
    )

    manager.clear()

    assert (
        manager.agents()
        == []
    )


def test_agents_returns_copy():

    manager = create_manager()

    agent = create_agent()

    manager.register(
        agent,
    )

    agents = (
        manager.agents()
    )

    agents.clear()

    assert (
        len(
            manager,
        )
        == 1
    )


def test_len():

    manager = create_manager()

    manager.register(
        create_agent(
            "Planner",
        ),
    )

    manager.register(
        create_agent(
            "Writer",
        ),
    )

    assert (
        len(
            manager,
        )
        == 2
    )


def test_iter():

    manager = create_manager()

    first = create_agent(
        "Planner",
    )

    second = create_agent(
        "Writer",
    )

    manager.register(
        first,
    )

    manager.register(
        second,
    )

    assert (
        list(
            manager,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    manager = create_manager()

    agent = create_agent()

    manager.register(
        agent,
    )

    assert (
        agent
        in manager
    )


def test_repr():

    manager = create_manager()

    manager.register(
        create_agent(),
    )

    assert (
        repr(
            manager,
        )
        ==
        "AgentManager("
        "size=1"
        ")"
    )