"""
ScholarOS
Retrieval Result

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the result of a
retrieval operation.
"""

from __future__ import annotations

from typing import Any


class RetrievalResult:
    """
    Represents the result of a
    retrieval operation.
    """

    def __init__(
        self,
        source: str,
        content: str,
        score: float,
        metadata: dict[
            str,
            Any,
        ] | None = None,
    ) -> None:
        """
        Initialize the retrieval
        result.
        """

        self._source = source
        self._content = content
        self._score = score
        self._metadata = (
            metadata
            if metadata is not None
            else {}
        )

    @property
    def source(
        self,
    ) -> str:
        """
        Return the retrieval
        source.
        """

        return self._source

    @property
    def content(
        self,
    ) -> str:
        """
        Return the retrieved
        content.
        """

        return self._content

    @property
    def score(
        self,
    ) -> float:
        """
        Return the retrieval
        score.
        """

        return self._score

    @property
    def metadata(
        self,
    ) -> dict[
        str,
        Any,
    ]:
        """
        Return the retrieval
        metadata.
        """

        return self._metadata

    def to_dict(
        self,
    ) -> dict[
        str,
        Any,
    ]:
        """
        Return the retrieval result
        as a dictionary.
        """

        return {
            "source": self.source,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval result.
        """

        return (
            f"{self.__class__.__name__}("
            f"source={self.source!r}, "
            f"score={self.score}"
            f")"
        )