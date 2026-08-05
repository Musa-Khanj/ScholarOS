from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.similarity_metric import (
    SimilarityMetric,
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
        del second

        return 1.0


def create_metric() -> DummySimilarityMetric:

    return DummySimilarityMetric()


def create_embedding(
    text: str = "ScholarOS",
) -> Embedding:

    return Embedding(
        text=text,
        vector=[
            0.10,
            0.20,
            0.30,
        ],
        metadata={},
    )


def test_name_property():

    metric = create_metric()

    assert (
        metric.name
        == "Dummy"
    )


def test_description_property():

    metric = create_metric()

    assert (
        metric.description
        ==
        "Dummy similarity metric."
    )


def test_version_property():

    metric = create_metric()

    assert (
        metric.version
        == "1.0.0"
    )


def test_calculate():

    metric = create_metric()

    first = create_embedding(
        "First",
    )

    second = create_embedding(
        "Second",
    )

    assert (
        metric.calculate(
            first,
            second,
        )
        == 1.0
    )


def test_repr():

    metric = create_metric()

    assert (
        repr(
            metric,
        )
        ==
        "DummySimilarityMetric("
        "name='Dummy', "
        "version='1.0.0'"
        ")"
    )