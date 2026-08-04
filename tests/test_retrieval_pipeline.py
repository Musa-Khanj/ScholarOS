from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.filter import (
    RetrievalFilter,
)
from scholaros.retrieval.manager import (
    RetrievalManager,
)
from scholaros.retrieval.pipeline import (
    RetrievalPipeline,
)
from scholaros.retrieval.ranker import (
    RetrievalRanker,
)
from scholaros.retrieval.registry import (
    RetrievalRegistry,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)
from scholaros.retrieval.retriever import (
    Retriever,
)


def create_pipeline() -> RetrievalPipeline:

    registry = RetrievalRegistry()

    manager = RetrievalManager(
        registry,
    )

    collection = RetrievalCollection()

    collection.add(
        RetrievalResult(
            source="paper-1",
            content=(
                "Transformer models "
                "improve language models."
            ),
            score=0.80,
            metadata={},
        ),
    )

    collection.add(
        RetrievalResult(
            source="paper-2",
            content=(
                "Transformers achieve "
                "state-of-the-art results."
            ),
            score=0.95,
            metadata={},
        ),
    )

    collection.add(
        RetrievalResult(
            source="paper-3",
            content=(
                "Computer vision "
                "uses convolutional networks."
            ),
            score=0.50,
            metadata={},
        ),
    )

    manager.register(
        "Research",
        collection,
    )

    return RetrievalPipeline(
        Retriever(
            manager,
        ),
        RetrievalFilter(),
        RetrievalRanker(),
    )


def test_retriever_property():

    pipeline = create_pipeline()

    assert isinstance(
        pipeline.retriever,
        Retriever,
    )


def test_filter_property():

    pipeline = create_pipeline()

    assert isinstance(
        pipeline.filter,
        RetrievalFilter,
    )


def test_ranker_property():

    pipeline = create_pipeline()

    assert isinstance(
        pipeline.ranker,
        RetrievalRanker,
    )


def test_run_returns_ranked_results():

    pipeline = create_pipeline()

    results = pipeline.run(
        "transform",
    )

    assert len(
        results,
    ) == 2

    assert (
        results[0].score
        >=
        results[1].score
    )


def test_run_applies_filter():

    pipeline = create_pipeline()

    results = pipeline.run(
        "transform",
        minimum_score=0.90,
    )

    assert len(
        results,
    ) == 1

    assert (
        results[0].score
        == 0.95
    )


def test_run_returns_empty():

    pipeline = create_pipeline()

    results = pipeline.run(
        "biology",
    )

    assert results == []


def test_repr():

    pipeline = create_pipeline()

    assert (
        repr(
            pipeline,
        )
        ==
        "RetrievalPipeline("
        "collections=1)"
    )