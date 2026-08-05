"""
ScholarOS
Research Session

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single
research session.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4

from scholaros.research.result import (
    ResearchResult,
)


@dataclass(
    slots=True,
)
class ResearchSession:
    """
    Represents a single
    research session.
    """

    query: str

    context: list[
        str
    ] = field(
        default_factory=list,
    )

    notes: list[
        str
    ] = field(
        default_factory=list,
    )

    result: (
        ResearchResult
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
            f"query={self.query!r}"
            f")"
        )
    