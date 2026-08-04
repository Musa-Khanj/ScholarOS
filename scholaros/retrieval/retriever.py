"""
ScholarOS
Retriever

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Performs retrieval over
registered retrieval
collections.
"""

from __future__ import annotations

from scholaros.retrieval.manager import (
    RetrievalManager,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


class Retriever:
    """
    Searches registered
    retrieval collections.
    """

    def __init__(
        self,
        manager: RetrievalManager,
    ) -> None:
        """
        Initialize the
        retriever.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> RetrievalManager:
        """
        Return the retrieval
        manager.
        """

        return self._manager

    def search(
        self,
        query: str,
    ) -> list[RetrievalResult]:
        """
        Search registered
        retrieval collections.
        """

        query = query.casefold()

        matches: list[
            RetrievalResult
        ] = []

        for collection in (
            self._manager
            .registry
            .values()
        ):

            for result in collection:

                if (
                    query
                    in result.content.casefold()
                ):

                    matches.append(
                        result,
                    )

        matches.sort(
            key=lambda result: (
                result.score
            ),
            reverse=True,
        )

        return matches

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retriever.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.manager.registry)}"
            f")"
        )