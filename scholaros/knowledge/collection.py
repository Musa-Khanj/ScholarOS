"""
ScholarOS Knowledge Collection.

Represents a collection of knowledge documents with lifecycle and batch operations:
add, remove, get, update, merge, clone, export, and import.
"""

from __future__ import annotations

import json
from typing import Any, Iterator

from scholaros.knowledge.document import KnowledgeDocument


class _ImportJsonDescriptor:
    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return lambda json_str: owner.from_dict(json.loads(json_str))  # type: ignore
        return lambda json_str: instance._import_json_instance(json_str)


class KnowledgeCollection:
    """
    Represents a collection of knowledge documents.
    """

    def __init__(
        self,
        name: str = "default",
        description: str = "",
        id: str | None = None,
    ) -> None:
        """
        Initialize the knowledge collection.
        """
        self._id = id or name
        self._name = name or self._id
        self._description = description
        self._documents: dict[str, KnowledgeDocument] = {}

    @property
    def id(self) -> str:
        """Return collection identifier."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def name(self) -> str:
        """Return collection name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def description(self) -> str:
        """Return collection description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    def document_count(self) -> int:
        """Return the number of documents in this collection."""
        return len(self._documents)

    @classmethod
    def create(cls, name: str, description: str = "", id: str | None = None) -> KnowledgeCollection:
        """Factory method to construct a named collection."""
        return cls(name=name, description=description, id=id)

    def add(self, document: KnowledgeDocument) -> None:
        """
        Add a document to the collection.
        """
        self._documents[document.identifier] = document

    def add_document(self, document: KnowledgeDocument) -> None:
        """Alias for add."""
        self.add(document)

    def remove(self, identifier: str) -> None:
        """
        Remove a document from the collection.
        """
        self._documents.pop(identifier, None)

    def remove_document(self, identifier: str) -> None:
        """Alias for remove."""
        self.remove(identifier)

    def update(self, document: KnowledgeDocument) -> None:
        """
        Update an existing document in the collection.
        """
        self._documents[document.identifier] = document

    def get(self, identifier: str) -> KnowledgeDocument | None:
        """
        Return a document from the collection.
        """
        return self._documents.get(identifier)

    def get_document(self, identifier: str) -> KnowledgeDocument | None:
        """Alias for get."""
        return self.get(identifier)

    def contains(self, identifier: str) -> bool:
        """
        Return whether a document exists.
        """
        return identifier in self._documents

    def has_document(self, identifier: str) -> bool:
        """Alias for contains."""
        return self.contains(identifier)

    def identifiers(self) -> tuple[str, ...]:
        """
        Return all document identifiers.
        """
        return tuple(self._documents.keys())

    def values(self) -> tuple[KnowledgeDocument, ...]:
        """
        Return all documents.
        """
        return tuple(self._documents.values())

    def items(self) -> tuple[tuple[str, KnowledgeDocument], ...]:
        """
        Return all document items.
        """
        return tuple(self._documents.items())

    def get_chunks(self) -> list[Any]:
        """
        Return all chunks across all documents in this collection.
        """
        chunks: list[Any] = []
        for doc in self._documents.values():
            chunks.extend(doc.chunks)
        return chunks

    def clear(self) -> None:
        """
        Remove every document from the collection.
        """
        self._documents.clear()

    def merge(
        self,
        other: KnowledgeCollection,
        new_id: str | None = None,
        new_name: str | None = None,
    ) -> KnowledgeCollection:
        """
        Merge another collection into this collection or a new collection.
        """
        target = KnowledgeCollection(
            id=new_id or self.id,
            name=new_name or self.name,
            description=self.description,
        )
        for doc in self.values():
            target.add(doc)
        for doc in other.values():
            target.add(doc)
        return target

    def clone(self, new_id: str | None = None, new_name: str | None = None) -> KnowledgeCollection:
        """
        Create an independent deep copy of this collection.
        """
        target_id = new_id or f"{self.id}_copy"
        target_name = new_name or f"{self.name}_copy"
        cloned = KnowledgeCollection(id=target_id, name=target_name, description=self.description)
        for doc in self._documents.values():
            cloned.add(KnowledgeDocument.from_dict(doc.to_dict()))
        return cloned

    def export_dict(self) -> dict[str, Any]:
        """Export collection contents to dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "documents": [doc.to_dict() for doc in self._documents.values()],
        }

    def export_json(self, indent: int | None = 2) -> str:
        """Export collection contents to JSON string."""
        return json.dumps(self.export_dict(), indent=indent)

    def import_dict(self, data: dict[str, Any]) -> None:
        """Import documents into this collection from dictionary."""
        if "id" in data and not self._id:
            self._id = data["id"]
        if "name" in data and not self._name:
            self._name = data["name"]
        if "description" in data and not self._description:
            self._description = data["description"]
        for doc_data in data.get("documents", []):
            self.add(KnowledgeDocument.from_dict(doc_data))

    def _import_json_instance(self, json_str: str) -> None:
        """Import documents into this collection from JSON string."""
        data = json.loads(json_str)
        self.import_dict(data)

    import_json = _ImportJsonDescriptor()

    @classmethod
    def from_json(cls, json_str: str) -> KnowledgeCollection:
        """Construct KnowledgeCollection from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeCollection:
        """Construct KnowledgeCollection from exported dictionary."""
        coll = cls(
            id=data.get("id"),
            name=data.get("name", "default"),
            description=data.get("description", ""),
        )
        coll.import_dict(data)
        return coll

    def __contains__(self, identifier: str) -> bool:
        """
        Return whether the supplied identifier exists.
        """
        return self.contains(identifier)

    def __iter__(self) -> Iterator[KnowledgeDocument]:
        """
        Iterate over the stored documents.
        """
        return iter(self._documents.values())

    def __len__(self) -> int:
        """
        Return the number of documents.
        """
        return len(self._documents)

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the collection.
        """
        return f"{self.__class__.__name__}(documents={len(self)})"


# Canonical alias
Collection = KnowledgeCollection

__all__ = [
    "Collection",
    "KnowledgeCollection",
]
