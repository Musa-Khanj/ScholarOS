"""
ScholarOS
Cosine Similarity

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Calculates cosine
similarity between
two embeddings.
"""

from __future__ import annotations

from math import sqrt

from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.similarity_metric import (
    SimilarityMetric,
)


class CosineSimilarity(
    SimilarityMetric,
):
    """
    Calculates cosine
    similarity between
    two embeddings.
    """

    @property
    def name(
        self,
    ) -> str:
        """
        Return the metric
        name.
        """

        return (
            "CosineSimilarity"
        )

    @property
    def description(
        self,
    ) -> str:
        """
        Return the metric
        description.
        """

        return (
            "Calculates cosine "
            "similarity between "
            "two embeddings."
        )

    @property
    def version(
        self,
    ) -> str:
        """
        Return the metric
        version.
        """

        return "1.0.0"

    def calculate(
        self,
        first: Embedding,
        second: Embedding,
    ) -> float:
        """
        Calculate the cosine
        similarity between
        two embeddings.
        """

        first_vector = first.vector
        second_vector = second.vector

        if (
            len(first_vector)
            !=
            len(second_vector)
        ):
            raise ValueError(
                "Embedding vectors "
                "must have the same "
                "length."
            )

        dot_product = sum(
            a * b
            for a, b in zip(
                first_vector,
                second_vector,
            )
        )

        first_norm = sqrt(
            sum(
                value * value
                for value in first_vector
            )
        )

        second_norm = sqrt(
            sum(
                value * value
                for value in second_vector
            )
        )

        if (
            first_norm == 0.0
            or second_norm == 0.0
        ):
            return 0.0

        return (
            dot_product
            /
            (
                first_norm
                * second_norm
            )
        )