from scholaros.retrieval.ranker import (
    RetrievalRanker,
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
            score=0.75,
            metadata={},
        ),
        RetrievalResult(
            source="paper-2",
            content="Computer vision",
            score=0.95,
            metadata={},
        ),
        RetrievalResult(
            source="paper-3",
            content="Neural networks",
            score=0.50,
            metadata={},
        ),
    ]


def test_rank_default_order():

    ranker = RetrievalRanker()

    ranked = ranker.rank(
        create_results(),
    )

    assert [
        result.score
        for result in ranked
    ] == [
        0.95,
        0.75,
        0.50,
    ]


def test_rank_ascending():

    ranker = RetrievalRanker()

    ranked = ranker.rank(
        create_results(),
        reverse=False,
    )

    assert [
        result.score
        for result in ranked
    ] == [
        0.50,
        0.75,
        0.95,
    ]


def test_rank_empty_list():

    ranker = RetrievalRanker()

    ranked = ranker.rank(
        [],
    )

    assert ranked == []


def test_rank_returns_new_list():

    ranker = RetrievalRanker()

    results = create_results()

    ranked = ranker.rank(
        results,
    )

    assert ranked is not results


def test_rank_preserves_original():

    ranker = RetrievalRanker()

    results = create_results()

    original = list(
        results,
    )

    ranker.rank(
        results,
    )

    assert results == original


def test_rank_is_stable():

    ranker = RetrievalRanker()

    results = [
        RetrievalResult(
            source="A",
            content="First",
            score=0.80,
            metadata={},
        ),
        RetrievalResult(
            source="B",
            content="Second",
            score=0.80,
            metadata={},
        ),
    ]

    ranked = ranker.rank(
        results,
    )

    assert (
        ranked[0].source
        == "A"
    )

    assert (
        ranked[1].source
        == "B"
    )


def test_repr():

    ranker = RetrievalRanker()

    assert (
        repr(
            ranker,
        )
        ==
        "RetrievalRanker()"
    )