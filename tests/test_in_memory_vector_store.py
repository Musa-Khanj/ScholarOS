from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.in_memory_vector_store import (
    InMemoryVectorStore,
)
from scholaros.embeddings.similarity_metric import (
    SimilarityMetric,
)
from scholaros.embeddings.cosine_similarity import (
    CosineSimilarity,
)


class DummySimilarityMetric(
    SimilarityMetric,
):

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
            "Dummy similarity metric."
        )

    @property
    def version(
        self,
    ) -> str:

        return "1.0.0"

    def calculate(
        self,
        first: Embedding,
        second: Embedding,
    ) -> float:

        del first

        return second.vector[0]


def create_store(
    metric: SimilarityMetric | None = None,
) -> InMemoryVectorStore:

    return InMemoryVectorStore(
        metric,
    )


def create_embedding(
    text: str,
    vector: list[float],
) -> Embedding:

    return Embedding(
        text=text,
        vector=vector,
        metadata={},
    )


def test_default_metric():

    store = create_store()

    assert isinstance(
        store.metric,
        CosineSimilarity,
    )


def test_custom_metric():

    metric = DummySimilarityMetric()

    store = create_store(
        metric,
    )

    assert (
        store.metric
        is metric
    )


def test_name_property():

    store = create_store()

    assert (
        store.name
        ==
        "InMemoryVectorStore"
    )


def test_description_property():

    store = create_store()

    assert (
        store.description
        ==
        "Stores embeddings "
        "in memory."
    )


def test_version_property():

    store = create_store()

    assert (
        store.version
        == "1.0.0"
    )


def test_add():

    store = create_store()

    embedding = create_embedding(
        "One",
        [
            1.0,
            0.0,
        ],
    )

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

    embedding = create_embedding(
        "One",
        [
            1.0,
            0.0,
        ],
    )

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
        create_embedding(
            "One",
            [
                1.0,
                0.0,
            ],
        ),
    )

    store.add(
        create_embedding(
            "Two",
            [
                0.0,
                1.0,
            ],
        ),
    )

    store.clear()

    assert (
        store.embeddings()
        == []
    )


def test_embeddings_returns_copy():

    store = create_store()

    embedding = create_embedding(
        "One",
        [
            1.0,
            0.0,
        ],
    )

    store.add(
        embedding,
    )

    result = (
        store.embeddings()
    )

    result.clear()

    assert (
        len(
            store.embeddings(),
        )
        == 1
    )


def test_search_orders_results():

    metric = DummySimilarityMetric()

    store = create_store(
        metric,
    )

    low = create_embedding(
        "Low",
        [
            0.1,
        ],
    )

    medium = create_embedding(
        "Medium",
        [
            0.5,
        ],
    )

    high = create_embedding(
        "High",
        [
            0.9,
        ],
    )

    store.add(
        low,
    )

    store.add(
        high,
    )

    store.add(
        medium,
    )

    query = create_embedding(
        "Query",
        [
            0.0,
        ],
    )

    result = store.search(
        query,
    )

    assert (
        result
        ==
        [
            high,
            medium,
            low,
        ]
    )


def test_search_limit():

    metric = DummySimilarityMetric()

    store = create_store(
        metric,
    )

    store.add(
        create_embedding(
            "One",
            [
                0.9,
            ],
        ),
    )

    store.add(
        create_embedding(
            "Two",
            [
                0.8,
            ],
        ),
    )

    store.add(
        create_embedding(
            "Three",
            [
                0.7,
            ],
        ),
    )

    query = create_embedding(
        "Query",
        [
            0.0,
        ],
    )

    assert (
        len(
            store.search(
                query,
                limit=2,
            ),
        )
        == 2
    )


def test_repr():

    store = create_store()

    assert (
        repr(
            store,
        )
        ==
        "InMemoryVectorStore("
        "name='InMemoryVectorStore', "
        "version='1.0.0'"
        ")"
    )