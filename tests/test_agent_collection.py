from scholaros.collaboration.agent import (
    Agent,
)
from scholaros.collaboration.agent_collection import (
    AgentCollection,
)


def create_collection() -> AgentCollection:

    return AgentCollection()


def create_agent(
    name: str = "Planner",
) -> Agent:

    return Agent(
        name=name,
        role="planning",
        description="Plans research tasks.",
    )


def test_add():

    collection = create_collection()

    agent = create_agent()

    collection.add(
        agent,
    )

    assert (
        collection.all()
        ==
        [
            agent,
        ]
    )


def test_remove():

    collection = create_collection()

    agent = create_agent()

    collection.add(
        agent,
    )

    collection.remove(
        agent,
    )

    assert (
        collection.all()
        == []
    )


def test_clear():

    collection = create_collection()

    collection.add(
        create_agent(
            "Planner",
        ),
    )

    collection.add(
        create_agent(
            "Writer",
        ),
    )

    collection.clear()

    assert (
        collection.all()
        == []
    )


def test_all_returns_copy():

    collection = create_collection()

    agent = create_agent()

    collection.add(
        agent,
    )

    agents = (
        collection.all()
    )

    agents.clear()

    assert (
        len(
            collection,
        )
        == 1
    )


def test_len():

    collection = create_collection()

    collection.add(
        create_agent(
            "Planner",
        ),
    )

    collection.add(
        create_agent(
            "Writer",
        ),
    )

    assert (
        len(
            collection,
        )
        == 2
    )


def test_iter():

    collection = create_collection()

    first = create_agent(
        "Planner",
    )

    second = create_agent(
        "Writer",
    )

    collection.add(
        first,
    )

    collection.add(
        second,
    )

    assert (
        list(
            collection,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    collection = create_collection()

    agent = create_agent()

    collection.add(
        agent,
    )

    assert (
        agent
        in collection
    )


def test_repr():

    collection = create_collection()

    collection.add(
        create_agent(),
    )

    assert (
        repr(
            collection,
        )
        ==
        "AgentCollection("
        "size=1"
        ")"
    )