"""
ScholarOS
Report

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a generated
research report.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4

from scholaros.research.citation import (
    Citation,
)


@dataclass(
    slots=True,
)
class Report:
    """
    Represents a generated
    research report.
    """

    title: str

    content: str

    citations: list[
        Citation
    ] = field(
        default_factory=list,
    )

    created_at: (
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