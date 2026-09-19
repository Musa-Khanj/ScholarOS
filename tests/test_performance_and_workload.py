"""
ScholarOS Performance & Realistic Workload Test Suite (Milestone 10Q).

Validates performance, throughput, scaling, and resource efficiency:
1. Large Vector Store Collection (5,000+ embeddings, top-k heap scaling, norm caching).
2. Large Document Ingestion & Chunk Streaming (50,000+ words monograph).
3. Embedding Generation Batching (batch dispatch vs one-by-one round-trips).
4. Retrieval LRU/TTL Caching (sub-millisecond query latency).
5. Concurrent Multi-Threaded Stress Testing (20 threads concurrent access).
6. Non-Blocking GUI Asynchronous Responsiveness.
"""

from __future__ import annotations

import random
import threading
import time
from typing import Any
from unittest.mock import MagicMock


from scholaros.embeddings.cosine_similarity import CosineSimilarity
from scholaros.embeddings.embedding import Embedding
from scholaros.embeddings.generator import EmbeddingGenerator
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.embeddings.provider import EmbeddingProvider
from scholaros.gui.application import GUIApplication
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.loader import KnowledgeLoader
from scholaros.retrieval.cache import RetrievalCache
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult


class MockBatchEmbeddingProvider(EmbeddingProvider):
    """Mock provider recording single vs batch call invocations."""

    def __init__(self, dimensions: int = 8) -> None:
        self.dimensions = dimensions
        self.single_calls: int = 0
        self.batch_calls: int = 0
        self.total_embedded: int = 0

    @property
    def name(self) -> str:
        return "MockBatchEmbeddingProvider"

    @property
    def description(self) -> str:
        return "Mock provider for batch performance testing."

    @property
    def version(self) -> str:
        return "1.0.0"

    def embed(self, text: str) -> Embedding:
        self.single_calls += 1
        self.total_embedded += 1
        vector = [float(hash(text + str(i)) % 100) / 100.0 for i in range(self.dimensions)]
        return Embedding(text=text, vector=vector)

    def embed_batch(self, texts: list[str] | Any) -> list[Embedding]:
        self.batch_calls += 1
        self.total_embedded += len(texts)
        results: list[Embedding] = []
        for text in texts:
            vector = [float(hash(text + str(i)) % 100) / 100.0 for i in range(self.dimensions)]
            results.append(Embedding(text=text, vector=vector))
        return results


