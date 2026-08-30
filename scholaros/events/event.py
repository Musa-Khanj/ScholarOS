"""
ScholarOS
Event

Version : 2.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the immutable Event object used by the
ScholarOS event system.

Events represent something that has already
occurred within the application.

Examples
--------
- ChatOpened
- PluginLoaded
- SearchCompleted
- WorkspaceChanged
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Event:
    """
    Represents an application event.

    Parameters
    ----------
    name:
        Event name.

    payload:
        Event payload.

    metadata:
        Optional event metadata.

    timestamp:
        UTC timestamp generated automatically.

    id:
        Unique event identifier.
    """

    name: str

    payload: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )

    id: str = field(
        default_factory=lambda: str(
            uuid4(),
        ),
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Validate the event.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "Event name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Event name cannot be empty."
            )

        if not isinstance(
            self.payload,
            dict,
        ):
            raise TypeError(
                "Payload must be a dictionary."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "Metadata must be a dictionary."
            )

    @property
    def has_payload(
        self,
    ) -> bool:
        """
        Return True if the event contains payload.
        """

        return bool(
            self.payload,
        )

    @property
    def has_metadata(
        self,
    ) -> bool:
        """
        Return True if metadata exists.
        """

        return bool(
            self.metadata,
        )

    def copy(
        self,
    ) -> "Event":
        """
        Return a shallow copy of the event.

        The timestamp and identifier are preserved.
        """

        return Event(
            name=self.name,
            payload=dict(
                self.payload,
            ),
            metadata=dict(
                self.metadata,
            ),
            timestamp=self.timestamp,
            id=self.id,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"payload={self.payload!r}"
            f")"
        )