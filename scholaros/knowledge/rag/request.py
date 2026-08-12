"""
ScholarOS
RAG Request

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a request submitted to
the Retrieval-Augmented Generation
pipeline.
"""

from __future__ import annotations

import math


class RAGRequest:
    """
    Represents a RAG request.
    """

    def __init__(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> None:
        """
        Initialize the RAG request.
        """

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "RAG query must be a string."
            )

        if not query.strip():
            raise ValueError(
                "RAG query must not be empty."
            )

        if not isinstance(
            minimum_score,
            (int, float),
        ):
            raise TypeError(
                "RAG minimum score must "
                "be a number."
            )

        if not math.isfinite(
            float(minimum_score),
        ):
            raise ValueError(
                "RAG minimum score must "
                "be finite."
            )

        self._query = query
        self._minimum_score = (
            minimum_score
        )

    @property
    def query(
        self,
    ) -> str:
        """
        Return the RAG query.
        """

        return self._query

    @property
    def minimum_score(
        self,
    ) -> float:
        """
        Return the minimum retrieval score.
        """

        return self._minimum_score

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the request.
        """

        return (
            f"{self.__class__.__name__}("
            f"query={self.query!r}, "
            f"minimum_score={self.minimum_score!r}"
            f")"
        )