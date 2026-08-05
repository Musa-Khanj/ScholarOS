from scholaros.research.manager import (
    ResearchSessionManager,
)
from scholaros.research.registry import (
    ResearchSessionRegistry,
)
from scholaros.research.session import (
    ResearchSession,
)


def create_manager() -> ResearchSessionManager:

    return ResearchSessionManager()


def create_session(
    query: str = "ScholarOS",
) -> ResearchSession:

    return ResearchSession(
        query=query,
    )


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        ResearchSessionRegistry,
    )


def test_create():

    manager = create_manager()

    session = manager.create(
        "ScholarOS",
    )

    assert isinstance(
        session,
        ResearchSession,
    )

    assert (
        session.query
        ==
        "ScholarOS"
    )

    assert (
        session
        in manager
    )


def test_register():

    manager = create_manager()

    session = create_session()

    manager.register(
        session,
    )

    assert (
        manager.sessions()
        ==
        [
            session,
        ]
    )


def test_unregister():

    manager = create_manager()

    session = create_session()

    manager.register(
        session,
    )

    manager.unregister(
        session,
    )

    assert (
        manager.sessions()
        == []
    )


def test_clear():

    manager = create_manager()

    manager.register(
        create_session(
            "One",
        ),
    )

    manager.register(
        create_session(
            "Two",
        ),
    )

    manager.clear()

    assert (
        manager.sessions()
        == []
    )


def test_sessions_returns_copy():

    manager = create_manager()

    session = create_session()

    manager.register(
        session,
    )

    sessions = (
        manager.sessions()
    )

    sessions.clear()

    assert (
        len(
            manager,
        )
        == 1
    )


def test_len():

    manager = create_manager()

    manager.register(
        create_session(
            "One",
        ),
    )

    manager.register(
        create_session(
            "Two",
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

    first = create_session(
        "One",
    )

    second = create_session(
        "Two",
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

    session = create_session()

    manager.register(
        session,
    )

    assert (
        session
        in manager
    )


def test_repr():

    manager = create_manager()

    manager.register(
        create_session(),
    )

    assert (
        repr(
            manager,
        )
        ==
        "ResearchSessionManager("
        "size=1"
        ")"
    )