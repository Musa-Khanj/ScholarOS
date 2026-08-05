"""
ScholarOS
Embedding

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents an embedded
text document.
"""

from __future__ import annotations

from collections.abc import Mapping


class Embedding:
    """
    Represents an
    embedding.
    """

    def __init__(
        self,
        text: str,
        vector: list[float],
        metadata: Mapping[
            str,
            object,
        ] | None = None,
    ) -> None:
        """
        Initialize the
        embedding.
        """

        self._text = text

        self._vector = list(
            vector,
        )

        self._metadata = dict(
            metadata or {},
        )

    @property
    def text(
        self,
    ) -> str:
        """
        Return the original
        text.
        """

        return self._text

    @property
    def vector(
        self,
    ) -> list[float]:
        """
        Return the embedding
        vector.
        """

        return list(
            self._vector,
        )

    @property
    def metadata(
        self,
    ) -> dict[
        str,
        object,
    ]:
        """
        Return the embedding
        metadata.
        """

        return dict(
            self._metadata,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the vector
        dimension.
        """

        return len(
            self._vector,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        embedding.
        """

        return (
            f"{self.__class__.__name__}("
            f"dimensions={len(self)}"
            f")"
        )