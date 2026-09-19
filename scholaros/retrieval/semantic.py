"""
ScholarOS Semantic Retriever.

Performs dense vector semantic retrieval using:
1. Embeddings subsystem (EmbeddingGenerator, EmbeddingProvider, VectorStore, SimilarityMetric)
2. Unified AIProvider embeddings and KnowledgeStorage chunks
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.contracts.retrieval import VectorRetrieverContract
from scholaros.retrieval.exceptions import RetrievalEmbeddingError
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider
    from scholaros.embeddings.generator import EmbeddingGenerator
    from scholaros.embeddings.provider import EmbeddingProvider
    from scholaros.embeddings.similarity_metric import SimilarityMetric
    from scholaros.embeddings.vector_store import VectorStore
    from scholaros.knowledge.storage import KnowledgeStorage


class SemanticRetriever(BaseRetriever, VectorRetrieverContract):
    """
    Dense semantic retriever supporting both VectorStore/EmbeddingGenerator architecture
    and unified AIProvider/KnowledgeStorage backends.
    """

    def __init__(
        self,
        ai_provider: AIProvider | None = None,
        storage: KnowledgeStorage | None = None,
        embedding_model: str | None = None,
        generator: EmbeddingGenerator | None = None,
        vector_store: VectorStore | None = None,
        provider: EmbeddingProvider | None = None,
        metric: SimilarityMetric | None = None,
        name: str = "SemanticRetriever",
    ) -> None:
        super().__init__(name=name)
        self._ai_provider = ai_provider
        self._storage = storage
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._metric = metric

        self._generator: EmbeddingGenerator | None
        if generator is not None:
            self._generator = generator
        elif provider is not None:
            from scholaros.embeddings.generator import EmbeddingGenerator as Gen
            self._generator = Gen(provider=provider)
        else:
            self._generator = None

    @property
    def ai_provider(self) -> AIProvider | None:
        """Return the underlying AI provider."""
        return self._ai_provider

    @property
    def storage(self) -> KnowledgeStorage | None:
        """Return the underlying knowledge storage."""
        return self._storage

    @property
    def vector_store(self) -> VectorStore | None:
        """Return the backing vector store."""
        return self._vector_store

    @property
    def generator(self) -> EmbeddingGenerator | None:
        """Return the embedding generator."""
        return self._generator

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for search query."""
        if self._generator is not None:
            emb = self._generator.generate(text)
            return emb.vector

        if self._ai_provider is None:
            raise RetrievalEmbeddingError("No AIProvider or EmbeddingGenerator configured on SemanticRetriever.")
        try:
            req = EmbeddingRequest.from_text(text, model=self._embedding_model)
            resp = self._ai_provider.embed(req)
            return resp.vector
        except Exception as e:
            raise RetrievalEmbeddingError(f"Failed to generate query embedding: {e}") from e

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Execute dense vector search against VectorStore or KnowledgeStorage.
        """
        # Path 1: Backed by VectorStore
        if self._vector_store is not None:
            return self._retrieve_from_vector_store(query)

        # Path 2: Backed by AIProvider + KnowledgeStorage
        if self._ai_provider is not None and self._storage is not None:
            return self._retrieve_from_storage(query)

        return []

    def _retrieve_from_vector_store(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute semantic search using the VectorStore."""
        assert self._vector_store is not None
        from scholaros.embeddings.cosine_similarity import CosineSimilarity
        from scholaros.embeddings.embedding import Embedding

        if self._generator is not None:
            query_emb = self._generator.generate(query.text)
        else:
            query_vector = self.embed_query(query.text)
            query_emb = Embedding(text=query.text, vector=query_vector)

        matches = self._vector_store.search(query_emb, limit=max(query.limit * 2, 10))
        metric_candidate = self._metric or getattr(self._vector_store, "metric", None)
        metric_obj: SimilarityMetric = metric_candidate if metric_candidate is not None else CosineSimilarity()

        results: list[RetrievalResult] = []
        target_collections = set(query.collections) if query.collections else None

        for emb in matches:
            try:
                score = metric_obj.calculate(query_emb, emb)
            except Exception:
                score = 1.0

            if score < query.min_score:
                continue

            meta = emb.metadata
            col = meta.get("collection")
            if target_collections is not None and col and col not in target_collections:
                continue

            results.append(
                RetrievalResult.from_embedding(
                    embedding=emb,
                    score=round(score, 4),
                    collection=str(col) if col else None,
                )
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[: query.limit]

    def _retrieve_from_storage(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute semantic search against KnowledgeStorage chunks."""
        assert self._ai_provider is not None and self._storage is not None

        query_vector = self.embed_query(query.text)
        if not query_vector:
            return []

        collections = (
            query.collections
            if query.collections
            else self._storage.list_collections()
        )
        if not collections:
            collections = ["default"]

        results: list[RetrievalResult] = []

        for col_name in collections:
            docs = self._storage.list_documents(col_name)
            for doc in docs:
                chunks = self._storage.get_chunks_for_document(doc.identifier)
                for chunk in chunks:
                    chunk_vec = chunk.embedding
                    if chunk_vec is None:
                        try:
                            c_resp = self._ai_provider.embed(
                                EmbeddingRequest.from_text(chunk.content, model=self._embedding_model)
                            )
                            chunk_vec = c_resp.vector
                            chunk.embedding = chunk_vec
                        except Exception:
                            continue

                    similarity = EmbeddingResponse.cosine_similarity(query_vector, chunk_vec)
                    if similarity >= query.min_score:
                        results.append(
                            RetrievalResult.from_chunk(
                                chunk=chunk,
                                score=round(similarity, 4),
                                collection=col_name,
                            )
                        )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[: query.limit]

    def retrieve_vectors(
        self,
        query_vector: list[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[RetrievalResult]:
        """Retrieve candidates directly using an embedding vector."""
        if self._vector_store is None:
            return []

        from scholaros.embeddings.cosine_similarity import CosineSimilarity
        from scholaros.embeddings.embedding import Embedding

        query_emb = Embedding(text="", vector=query_vector)
        matches = self._vector_store.search(query_emb, limit=limit)
        metric_candidate = self._metric or getattr(self._vector_store, "metric", None)
        metric_obj: SimilarityMetric = metric_candidate if metric_candidate is not None else CosineSimilarity()

        results: list[RetrievalResult] = []
        for emb in matches:
            try:
                score = metric_obj.calculate(query_emb, emb)
            except Exception:
                score = 1.0

            if score >= min_score:
                results.append(RetrievalResult.from_embedding(emb, score=round(score, 4)))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]


class VectorStoreRetriever(SemanticRetriever):
    """
    Dedicated retriever adapter connecting a VectorStore and EmbeddingGenerator.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        generator: EmbeddingGenerator | None = None,
        provider: EmbeddingProvider | None = None,
        metric: SimilarityMetric | None = None,
        name: str = "VectorStoreRetriever",
    ) -> None:
        super().__init__(
            vector_store=vector_store,
            generator=generator,
            provider=provider,
            metric=metric,
            name=name,
        )


__all__ = [
    "SemanticRetriever",
    "VectorStoreRetriever",
]
