"""
ScholarOS
RAG Context

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the context assembled from
retrieval results for RAG generation.
"""

from __future__ import annotations

from scholaros.retrieval.result import (
    RetrievalResult,
)


class RAGContext:
    """
    Represents context assembled from
    retrieval results.
    """

    def __init__(
        self,
        results: list[RetrievalResult],
    ) -> None:
        """
        Initialize the RAG context.
        """

        self._results = tuple(
            results,
        )

    @property
    def results(
        self,
    ) -> tuple[
        RetrievalResult,
        ...,
    ]:
        """
        Return the retrieval results
        used to build the context.
        """

        return self._results

    @property
    def text(
        self,
    ) -> str:
        """
        Return the assembled context text.
        """

        if not self._results:
            return ""

        sections: list[str] = []

        for index, result in enumerate(
            self._results,
            start=1,
        ):
            sections.append(
                (
                    f"[Source {index}: "
                    f"{result.source}]\n"
                    f"{result.content}"
                )
            )

        return "\n\n".join(
            sections,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of retrieval
        results contained in the context.
        """

        return len(
            self._results,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the context.
        """

        return (
            f"{self.__class__.__name__}("
            f"results={len(self)}"
            f")"
        )