"""
ScholarOS Knowledge Manager.

High-level manager for knowledge collections, document pipelines, search indexing,
statistics, diagnostics, and event dispatch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.diagnostics import DiagnosticReport, KnowledgeDiagnostics
from scholaros.knowledge.events import (
    CollectionCreated,
    CollectionDeleted,
    CollectionIndexed,
    DocumentAdded,
    DocumentRemoved,
    DocumentUpdated,
    KnowledgeEvent,
    SearchCompleted,
)
from scholaros.knowledge.exceptions import DuplicateDocumentError
from scholaros.knowledge.index import InvertedIndex
from scholaros.knowledge.lifecycle import DocumentStatus, DuplicatePolicy
from scholaros.knowledge.registry import KnowledgeRegistry
from scholaros.knowledge.search import SearchEngine, SearchQuery, SearchResponse
from scholaros.knowledge.statistics import KnowledgeStatistics, calculate_statistics
from scholaros.knowledge.storage import InMemoryStorage, KnowledgeStorage

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider
    from scholaros.embeddings.generator import EmbeddingGenerator
    from scholaros.embeddings.provider import EmbeddingProvider
    from scholaros.embeddings.vector_store import VectorStore
    from scholaros.events.bus import EventBus
    from scholaros.knowledge.document import KnowledgeDocument
    from scholaros.retrieval.manager import RetrievalManager
    from scholaros.retrieval.pipeline import RetrievalPipeline


class KnowledgeManager:
    """
    Orchestrates knowledge storage, collections, document pipelines, and search queries.
    """

    def __init__(
        self,
        registry: KnowledgeRegistry | None = None,
        storage: KnowledgeStorage | None = None,
        index: InvertedIndex | None = None,
        event_bus: EventBus | None = None,
        vector_store: VectorStore | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        ai_provider: AIProvider | None = None,
    ) -> None:
        """
        Initialize the knowledge manager.
        """
        self._registry = registry if registry is not None else KnowledgeRegistry()
        self.storage = storage if storage is not None else InMemoryStorage()
        self.index = index if index is not None else InvertedIndex()
        self.event_bus = event_bus
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.embedding_provider = embedding_provider
        self.ai_provider = ai_provider
        self.search_engine = SearchEngine(storage=self.storage, index=self.index)
        self.diagnostics_runner = KnowledgeDiagnostics()

    @property
    def registry(self) -> KnowledgeRegistry:
        """Return the knowledge registry."""
        return self._registry

    # ---------------------------------------------------------
    # Backward-compatible Collection Management
    # ---------------------------------------------------------

    def add(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """Add a knowledge collection."""
        collection.name = name
        self._registry.add(name, collection)
        self.storage.save_collection(collection)
        self._publish(CollectionCreated(collection_name=name))

    def remove(
        self,
        name: str,
    ) -> None:
        """Remove a registered knowledge collection."""
        self._registry.remove(name)
        self.storage.delete_collection(name)
        self._publish(CollectionDeleted(collection_name=name))

    def get(
        self,
        name: str,
    ) -> KnowledgeCollection:
        """Return a registered knowledge collection."""
        return self._registry.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """Return whether a knowledge collection is registered."""
        return self._registry.contains(name)

    def names(self) -> tuple[str, ...]:
        """Return registered knowledge collection names."""
        return self._registry.names()

    def clear(self) -> None:
        """Remove all registered knowledge collections."""
        self._registry.clear()
        self.storage.clear()
        self.index.clear()

    # ---------------------------------------------------------
    # Enhanced Collection Operations
    # ---------------------------------------------------------

    def create_collection(
        self,
        name_or_id: str = "default",
        description: str = "",
        name: str | None = None,
        id: str | None = None,
    ) -> KnowledgeCollection:
        """Create and register a new collection."""
        actual_id = id or name_or_id
        actual_name = name or name_or_id
        coll = KnowledgeCollection.create(id=actual_id, name=actual_name, description=description)
        self.add(actual_name, coll)
        if actual_id != actual_name:
            self.storage.save_collection(coll)
        return coll

    def get_or_create_collection(self, name: str, description: str = "") -> KnowledgeCollection:
        """Retrieve collection by name, creating it if absent."""
        if self.contains(name):
            return self.get(name)
        return self.create_collection(name, description)

    def delete_collection(self, name: str) -> bool:
        """Delete collection by name. Returns True if removed."""
        if self.contains(name):
            self.remove(name)
            return True
        return False

    def merge_collections(self, target_name: str, source_names: list[str]) -> KnowledgeCollection:
        """Merge documents from multiple source collections into target collection."""
        target = self.get_or_create_collection(target_name)
        for s_name in source_names:
            if self.contains(s_name):
                source = self.get(s_name)
                target.merge(source)
        self.storage.save_collection(target)
        return target

    def clone_collection(self, source_name: str, new_name: str) -> KnowledgeCollection:
        """Create an independent copy of a collection."""
        source = self.get(source_name)
        cloned = source.clone(new_name=new_name)
        self.add(new_name, cloned)
        return cloned

    # ---------------------------------------------------------
    # Document Pipeline & Indexing
    # ---------------------------------------------------------

    def add_document(
        self,
        document: KnowledgeDocument,
        collection_name: str = "default",
        auto_chunk: bool = True,
        collection_id: str | None = None,
        duplicate_policy: DuplicatePolicy | str = DuplicatePolicy.REPLACE,
    ) -> KnowledgeDocument:
        """
        Add a document to a collection, chunking, embedding into VectorStore, and indexing it.
        """
        key = collection_id or collection_name
        policy = (
            DuplicatePolicy(duplicate_policy)
            if isinstance(duplicate_policy, str)
            else duplicate_policy
        )

        coll = self.get_or_create_collection(key)
        existing_doc = coll.get(document.identifier)
        if existing_doc is None:
            # Check by content hash across collection documents
            for doc in coll.values():
                if hasattr(doc, "content_hash") and doc.content_hash == document.content_hash:
                    existing_doc = doc
                    break

        if existing_doc is not None:
            if policy == DuplicatePolicy.ERROR:
                raise DuplicateDocumentError(
                    f"Document '{document.identifier}' (or identical content) already exists in collection '{key}'."
                )
            elif policy == DuplicatePolicy.SKIP:
                return existing_doc
            elif policy == DuplicatePolicy.REPLACE:
                self.remove_document(existing_doc.identifier, collection_name=key)

        coll.add(document)

        if auto_chunk and not document.chunks:
            from scholaros.knowledge.loader import KnowledgeLoader

            chunks = KnowledgeLoader.chunk_text(
                document_id=document.identifier,
                text=document.content,
            )
            document.set_chunks(chunks)

        self.storage.save_document(document, collection_name=key)
        self.index_document(document, collection_name=key)

        document.status = DocumentStatus.INDEXED
        self._publish(DocumentAdded(document_id=document.identifier, collection_name=key))
        return document

    def update_document(
        self,
        document: KnowledgeDocument,
        collection_name: str = "default",
        auto_chunk: bool = True,
        collection_id: str | None = None,
    ) -> KnowledgeDocument:
        """Update an existing document, re-chunking, re-embedding, and re-indexing."""
        key = collection_id or collection_name
        self.remove_document(document.identifier, collection_name=key)
        doc = self.add_document(
            document=document,
            collection_name=key,
            auto_chunk=auto_chunk,
            duplicate_policy=DuplicatePolicy.REPLACE,
        )
        self._publish(DocumentUpdated(document_id=document.identifier, collection_name=key))
        return doc

    def remove_document(self, document_id: str, collection_name: str = "default") -> bool:
        """Remove a document and its chunks from storage, inverted index, and vector store."""
        coll = self._registry.get(collection_name) if self.contains(collection_name) else None
        existed_in_coll = coll.contains(document_id) if coll else False
        if coll and existed_in_coll:
            coll.remove(document_id)

        # Remove chunks from inverted index
        chunks = self.storage.get_chunks_for_document(document_id)
        for c in chunks:
            self.index.remove_chunk(c.identifier)

        # Remove chunk embeddings from vector store if present
        if self.vector_store is not None:
            try:
                all_embs = list(self.vector_store.embeddings())
                for emb in all_embs:
                    meta = getattr(emb, "metadata", {})
                    if meta.get("document_id") == document_id:
                        self.vector_store.remove(emb)
            except Exception:
                pass

        removed = self.storage.delete_document(document_id, collection_name=collection_name)
        if existed_in_coll:
            removed = True
            # Ensure storage chunks are cleaned up if storage shared the collection
            if hasattr(self.storage, "_doc_to_chunks") and hasattr(self.storage, "_chunks"):
                chunk_ids = self.storage._doc_to_chunks.pop(document_id, set())
                for cid in chunk_ids:
                    self.storage._chunks.pop(cid, None)

        if removed:
            self._publish(DocumentRemoved(document_id=document_id, collection_name=collection_name))
        return removed

    def index_document(
        self,
        document: KnowledgeDocument,
        collection_name: str = "default",
    ) -> None:
        """Index all chunks of a document into InvertedIndex and VectorStore."""
        chunks = document.chunks or self.storage.get_chunks_for_document(document.identifier)
        for chunk in chunks:
            meta = document.metadata.to_dict()
            meta.update(chunk.metadata)
            meta["title"] = document.title
            meta["collection"] = collection_name
            meta["document_id"] = document.identifier
            meta["chunk_id"] = chunk.identifier
            self.index.add_chunk(chunk, metadata=meta)

            # Store in VectorStore if vector_store and embedding generator/provider exist
            if self.vector_store is not None:
                self._embed_and_store_chunk(chunk, collection_name, document)

        document.status = DocumentStatus.INDEXED

    def _embed_and_store_chunk(
        self,
        chunk: Any,
        collection_name: str,
        document: KnowledgeDocument,
    ) -> None:
        """Embed a chunk and store it in the VectorStore."""
        assert self.vector_store is not None
        from scholaros.embeddings.embedding import Embedding

        vector: list[float] | None = None
        if self.embedding_generator is not None:
            emb_obj = self.embedding_generator.generate(chunk.content)
            vector = list(emb_obj.vector)
        elif self.embedding_provider is not None:
            emb_obj = self.embedding_provider.embed(chunk.content)
            vector = list(emb_obj.vector)
        elif self.ai_provider is not None and hasattr(self.ai_provider, "embed"):
            try:
                from scholaros.ai.embedding import EmbeddingRequest

                emb_req = EmbeddingRequest.from_text(chunk.content)
                emb_resp = self.ai_provider.embed(emb_req)
                vector = list(emb_resp.vector)
            except Exception:
                pass

        if vector is not None:
            emb_entry = Embedding(
                text=chunk.content,
                vector=vector,
                metadata={
                    "chunk_id": chunk.identifier,
                    "document_id": document.identifier,
                    "collection": collection_name,
                    "title": document.title,
                    "start_char": getattr(chunk, "start_char", 0),
                    "end_char": getattr(chunk, "end_char", 0),
                    "index": getattr(chunk, "index", 0),
                },
            )
            self.vector_store.add(emb_entry)

    def index_collection(self, collection_name: str) -> int:
        """Re-index all documents in a collection into both inverted index and vector store."""
        docs = self.storage.list_documents(collection_name)
        chunk_count = 0
        for doc in docs:
            self.index_document(doc, collection_name=collection_name)
            chunk_count += len(doc.chunks)

        self._publish(CollectionIndexed(collection_name=collection_name, chunk_count=chunk_count))
        return chunk_count

    def reindex_all(self) -> int:
        """Re-index all documents across all collections."""
        total_chunks = 0
        for name in self.names():
            total_chunks += self.index_collection(name)
        return total_chunks

    def create_retrieval_manager(self, **kwargs: Any) -> RetrievalManager:
        """Factory creating a RetrievalManager wired to this KnowledgeManager's storage and vector store."""
        from scholaros.retrieval.manager import RetrievalManager

        params: dict[str, Any] = {
            "storage": self.storage,
            "vector_store": self.vector_store,
            "embedding_generator": self.embedding_generator,
            "embedding_provider": self.embedding_provider,
            "ai_provider": self.ai_provider,
            "event_bus": self.event_bus,
        }
        params.update(kwargs)
        return RetrievalManager(**params)

    def create_retrieval_pipeline(
        self,
        strategy_name: str = "hybrid",
        **kwargs: Any,
    ) -> RetrievalPipeline:
        """Factory creating a RetrievalPipeline wired to this KnowledgeManager."""
        from scholaros.retrieval.pipeline import RetrievalPipeline

        manager = self.create_retrieval_manager()
        strategy = manager.strategies.get(strategy_name)
        retriever = getattr(strategy, "retriever", None)
        if retriever is None:
            from scholaros.retrieval.retriever import Retriever

            retriever = Retriever(manager, name=strategy_name)
        return RetrievalPipeline(retriever=retriever, **kwargs)

    # ---------------------------------------------------------
    # Search API
    # ---------------------------------------------------------

    def search(
        self,
        query: str | SearchQuery,
        collection_name: str | None = None,
        limit: int = 10,
        collection_id: str | None = None,
        **kwargs: Any,
    ) -> SearchResponse:
        """Execute a knowledge search query."""
        key = collection_id or collection_name
        response = self.search_engine.search(
            query=query,
            collection_name=key,
            limit=limit,
            **kwargs,
        )
        q_str = query if isinstance(query, str) else query.query
        self._publish(
            SearchCompleted(
                query=q_str,
                total_results=response.total,
                latency_ms=response.latency_ms,
            )
        )
        return response

    # ---------------------------------------------------------
    # Statistics & Diagnostics
    # ---------------------------------------------------------

    def statistics(self) -> KnowledgeStatistics:
        """Calculate and return real-time knowledge subsystem statistics."""
        return calculate_statistics(storage=self.storage, index=self.index)

    def get_statistics(self, collection_name: str | None = None) -> KnowledgeStatistics:
        """Alias for statistics."""
        if collection_name and self.contains(collection_name):
            return calculate_statistics(target=self.get(collection_name), index=self.index)
        return self.statistics()

    def run_diagnostics(self, collection_name: str | None = None) -> DiagnosticReport:
        """Execute system integrity checks."""
        if collection_name and self.contains(collection_name):
            coll = self.get(collection_name)
            return self.diagnostics_runner.run(coll)
        return self.diagnostics_runner.run_checks(storage=self.storage)

    # ---------------------------------------------------------
    # Event Publication
    # ---------------------------------------------------------

    def _publish(self, event: KnowledgeEvent) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(event)
            except Exception:
                pass

    def __len__(self) -> int:
        """Return the number of registered collections."""
        return len(self._registry)

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the knowledge manager."""
        return f"{self.__class__.__name__}(collections={len(self)})"


# Canonical alias
Manager = KnowledgeManager

__all__ = [
    "KnowledgeManager",
    "Manager",
]
