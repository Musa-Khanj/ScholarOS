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

        self._norm: float | None = None
        self._inv_norm: float | None = None

    @property
    def norm(self) -> float:
        """Return the precomputed Euclidean (L2) norm of the vector."""
        if self._norm is None:
            from math import sqrt
            self._norm = sqrt(sum(v * v for v in self._vector))
            self._inv_norm = (1.0 / self._norm) if self._norm > 0 else 0.0
        return self._norm

    @property
    def inv_norm(self) -> float:
        """Return the reciprocal (1.0 / norm) for high-speed dot-product scaling."""
        if self._inv_norm is None:
            _ = self.norm
        return self._inv_norm or 0.0

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
