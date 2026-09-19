"""
ScholarOS Knowledge Storage Layer.

Provides an abstract storage interface and reference in-memory implementation
designed for pluggable persistence backends (SQLite, DuckDB, PostgreSQL, Chroma, FAISS, LanceDB).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scholaros.knowledge.chunk import Chunk
    from scholaros.knowledge.collection import KnowledgeCollection
    from scholaros.knowledge.document import KnowledgeDocument


class KnowledgeStorage(ABC):
    """
    Abstract storage backend for knowledge documents, chunks, and collections.
    """

    @abstractmethod
    def save_document(self, document: KnowledgeDocument, collection_name: str = "default") -> None:
        """Persist or update a document."""

    @abstractmethod
    def get_document(self, identifier: str, collection_name: str = "default") -> KnowledgeDocument | None:
        """Retrieve a document by identifier."""

    @abstractmethod
    def delete_document(self, identifier: str, collection_name: str = "default") -> bool:
        """Delete a document by identifier."""

    @abstractmethod
    def list_documents(self, collection_name: str = "default") -> list[KnowledgeDocument]:
        """List all documents in a collection."""

    @abstractmethod
    def save_chunk(self, chunk: Chunk, collection_name: str = "default") -> None:
        """Persist or update a chunk."""

    @abstractmethod
    def get_chunk(self, identifier: str) -> Chunk | None:
        """Retrieve a chunk by identifier."""

    @abstractmethod
    def get_chunks_for_document(self, document_id: str) -> list[Chunk]:
        """Retrieve all chunks belonging to a document."""

    @abstractmethod
    def delete_chunks_for_document(self, document_id: str) -> int:
        """Delete all chunks belonging to a document."""

    @abstractmethod
    def save_collection(self, collection: KnowledgeCollection) -> None:
        """Persist an entire collection and its documents."""

    @abstractmethod
    def get_collection(self, name: str) -> KnowledgeCollection | None:
        """Retrieve a collection by name."""

    @abstractmethod
    def delete_collection(self, name: str) -> bool:
        """Delete a collection and its associated documents."""

    @abstractmethod
    def list_collections(self) -> list[str]:
        """Return names of all stored collections."""

    @abstractmethod
    def clear(self) -> None:
        """Wipe all data from storage."""


class InMemoryStorage(KnowledgeStorage):
    """
    Thread-safe in-memory reference implementation of KnowledgeStorage.
    """

    def __init__(self) -> None:
        from scholaros.knowledge.collection import KnowledgeCollection

        self._collections: dict[str, KnowledgeCollection] = {
            "default": KnowledgeCollection(name="default")
        }
        self._chunks: dict[str, Chunk] = {}
        self._doc_to_chunks: dict[str, set[str]] = {}
        self._lock = Lock()

    def save_document(
        self,
        document: KnowledgeDocument,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> None:
        key = collection_id or collection_name
        with self._lock:
            if key not in self._collections:
                from scholaros.knowledge.collection import KnowledgeCollection

                self._collections[key] = KnowledgeCollection(id=key, name=key)

            self._collections[key].add(document)
            # Index document chunks if present
            for chunk in document.chunks:
                self._chunks[chunk.identifier] = chunk
                self._doc_to_chunks.setdefault(document.identifier, set()).add(chunk.identifier)

    def get_document(
        self,
        identifier: str,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> KnowledgeDocument | None:
        key = collection_id or collection_name
        with self._lock:
            coll = self._collections.get(key)
            if coll and coll.contains(identifier):
                return coll.get(identifier)
            # Global fallback across all collections
            for c in self._collections.values():
                doc = c.get(identifier)
                if doc is not None:
                    return doc
            return None

    def delete_document(
        self,
        identifier: str,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> bool:
        key = collection_id or collection_name
        with self._lock:
            deleted = False
            coll = self._collections.get(key)
            if coll and coll.contains(identifier):
                coll.remove(identifier)
                deleted = True
            else:
                for c in self._collections.values():
                    if c.contains(identifier):
                        c.remove(identifier)
                        deleted = True
                        break

            if deleted:
                chunk_ids = self._doc_to_chunks.pop(identifier, set())
                for cid in chunk_ids:
                    self._chunks.pop(cid, None)
                return True
            return False

    def list_documents(
        self,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> list[KnowledgeDocument]:
        key = collection_id or collection_name
        with self._lock:
            coll = self._collections.get(key)
            return list(coll.values()) if coll else []

    def save_chunk(self, chunk: Chunk, collection_name: str = "default") -> None:
        with self._lock:
            self._chunks[chunk.identifier] = chunk
            self._doc_to_chunks.setdefault(chunk.document_id, set()).add(chunk.identifier)

    def get_chunk(self, identifier: str) -> Chunk | None:
        with self._lock:
            return self._chunks.get(identifier)

    def get_chunks(self, document_id: str) -> list[Chunk]:
        """Alias for get_chunks_for_document."""
        return self.get_chunks_for_document(document_id)

    def get_chunks_for_document(self, document_id: str) -> list[Chunk]:
        with self._lock:
            cids = self._doc_to_chunks.get(document_id, set())
            return [self._chunks[cid] for cid in sorted(cids) if cid in self._chunks]

    def count_documents(
        self,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> int:
        """Count total documents in a collection."""
        key = collection_id or collection_name
        with self._lock:
            coll = self._collections.get(key)
            return len(coll) if coll else 0

    def count_chunks(
        self,
        collection_name: str = "default",
        collection_id: str | None = None,
    ) -> int:
        """Count total chunks across documents in a collection."""
        key = collection_id or collection_name
        with self._lock:
            coll = self._collections.get(key)
            if not coll:
                return 0
            count = 0
            for doc in coll.values():
                count += len(self._doc_to_chunks.get(doc.identifier, set()))
            return count

    def delete_chunks_for_document(self, document_id: str) -> int:
        with self._lock:
            cids = self._doc_to_chunks.pop(document_id, set())
            count = 0
            for cid in cids:
                if self._chunks.pop(cid, None) is not None:
                    count += 1
            return count

    def save_collection(self, collection: KnowledgeCollection) -> None:
        key = collection.id or collection.name
        with self._lock:
            self._collections[key] = collection
            if collection.name and collection.name != key:
                self._collections[collection.name] = collection
            for doc in collection.values():
                for chunk in doc.chunks:
                    self._chunks[chunk.identifier] = chunk
                    self._doc_to_chunks.setdefault(doc.identifier, set()).add(chunk.identifier)

    def get_collection(self, name: str) -> KnowledgeCollection | None:
        with self._lock:
            return self._collections.get(name)

    def delete_collection(self, name: str) -> bool:
        with self._lock:
            coll = self._collections.pop(name, None)
            if coll:
                # Remove alias if present
                for k, v in list(self._collections.items()):
                    if v is coll:
                        self._collections.pop(k, None)
                for doc in coll.values():
                    chunk_ids = self._doc_to_chunks.pop(doc.identifier, set())
                    for cid in chunk_ids:
                        self._chunks.pop(cid, None)
                return True
            return False

    def list_collections(self) -> list[str]:
        with self._lock:
            seen_ids: set[int] = set()
            result: list[str] = []
            for name, col in self._collections.items():
                if id(col) not in seen_ids:
                    seen_ids.add(id(col))
                    result.append(name)
            return sorted(result)

    def clear(self) -> None:
        with self._lock:
            self._collections.clear()
            self._chunks.clear()
            self._doc_to_chunks.clear()
            self._doc_to_chunks.clear()


__all__ = [
    "InMemoryStorage",
    "KnowledgeStorage",
]
