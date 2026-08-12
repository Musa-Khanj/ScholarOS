from scholaros.knowledge.rag.request import (
    RAGRequest,
)


def test_request_query():

    request = RAGRequest(
        query="What is retrieval augmented generation?",
    )

    assert (
        request.query
        == "What is retrieval augmented generation?"
    )


def test_request_minimum_score():

    request = RAGRequest(
        query="ScholarOS",
        minimum_score=0.75,
    )

    assert (
        request.minimum_score
        == 0.75
    )


def test_request_default_minimum_score():

    request = RAGRequest(
        query="ScholarOS",
    )

    assert (
        request.minimum_score
        == 0.0
    )


def test_request_rejects_empty_query():

    try:
        RAGRequest(
            query="",
        )

        assert False

    except ValueError as exc:

        assert (
            str(exc)
            == "RAG query must not be empty."
        )


def test_request_rejects_whitespace_query():

    try:
        RAGRequest(
            query="   ",
        )

        assert False

    except ValueError as exc:

        assert (
            str(exc)
            == "RAG query must not be empty."
        )


def test_request_repr():

    request = RAGRequest(
        query="ScholarOS",
        minimum_score=0.5,
    )

    assert (
        repr(
            request,
        )
        == (
            "RAGRequest("
            "query='ScholarOS', "
            "minimum_score=0.5)"
        )
    )