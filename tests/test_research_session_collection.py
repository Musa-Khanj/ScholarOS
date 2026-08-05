from scholaros.research.collection import (
    ResearchSessionCollection,
)
from scholaros.research.session import (
    ResearchSession,
)


def create_collection() -> ResearchSessionCollection:

    return ResearchSessionCollection()


def create_session(
    query: str = "ScholarOS",
) -> ResearchSession:

    return ResearchSession(
        query=query,
    )


def test_add():

    collection = create_collection()

    session = create_session()

    collection.add(
        session,
    )

    assert (
        collection.all()
        ==
        [
            session,
        ]
    )


def test_remove():

    collection = create_collection()

    session = create_session()

    collection.add(
        session,
    )

    collection.remove(
        session,
    )

    assert (
        collection.all()
        == []
    )


def test_clear():

    collection = create_collection()

    collection.add(
        create_session(
            "One",
        ),
    )

    collection.add(
        create_session(
            "Two",
        ),
    )

    collection.clear()

    assert (
        collection.all()
        == []
    )


def test_all_returns_copy():

    collection = create_collection()

    session = create_session()

    collection.add(
        session,
    )

    sessions = (
        collection.all()
    )

    sessions.clear()

    assert (
        len(
            collection,
        )
        == 1
    )


def test_len():

    collection = create_collection()

    collection.add(
        create_session(),
    )

    collection.add(
        create_session(
            "Second",
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

    first = create_session(
        "One",
    )

    second = create_session(
        "Two",
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

    session = create_session()

    collection.add(
        session,
    )

    assert (
        session
        in collection
    )


def test_repr():

    collection = create_collection()

    collection.add(
        create_session(),
    )

    assert (
        repr(
            collection,
        )
        ==
        "ResearchSessionCollection("
        "size=1"
        ")"
    )