from scholaros.research.session import (
    ResearchSession,
)


def create_session() -> ResearchSession:

    return ResearchSession(
        query="What is ScholarOS?",
    )


def test_query():

    session = create_session()

    assert (
        session.query
        ==
        "What is ScholarOS?"
    )


def test_context_default():

    session = create_session()

    assert (
        session.context
        == []
    )


def test_notes_default():

    session = create_session()

    assert (
        session.notes
        == []
    )


def test_result_default():

    session = create_session()

    assert (
        session.result
        is None
    )


def test_id_generated():

    session = create_session()

    assert isinstance(
        session.id,
        str,
    )

    assert (
        len(
            session.id,
        )
        > 0
    )


def test_unique_ids():

    first = create_session()

    second = create_session()

    assert (
        first.id
        != second.id
    )


def test_context_is_independent():

    first = create_session()

    second = create_session()

    first.context.append(
        "Document",
    )

    assert (
        second.context
        == []
    )


def test_notes_are_independent():

    first = create_session()

    second = create_session()

    first.notes.append(
        "Observation",
    )

    assert (
        second.notes
        == []
    )


def test_repr():

    session = create_session()

    expected = (
        "ResearchSession("
        f"id='{session.id}', "
        "query='What is ScholarOS?'"
        ")"
    )

    assert (
        repr(
            session,
        )
        == expected
    )