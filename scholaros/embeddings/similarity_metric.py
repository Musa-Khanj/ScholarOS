"""
ScholarOS
Similarity Metric

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Abstract base class
for similarity metrics.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scholaros.embeddings.embedding import (
    Embedding,
)


class SimilarityMetric(
    ABC,
):
    """
    Abstract similarity
    metric.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the metric
        name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return the metric
        description.
        """

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the metric
        version.
        """

    @abstractmethod
    def calculate(
        self,
        first: Embedding,
        second: Embedding,
    ) -> float:
        """
        Calculate the
        similarity score
        between two
        embeddings.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        similarity metric.
        """

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}'"
            f")"
        )