from math import isclose

import pytest

from scholaros.embeddings.cosine_similarity import (
    CosineSimilarity,
)
from scholaros.embeddings.embedding import (
    Embedding,
)


def create_metric() -> CosineSimilarity:

    return CosineSimilarity()


def create_embedding(
    vector: list[float],
) -> Embedding:

    return Embedding(
        text="ScholarOS",
        vector=vector,
        metadata={},
    )


def test_name_property():

    metric = create_metric()

    assert (
        metric.name
        ==
        "CosineSimilarity"
    )


def test_description_property():

    metric = create_metric()

    assert (
        metric.description
        ==
        "Calculates cosine "
        "similarity between "
        "two embeddings."
    )


def test_version_property():

    metric = create_metric()

    assert (
        metric.version
        == "1.0.0"
    )


def test_identical_vectors():

    metric = create_metric()

    first = create_embedding(
        [
            1.0,
            2.0,
            3.0,
        ],
    )

    second = create_embedding(
        [
            1.0,
            2.0,
            3.0,
        ],
    )

    assert isclose(
        metric.calculate(
            first,
            second,
        ),
        1.0,
    )


def test_orthogonal_vectors():

    metric = create_metric()

    first = create_embedding(
        [
            1.0,
            0.0,
        ],
    )

    second = create_embedding(
        [
            0.0,
            1.0,
        ],
    )

    assert isclose(
        metric.calculate(
            first,
            second,
        ),
        0.0,
    )


def test_opposite_vectors():

    metric = create_metric()

    first = create_embedding(
        [
            1.0,
            0.0,
        ],
    )

    second = create_embedding(
        [
            -1.0,
            0.0,
        ],
    )

    assert isclose(
        metric.calculate(
            first,
            second,
        ),
        -1.0,
    )


def test_zero_vector():

    metric = create_metric()

    first = create_embedding(
        [
            0.0,
            0.0,
        ],
    )

    second = create_embedding(
        [
            1.0,
            2.0,
        ],
    )

    assert (
        metric.calculate(
            first,
            second,
        )
        == 0.0
    )


def test_mismatched_dimensions():

    metric = create_metric()

    first = create_embedding(
        [
            1.0,
            2.0,
        ],
    )

    second = create_embedding(
        [
            1.0,
            2.0,
            3.0,
        ],
    )

    with pytest.raises(
        ValueError,
    ):
        metric.calculate(
            first,
            second,
        )


def test_repr():

    metric = create_metric()

    assert (
        repr(
            metric,
        )
        ==
        "CosineSimilarity("
        "name='CosineSimilarity', "
        "version='1.0.0'"
        ")"
    )