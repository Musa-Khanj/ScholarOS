from scholaros.retrieval.filter import (
    RetrievalFilter,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_results() -> list[
    RetrievalResult
]:

    return [
        RetrievalResult(
            source="paper-1",
            content="Transformer models",
            score=0.95,
            metadata={},
        ),
        RetrievalResult(
            source="paper-2",
            content="Computer vision",
            score=0.75,
            metadata={},
        ),
        RetrievalResult(
            source="paper-3",
            content="Neural networks",
            score=0.45,
            metadata={},
        ),
    ]


def test_filter_default_threshold():

    retrieval_filter = (
        RetrievalFilter()
    )

    results = create_results()

    filtered = (
        retrieval_filter.filter(
            results,
        )
    )

    assert filtered == results

    assert filtered is not results


def test_filter_custom_threshold():

    retrieval_filter = (
        RetrievalFilter()
    )

    filtered = (
        retrieval_filter.filter(
            create_results(),
            minimum_score=0.70,
        )
    )

    assert len(
        filtered,
    ) == 2

    assert all(
        result.score >= 0.70
        for result in filtered
    )


def test_filter_returns_empty_list():

    retrieval_filter = (
        RetrievalFilter()
    )

    filtered = (
        retrieval_filter.filter(
            create_results(),
            minimum_score=1.00,
        )
    )

    assert filtered == []


def test_filter_empty_input():

    retrieval_filter = (
        RetrievalFilter()
    )

    filtered = (
        retrieval_filter.filter(
            [],
        )
    )

    assert filtered == []


def test_filter_preserves_order():

    retrieval_filter = (
        RetrievalFilter()
    )

    filtered = (
        retrieval_filter.filter(
            create_results(),
            minimum_score=0.40,
        )
    )

    assert [
        result.source
        for result in filtered
    ] == [
        "paper-1",
        "paper-2",
        "paper-3",
    ]


def test_repr():

    retrieval_filter = (
        RetrievalFilter()
    )

    assert (
        repr(
            retrieval_filter,
        )
        ==
        "RetrievalFilter()"
    )