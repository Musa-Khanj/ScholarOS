from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.vector_store import (
    VectorStore,
)


class DummyVectorStore(
    VectorStore,
):

    def __init__(
        self,
    ) -> None:

        self._embeddings: list[
            Embedding
        ] = []

    @property
    def name(
        self,
    ) -> str:

        return "Dummy"

    @property
    def description(
        self,
    ) -> str:

        return (
            "Dummy vector store."
        )

    @property
    def version(
        self,
    ) -> str:

        return "1.0.0"

    def add(
        self,
        embedding: Embedding,
    ) -> None:

        self._embeddings.append(
            embedding,
        )

    def remove(
        self,
        embedding: Embedding,
    ) -> None:

        self._embeddings.remove(
            embedding,
        )

    def clear(
        self,
    ) -> None:

        self._embeddings.clear()

    def embeddings(
        self,
    ) -> list[
        Embedding
    ]:

        return list(
            self._embeddings,
        )

    def search(
        self,
        query: Embedding,
        limit: int = 5,
    ) -> list[
        Embedding
    ]:

        return self._embeddings[
            :limit
        ]


def create_embedding() -> Embedding:

    return Embedding(
        text="ScholarOS",
        vector=[
            0.10,
            0.20,
            0.30,
        ],
        metadata={},
    )


def create_store() -> DummyVectorStore:

    return DummyVectorStore()


def test_add():

    store = create_store()

    embedding = create_embedding()

    store.add(
        embedding,
    )

    assert (
        store.embeddings()
        ==
        [
            embedding,
        ]
    )


def test_remove():

    store = create_store()

    embedding = create_embedding()

    store.add(
        embedding,
    )

    store.remove(
        embedding,
    )

    assert (
        store.embeddings()
        == []
    )


def test_clear():

    store = create_store()

    store.add(
        create_embedding(),
    )

    store.add(
        create_embedding(),
    )

    store.clear()

    assert (
        store.embeddings()
        == []
    )


def test_search():

    store = create_store()

    first = create_embedding()

    second = create_embedding()

    store.add(
        first,
    )

    store.add(
        second,
    )

    result = store.search(
        first,
        limit=1,
    )

    assert (
        result
        ==
        [
            first,
        ]
    )


def test_repr():

    store = create_store()

    assert (
        repr(
            store,
        )
        ==
        "DummyVectorStore("
        "name='Dummy', "
        "version='1.0.0'"
        ")"
    )