from scholaros.research.collection import (
    ResearchSessionCollection,
)
from scholaros.research.registry import (
    ResearchSessionRegistry,
)
from scholaros.research.session import (
    ResearchSession,
)


def create_registry() -> ResearchSessionRegistry:

    return ResearchSessionRegistry()


def create_session(
    query: str = "ScholarOS",
) -> ResearchSession:

    return ResearchSession(
        query=query,
    )


def test_collection_property():

    registry = create_registry()

    assert isinstance(
        registry.collection,
        ResearchSessionCollection,
    )


def test_register():

    registry = create_registry()

    session = create_session()

    registry.register(
        session,
    )

    assert (
        registry.sessions()
        ==
        [
            session,
        ]
    )


def test_unregister():

    registry = create_registry()

    session = create_session()

    registry.register(
        session,
    )

    registry.unregister(
        session,
    )

    assert (
        registry.sessions()
        == []
    )


def test_clear():

    registry = create_registry()

    registry.register(
        create_session(
            "One",
        ),
    )

    registry.register(
        create_session(
            "Two",
        ),
    )

    registry.clear()

    assert (
        registry.sessions()
        == []
    )


def test_sessions_returns_copy():

    registry = create_registry()

    session = create_session()

    registry.register(
        session,
    )

    sessions = (
        registry.sessions()
    )

    sessions.clear()

    assert (
        len(
            registry,
        )
        == 1
    )


def test_len():

    registry = create_registry()

    registry.register(
        create_session(
            "One",
        ),
    )

    registry.register(
        create_session(
            "Two",
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

    first = create_session(
        "One",
    )

    second = create_session(
        "Two",
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

    session = create_session()

    registry.register(
        session,
    )

    assert (
        session
        in registry
    )


def test_repr():

    registry = create_registry()

    registry.register(
        create_session(),
    )

    assert (
        repr(
            registry,
        )
        ==
        "ResearchSessionRegistry("
        "size=1"
        ")"
    )