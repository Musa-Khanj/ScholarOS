"""
ScholarOS Knowledge Metadata.

Represents metadata associated with a knowledge document or chunk.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class KnowledgeMetadata:
    """
    Represents metadata for a knowledge document.
    """

    def __init__(
        self,
        author: str = "",
        source: str = "",
        language: str = "",
        version: str = "",
        tags: tuple[str, ...] | list[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        extra: dict[str, Any] | None = None,
        title: str = "",
        **kwargs: Any,
    ) -> None:
        self._author = author
        self._source = source
        self._language = language
        self._version = version
        self._tags = tuple(tags) if tags else ()
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or self._created_at
        self._extra = dict(extra) if extra else {}
        self._title = title or str(self._extra.get("title", ""))
        if kwargs:
            self._extra.update(kwargs)

    @property
    def title(self) -> str:
        """Return the document title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def author(self) -> str:
        """Return the document author."""
        return self._author

    @property
    def source(self) -> str:
        """Return the document source."""
        return self._source

    @property
    def language(self) -> str:
        """Return the document language."""
        return self._language

    @property
    def version(self) -> str:
        """Return the document version."""
        return self._version

    @property
    def tags(self) -> tuple[str, ...]:
        """Return the document tags."""
        return self._tags

    @property
    def created_at(self) -> datetime:
        """Return creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Return last modification timestamp."""
        return self._updated_at

    @property
    def extra(self) -> dict[str, Any]:
        """Return arbitrary custom metadata attributes."""
        return self._extra

    @property
    def custom(self) -> dict[str, Any]:
        """Alias for extra metadata dictionary."""
        return self._extra


    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return {
            "title": self._title,
            "author": self._author,
            "source": self._source,
            "language": self._language,
            "version": self._version,
            "tags": list(self._tags),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "extra": self._extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeMetadata:
        """Deserialize metadata from dictionary."""
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else None
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else None
        )
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            source=data.get("source", ""),
            language=data.get("language", ""),
            version=data.get("version", ""),
            tags=tuple(data.get("tags", ())),
            created_at=created_at,
            updated_at=updated_at,
            extra=data.get("extra", {}),
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"author={self.author!r}, "
            f"source={self.source!r}, "
            f"language={self.language!r}, "
            f"version={self.version!r}, "
            f"tags={self.tags!r}"
            f")"
        )


# Canonical alias
Metadata = KnowledgeMetadata

__all__ = [
    "KnowledgeMetadata",
    "Metadata",
]
