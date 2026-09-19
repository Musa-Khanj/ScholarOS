"""
ScholarOS Knowledge Serializer.

Handles serialization and deserialization of documents, chunks, and collections
between objects, JSON, and dictionaries.
"""

from __future__ import annotations

import json
from typing import Any

from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument


class DocumentSerializer:
    """
    Serializes and deserializes KnowledgeDocument instances.
    """

    @staticmethod
    def to_dict(document: KnowledgeDocument) -> dict[str, Any]:
        """Convert document to dictionary."""
        return document.to_dict()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> KnowledgeDocument:
        """Construct document from dictionary."""
        return KnowledgeDocument.from_dict(data)

    @staticmethod
    def to_json(document: KnowledgeDocument, indent: int | None = 2) -> str:
        """Convert document to JSON string."""
        return json.dumps(document.to_dict(), indent=indent)

    @staticmethod
    def from_json(json_str: str) -> KnowledgeDocument:
        """Construct document from JSON string."""
        return KnowledgeDocument.from_dict(json.loads(json_str))


class CollectionSerializer:
    """
    Serializes and deserializes KnowledgeCollection instances.
    """

    @staticmethod
    def to_dict(collection: KnowledgeCollection) -> dict[str, Any]:
        """Convert collection to dictionary."""
        return collection.export_dict()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> KnowledgeCollection:
        """Construct collection from dictionary."""
        return KnowledgeCollection.from_dict(data)

    @staticmethod
    def to_json(collection: KnowledgeCollection, indent: int | None = 2) -> str:
        """Convert collection to JSON string."""
        return collection.export_json(indent=indent)

    @staticmethod
    def from_json(json_str: str) -> KnowledgeCollection:
        """Construct collection from JSON string."""
        coll = KnowledgeCollection()
        coll.import_json(json_str)
        return coll


__all__ = [
    "CollectionSerializer",
    "DocumentSerializer",
]
