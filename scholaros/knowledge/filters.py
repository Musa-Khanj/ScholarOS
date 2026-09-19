"""
ScholarOS Knowledge Search Filters.

Provides declarative criteria for filtering knowledge queries by tags, authors, sources, and dates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from scholaros.knowledge.metadata import KnowledgeMetadata

if TYPE_CHECKING:
    from scholaros.knowledge.chunk import Chunk
    from scholaros.knowledge.document import KnowledgeDocument


@dataclass(slots=True)
class KnowledgeFilter:
    """
    Search filter criteria evaluated against document metadata.
    """

    tags: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)
    source: str | None = None
    language: str | None = None
    min_date: datetime | None = None
    max_date: datetime | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def matches(self, target: KnowledgeDocument | Chunk | KnowledgeMetadata | dict[str, Any]) -> bool:
        """
        Evaluate if target satisfies all active filter conditions.
        """
        meta_dict: dict[str, Any] = {}
        target_tags: set[str] = set()
        target_author: str = ""
        target_source: str = ""
        target_lang: str = ""
        target_date: datetime | None = None

        m: Any = getattr(target, "metadata", target)
        if isinstance(m, KnowledgeMetadata):
            meta_dict = m.to_dict()
            target_tags = set(m.tags)
            target_author = m.author.lower()
            target_source = m.source.lower()
            target_lang = m.language.lower()
            target_date = m.created_at
        elif isinstance(m, dict):
            meta_dict = m
            raw_tags = m.get("tags", [])
            target_tags = set(raw_tags) if isinstance(raw_tags, (list, set, tuple)) else set()
            target_author = str(m.get("author", "")).lower()
            target_source = str(m.get("source", "")).lower()
            target_lang = str(m.get("language", "")).lower()
            raw_date = m.get("created_at")
            if isinstance(raw_date, datetime):
                target_date = raw_date

        # Check tags (all specified tags must be present)
        if self.tags:
            required_tags = {t.lower() for t in self.tags}
            normalized_target = {t.lower() for t in target_tags}
            if not required_tags.issubset(normalized_target):
                return False

        # Check authors
        if self.authors:
            author_matches = any(a.lower() in target_author for a in self.authors)
            if not author_matches:
                return False

        # Check source
        if self.source and self.source.lower() not in target_source:
            return False

        # Check language
        if self.language and self.language.lower() != target_lang:
            return False

        # Check date range
        if target_date is not None:
            if self.min_date and target_date < self.min_date:
                return False
            if self.max_date and target_date > self.max_date:
                return False

        # Check custom metadata key-values
        for k, v in self.extra.items():
            if meta_dict.get(k) != v:
                return False

        return True


__all__ = [
    "KnowledgeFilter",
]
