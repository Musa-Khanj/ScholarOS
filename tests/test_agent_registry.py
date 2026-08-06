from scholaros.collaboration.agent import (
    Agent,
)
from scholaros.collaboration.agent_collection import (
    AgentCollection,
)
from scholaros.collaboration.agent_registry import (
    AgentRegistry,
)


def create_registry() -> AgentRegistry:

    return AgentRegistry()


def create_agent(
    name: str = "Planner",
) -> Agent:

    return Agent(
        name=name,
        role="planning",
        description="Plans research tasks.",
    )


def test_collection_property():

    registry = create_registry()

    assert isinstance(
        registry.collection,
        AgentCollection,
    )


def test_register():

    registry = create_registry()

    agent = create_agent()

    registry.register(
        agent,
    )

    assert (
        registry.agents()
        ==
        [
            agent,
        ]
    )


def test_unregister():

    registry = create_registry()

    agent = create_agent()

    registry.register(
        agent,
    )

    registry.unregister(
        agent,
    )

    assert (
        registry.agents()
        == []
    )


def test_clear():

    registry = create_registry()

    registry.register(
        create_agent(
            "Planner",
        ),
    )

    registry.register(
        create_agent(
            "Writer",
        ),
    )

    registry.clear()

    assert (
        registry.agents()
        == []
    )


def test_agents_returns_copy():

    registry = create_registry()

    agent = create_agent()

    registry.register(
        agent,
    )

    agents = (
        registry.agents()
    )

    agents.clear()

    assert (
        len(
            registry,
        )
        == 1
    )


def test_len():

    registry = create_registry()

    registry.register(
        create_agent(
            "Planner",
        ),
    )

    registry.register(
        create_agent(
            "Writer",
        ),
    )

    assert (
        len(
            registry,
        )
        == 2
    )


def test_iter():

    registry = create_registry()

    first = create_agent(
        "Planner",
    )

    second = create_agent(
        "Writer",
    )

    registry.register(
        first,
    )

    registry.register(
        second,
    )

    assert (
        list(
            registry,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    registry = create_registry()

    agent = create_agent()

    registry.register(
        agent,
    )

    assert (
        agent
        in registry
    )


def test_repr():

    registry = create_registry()

    registry.register(
        create_agent(),
    )

    assert (
        repr(
            registry,
        )
        ==
        "AgentRegistry("
        "size=1"
        ")"
    )