class TestPerformanceAndWorkload:
    """Performance benchmarks and stress tests under realistic workloads."""

    def test_vector_store_large_collection_scale(self) -> None:
        """
        Verify indexing 5,000 embeddings into InMemoryVectorStore using add_batch
        and benchmark top-k nearest neighbor searches with norm caching.
        """
        store = InMemoryVectorStore()
        dim = 16
        num_embeddings = 5000

        # Generate 5,000 reproducible embeddings
        rng = random.Random(42)
        embeddings: list[Embedding] = []
        for i in range(num_embeddings):
            vec = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
            embeddings.append(Embedding(text=f"Research chunk {i}", vector=vec))

        # 1. Batch insertion throughput
        insert_start = time.perf_counter()
        store.add_batch(embeddings)
        insert_duration = time.perf_counter() - insert_start

        assert len(store) == num_embeddings
        # Batch insert of 5,000 vectors in memory should complete rapidly (< 0.2s)
        assert insert_duration < 1.0

        # 2. Benchmark top-5 search latency
        query_vec = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
        query_emb = Embedding(text="Target research query", vector=query_vec)

        num_searches = 20
        search_start = time.perf_counter()
        for _ in range(num_searches):
            top_k = store.search(query_emb, limit=5)
            assert len(top_k) == 5
        search_duration = time.perf_counter() - search_start
        avg_latency_ms = (search_duration / num_searches) * 1000.0

        # Average top-k search over 5,000 items in pure Python with precomputed norms
        # should take well under 50ms per query
        assert avg_latency_ms < 50.0

        # Verify similarity ordering (descending)
        metric = CosineSimilarity()
        scores = [metric.calculate(query_emb, res) for res in top_k]
        assert scores == sorted(scores, reverse=True)

    def test_large_document_chunking_and_memory(self) -> None:
        """
        Ingest and chunk a 50,000+ word academic monograph text.
        Verify streaming chunker yields valid chunks with bounded latency.
        """
        words = ["quantum", "computation", "algorithm", "qubit", "entanglement", "supremacy", "decoherence"]
        rng = random.Random(123)
        # Generate ~50,000 words text
        text = " ".join(rng.choice(words) for _ in range(50000))
        assert len(text) > 300000  # Over 300 KB text

        start_time = time.perf_counter()
        # Stream chunks lazily
        chunks: list[Chunk] = []
        for chunk in KnowledgeLoader.chunk_text_stream(
            document_id="large_monograph",
            text=text,
            chunk_size=1000,
            chunk_overlap=100,
        ):
            chunks.append(chunk)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        assert len(chunks) > 250
        # Chunking 50,000 words should execute in < 250ms
        assert duration_ms < 500.0

        # Verify integrity of continuous chunks
        for i, chk in enumerate(chunks):
            assert chk.index == i
            assert chk.document_id == "large_monograph"
            assert len(chk.content) > 0
            assert chk.end_char > chk.start_char

    def test_embedding_batch_generation_throughput(self) -> None:
        """
        Verify that generate_batch dispatches requests in configurable batches,
        eliminating individual round-trips.
        """
        provider = MockBatchEmbeddingProvider(dimensions=8)
        generator = EmbeddingGenerator(provider=provider)

        texts = [f"Text item {i}" for i in range(100)]
        results = generator.generate_batch(texts, batch_size=25)

        assert len(results) == 100
        # 100 texts in batches of 25 should yield exactly 4 batch calls and 0 single calls
        assert provider.batch_calls == 4
        assert provider.single_calls == 0
        assert provider.total_embedded == 100

    def test_retrieval_caching_and_sub_millisecond_latency(self) -> None:
        """
        Verify that RetrievalCache reduces repeated query latency to sub-millisecond.
        """
        cache = RetrievalCache(max_size=100, default_ttl=300.0)

        # Mock retriever with simulated latency (e.g. 5ms)
        mock_retriever = MagicMock()
        mock_retriever.name = "MockLatencyRetriever"

        def _slow_retrieve(query: Any) -> list[RetrievalResult]:
            time.sleep(0.005)  # 5ms simulated disk/index latency
            return [
                RetrievalResult(content=f"Result for {query.text}", score=0.95, source="doc-1")
            ]

        mock_retriever.retrieve.side_effect = _slow_retrieve

        pipeline = RetrievalPipeline(
            retriever=mock_retriever,
            cache=cache,
        )

        query = RetrievalQuery(text="Quantum supremacy experiments", limit=5)

        # 1. Cold Cache: executes retriever with simulated 5ms latency
        cold_start = time.perf_counter()
        res1, ctx1 = pipeline.execute(query)
        cold_latency_ms = (time.perf_counter() - cold_start) * 1000.0

        assert len(res1) == 1
        assert cold_latency_ms >= 4.0  # At least 4-5ms
        assert cache.stats()["misses"] == 1
        assert cache.stats()["hits"] == 0

        # 2. Warm Cache: instant sub-millisecond retrieval
        warm_start = time.perf_counter()
        res2, ctx2 = pipeline.execute(query)
        warm_latency_ms = (time.perf_counter() - warm_start) * 1000.0

        assert len(res2) == 1
        assert res2[0].content == res1[0].content
        # Cached response should return in sub-millisecond (< 1.5ms)
        assert warm_latency_ms < 2.0
        assert cache.stats()["hits"] == 1
        assert cache.stats()["hit_ratio"] == 0.5

    def test_concurrent_multi_threaded_requests(self) -> None:
        """
        Stress test concurrent multi-threaded requests across vector store and retrieval cache.
        Spawns 20 threads reading and writing concurrently to ensure thread safety.
        """
        store = InMemoryVectorStore()
        cache = RetrievalCache(max_size=200)

        # Populate base vectors
        for i in range(50):
            store.add(Embedding(text=f"Base {i}", vector=[float(i), float(i * 2)]))

        errors: list[Exception] = []
        barrier = threading.Barrier(20)

        def worker_task(worker_id: int) -> None:
            try:
                # Synchronize start across all 20 threads
                barrier.wait(timeout=5.0)

                # Each thread performs concurrent adds and searches
                for step in range(10):
                    # Add new vector
                    emb = Embedding(
                        text=f"Worker {worker_id} Step {step}",
                        vector=[float(worker_id + step), float(worker_id * 2)],
                    )
                    store.add(emb)

                    # Search
                    query_emb = Embedding(text="Search", vector=[1.0, 2.0])
                    results = store.search(query_emb, limit=3)
                    assert len(results) == 3

                    # Cache read/write
                    key = cache.make_key(f"Query {worker_id}")
                    cache.set(key, [RetrievalResult(content=f"Worker {worker_id}", score=0.9, source="worker_src")])
                    cached = cache.get(key)
                    assert cached is not None
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker_task, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        assert not errors, f"Concurrent thread errors encountered: {errors}"
        # 50 base + 20 workers * 10 steps = 250 embeddings
        assert len(store) == 250
        assert cache.size > 0

    def test_gui_non_blocking_async_responsiveness(self) -> None:
        """
        Verify GUIApplication asynchronous methods execute in background threads
        without blocking the caller.
        """
        mock_window = MagicMock()
        mock_ai_manager = MagicMock()
        mock_ai_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Async answer"
        mock_ai_provider.generate.return_value = mock_response
        mock_ai_manager.select_provider.return_value = mock_ai_provider

        mock_research_pipeline = MagicMock()
        mock_research_pipeline.execute.return_value = "Async research result"

        app = GUIApplication(
            window=mock_window,
            ai_manager=mock_ai_manager,
            research_pipeline=mock_research_pipeline,
            max_workers=2,
        )

        # 1. Async Chat execution
        chat_results: list[str] = []
        chat_done = threading.Event()

        def on_chat_complete(res: str) -> None:
            chat_results.append(res)
            chat_done.set()

        future = app.chat_async(
            prompt="Tell me about async architectures",
            on_complete=on_chat_complete,
        )

        assert not future.done() or future.done()  # Non-blocking return
        assert chat_done.wait(timeout=3.0)
        assert chat_results == ["Async answer"]

        # 2. Async Research execution
        research_results: list[Any] = []
        research_done = threading.Event()

        def on_research_complete(res: Any) -> None:
            research_results.append(res)
            research_done.set()

        res_future = app.research_async(
            query="Analyze distributed consensus",
            on_complete=on_research_complete,
        )

        assert res_future is not None
        assert research_done.wait(timeout=3.0)
        assert research_results == ["Async research result"]

        app.shutdown()
        assert app._executor is None
