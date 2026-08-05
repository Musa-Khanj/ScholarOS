from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.embedding import (
    Embedding,
)


def create_embedding() -> Embedding:

    return Embedding(
        text="Transformer models",
        vector=[
            0.10,
            0.20,
            0.30,
        ],
        metadata={},
    )


def test_add():

    collection = (
        EmbeddingCollection()
    )

    embedding = create_embedding()

    collection.add(
        embedding,
    )

    assert (
        len(
            collection,
        )
        == 1
    )

    assert (
        collection[0]
        is embedding
    )


def test_remove():

    collection = (
        EmbeddingCollection()
    )

    embedding = create_embedding()

    collection.add(
        embedding,
    )

    collection.remove(
        embedding,
    )

    assert (
        len(
            collection,
        )
        == 0
    )


def test_clear():

    collection = (
        EmbeddingCollection()
    )

    collection.add(
        create_embedding(),
    )

    collection.add(
        create_embedding(),
    )

    collection.clear()

    assert (
        len(
            collection,
        )
        == 0
    )


def test_iter():

    collection = (
        EmbeddingCollection()
    )

    collection.add(
        create_embedding(),
    )

    collection.add(
        create_embedding(),
    )

    assert (
        len(
            list(
                collection,
            )
        )
        == 2
    )


def test_getitem():

    collection = (
        EmbeddingCollection()
    )

    embedding = create_embedding()

    collection.add(
        embedding,
    )

    assert (
        collection[0]
        is embedding
    )


def test_len():

    collection = (
        EmbeddingCollection()
    )

    assert (
        len(
            collection,
        )
        == 0
    )

    collection.add(
        create_embedding(),
    )

    assert (
        len(
            collection,
        )
        == 1
    )


def test_repr():

    collection = (
        EmbeddingCollection()
    )

    collection.add(
        create_embedding(),
    )

    assert (
        repr(
            collection,
        )
        ==
        "EmbeddingCollection("
        "embeddings=1)"
    )