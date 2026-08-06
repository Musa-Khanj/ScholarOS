"""
ScholarOS
Agent

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents an AI
collaboration agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from uuid import uuid4


@dataclass(
    slots=True,
)
class Agent:
    """
    Represents an AI
    collaboration agent.
    """

    name: str

    role: str

    description: str

    enabled: bool = True

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
            f"name={self.name!r}, "
            f"role={self.role!r}"
            f")"
        )