"""
ScholarOS
Citation

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single
research citation.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4


@dataclass(
    slots=True,
)
class Citation:
    """
    Represents a single
    research citation.
    """

    title: str

    source: str

    url: (
        str
        | None
    ) = None

    authors: list[
        str
    ] = field(
        default_factory=list,
    )

    published: (
        str
        | None
    ) = None

    accessed: (
        str
        | None
    ) = None

    id: str = field(
        default_factory=lambda:
        str(
            uuid4(),
        ),
    )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id='{self.id}', "
            f"title={self.title!r}"
            f")"
        )