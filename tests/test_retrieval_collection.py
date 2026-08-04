from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_result() -> RetrievalResult:

    return RetrievalResult(
        source="knowledge:paper-001",
        content="Transformer models achieve state-of-the-art performance.",
        score=0.96,
        metadata={
            "title": (
                "Attention Is All You Need"
            ),
        },
    )


def test_collection_add():

    collection = RetrievalCollection()

    result = create_result()

    collection.add(
        result,
    )

    assert collection.values() == [
        result,
    ]


def test_collection_remove():

    collection = RetrievalCollection()

    result = create_result()

    collection.add(
        result,
    )

    collection.remove(
        result,
    )

    assert collection.values() == []


def test_collection_remove_missing():

    collection = RetrievalCollection()

    collection.remove(
        create_result(),
    )

    assert len(
        collection,
    ) == 0


def test_collection_clear():

    collection = RetrievalCollection()

    collection.add(
        create_result(),
    )

    collection.clear()

    assert len(
        collection,
    ) == 0


def test_collection_values():

    collection = RetrievalCollection()

    result = create_result()

    collection.add(
        result,
    )

    assert collection.values() == [
        result,
    ]


def test_collection_len():

    collection = RetrievalCollection()

    collection.add(
        create_result(),
    )

    assert len(
        collection,
    ) == 1


def test_collection_iter():

    collection = RetrievalCollection()

    result = create_result()

    collection.add(
        result,
    )

    assert list(
        collection,
    ) == [
        result,
    ]


def test_collection_repr():

    collection = RetrievalCollection()

    collection.add(
        create_result(),
    )

    assert (
        repr(
            collection,
        )
        == (
            "RetrievalCollection("
            "results=1)"
        )
    )