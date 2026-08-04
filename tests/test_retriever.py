from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.manager import (
    RetrievalManager,
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


def create_retriever() -> Retriever:

    manager = RetrievalManager(
        RetrievalRegistry(),
    )

    collection = RetrievalCollection()

    collection.add(
        RetrievalResult(
            source="paper-1",
            content=(
                "Transformer models improve "
                "natural language processing."
            ),
            score=0.95,
            metadata={},
        ),
    )

    collection.add(
        RetrievalResult(
            source="paper-2",
            content=(
                "Neural networks are widely "
                "used in computer vision."
            ),
            score=0.80,
            metadata={},
        ),
    )

    collection.add(
        RetrievalResult(
            source="paper-3",
            content=(
                "Transformers are also used "
                "for vision models."
            ),
            score=0.99,
            metadata={},
        ),
    )

    manager.register(
        "Research",
        collection,
    )

    return Retriever(
        manager,
    )


def test_manager_property():

    retriever = create_retriever()

    assert isinstance(
        retriever.manager,
        RetrievalManager,
    )


def test_search_returns_matches():

    retriever = create_retriever()

    results = retriever.search(
        "transform",
    )

    assert len(
        results,
    ) == 2


def test_search_returns_sorted_results():

    retriever = create_retriever()

    results = retriever.search(
        "transform",
    )

    assert (
        results[0].score
        >=
        results[1].score
    )


def test_search_returns_empty_list():

    retriever = create_retriever()

    results = retriever.search(
        "biology",
    )

    assert results == []


def test_search_is_case_insensitive():

    retriever = create_retriever()

    results = retriever.search(
        "TRANSFORMER",
    )

    assert len(
        results,
    ) == 2


def test_repr():

    retriever = create_retriever()

    assert (
        repr(
            retriever,
        )
        ==
        "Retriever(collections=1)"
    )