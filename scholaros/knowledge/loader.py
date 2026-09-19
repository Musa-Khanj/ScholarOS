"""
ScholarOS Knowledge Loader.

Loads, unloads, and processes knowledge documents through the ingestion pipeline:
Load -> Parse -> Normalize -> Chunk -> Store -> Index.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from scholaros.knowledge.adapters.filesystem import FilesystemAdapter
from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.events import DocumentIngested, IngestionFailed
from scholaros.knowledge.lifecycle import (
    BatchIngestionResult,
    DocumentStatus,
    DuplicatePolicy,
    IngestionResult,
)
from scholaros.knowledge.normalizer import TextNormalizer
from scholaros.knowledge.parser import ParserRegistry

if TYPE_CHECKING:
    from scholaros.knowledge.document import KnowledgeDocument
    from scholaros.knowledge.manager import KnowledgeManager



class KnowledgeLoader:
    """
    Loads and unloads knowledge collections and executes document processing pipelines.
    """

    def __init__(
        self,
        manager: KnowledgeManager | None = None,
        normalizer: TextNormalizer | None = None,
        parsers: ParserRegistry | None = None,
        fs_adapter: FilesystemAdapter | None = None,
        default_chunk_size: int = 500,
        default_chunk_overlap: int = 50,
    ) -> None:
        self._manager = manager
        self.normalizer = normalizer or TextNormalizer()
        self.parsers = parsers or ParserRegistry()
        self.fs_adapter = fs_adapter or FilesystemAdapter()
        self.default_chunk_size = default_chunk_size
        self.default_chunk_overlap = default_chunk_overlap

    @property
    def manager(self) -> KnowledgeManager:
        """Return the knowledge manager."""
        if self._manager is None:
            from scholaros.knowledge.manager import KnowledgeManager
            self._manager = KnowledgeManager()
        return self._manager

    def load(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """Load a knowledge collection."""
        self.manager.add(name, collection)

    def remove(
        self,
        name: str,
    ) -> None:
        """Remove a loaded knowledge collection."""
        self.manager.remove(name)

    def reload(
        self,
        name: str,
        collection: KnowledgeCollection,
    ) -> None:
        """Reload a knowledge collection."""
        self.remove(name)
        self.load(name, collection)

    def discover(self) -> tuple[str, ...]:
        """Return the discovered knowledge collections."""
        return self.manager.names()

    # ---------------------------------------------------------
    # Ingestion Pipeline Operations
    # ---------------------------------------------------------

    def load_file(
        self,
        file_path: str | Path,
        collection_name: str = "default",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> KnowledgeDocument:
        """
        Load a file through the pipeline and store/index it.
        """
        res = self.ingest_file(
            file_path=file_path,
            collection_name=collection_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            duplicate_policy=DuplicatePolicy.REPLACE,
        )
        if res.document is None:
            raise RuntimeError(res.error or "Failed to load document")
        return res.document

    def ingest_file(
        self,
        file_path: str | Path,
        collection_name: str = "default",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        duplicate_policy: DuplicatePolicy | str = DuplicatePolicy.REPLACE,
    ) -> IngestionResult:
        """
        Ingest a single document file with full chunking, embedding, indexing,
        and duplicate policy handling. Emits telemetry events.
        """
        start_time = time.perf_counter()
        policy = DuplicatePolicy(duplicate_policy) if isinstance(duplicate_policy, str) else duplicate_policy
        path = Path(file_path)

        try:
            doc = self.fs_adapter.read_file(path)
            doc.status = DocumentStatus.PARSED

            processed = self.process_document(
                doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            processed.status = DocumentStatus.CHUNKED

            # Add to manager (which handles deduplication, storage, vector embeddings, and inverted index)
            final_doc = self.manager.add_document(
                document=processed,
                collection_name=collection_name,
                auto_chunk=False,
                duplicate_policy=policy,
            )

            embedded = self.manager.vector_store is not None and (
                self.manager.embedding_generator is not None or self.manager.embedding_provider is not None
            )

            duration = (time.perf_counter() - start_time) * 1000
            if hasattr(self.manager, "_publish"):
                self.manager._publish(
                    DocumentIngested(
                        document_id=final_doc.identifier,
                        collection_name=collection_name,
                        chunks_count=len(final_doc.chunks),
                        embedded=embedded,
                    )
                )

            return IngestionResult(
                document=final_doc,
                chunks_count=len(final_doc.chunks),
                embedded=embedded,
                indexed=True,
                status=DocumentStatus.INDEXED,
                error=None,
                duration_ms=round(duration, 2),
                metadata={"file_path": str(path.resolve()), "collection": collection_name},
            )

        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            err_msg = str(exc)
            if hasattr(self.manager, "_publish"):
                self.manager._publish(
                    IngestionFailed(
                        file_path=str(path),
                        error=err_msg,
                        collection_name=collection_name,
                    )
                )
            return IngestionResult(
                document=None,
                chunks_count=0,
                embedded=False,
                indexed=False,
                status=DocumentStatus.FAILED,
                error=err_msg,
                duration_ms=round(duration, 2),
                metadata={"file_path": str(path.resolve()), "collection": collection_name},
            )

    def ingest_batch(
        self,
        file_paths: Sequence[str | Path],
        collection_name: str = "default",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        duplicate_policy: DuplicatePolicy | str = DuplicatePolicy.REPLACE,
    ) -> BatchIngestionResult:
        """
        Batch ingest documents with individual failure recovery.
        A failure on one file does not interrupt the rest of the batch.
        """
        start_time = time.perf_counter()
        batch_res = BatchIngestionResult(total_files=len(file_paths))

        for f_path in file_paths:
            res = self.ingest_file(
                file_path=f_path,
                collection_name=collection_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                duplicate_policy=duplicate_policy,
            )
            batch_res.results.append(res)
            if res.is_success and res.document is not None:
                batch_res.succeeded.append(res.document)
            else:
                batch_res.failed.append(str(f_path))
                batch_res.errors[str(f_path)] = res.error or "Unknown ingestion error"

        batch_res.duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return batch_res

    def ingest_directory(
        self,
        directory_path: str | Path,
        collection_name: str = "default",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        duplicate_policy: DuplicatePolicy | str = DuplicatePolicy.REPLACE,
        recursive: bool = True,
        extensions: tuple[str, ...] = (".txt", ".md", ".json", ".pdf"),
    ) -> BatchIngestionResult:
        """
        Scan and ingest a directory of documents with failure recovery.
        """
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        pattern = "**/*" if recursive else "*"
        matched_files = [f for f in path.glob(pattern) if f.is_file() and f.suffix.lower() in extensions]
        return self.ingest_batch(
            file_paths=matched_files,
            collection_name=collection_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            duplicate_policy=duplicate_policy,
        )

    def load_directory(
        self,
        directory_path: str | Path,
        collection_name: str | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> KnowledgeCollection:
        """
        Load an entire directory of documents into a collection.
        """
        collection = self.fs_adapter.scan_directory(
            directory_path,
            collection_name=collection_name,
        )

        for doc in list(collection.values()):
            processed = self.process_document(
                doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            collection.add(processed)

        self.manager.add(collection.name, collection)
        return collection


    def process_document(
        self,
        document: KnowledgeDocument,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> KnowledgeDocument:
        """
        Execute Normalize -> Chunk stages on a document.
        """
        normalized_text = self.normalizer.normalize(document.content)
        chunks = self.chunk_text(
            document_id=document.identifier,
            text=normalized_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        document.set_chunks(chunks)
        return document

    @classmethod
    def chunk_text(
        cls,
        text_or_doc_id: str = "",
        text_or_chunk_size: str | int = 500,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        document_id: str | None = None,
        text: str | None = None,
    ) -> list[Chunk]:
        """
        Split text into overlapping chunks with character offsets.
        Accepts:
        - chunk_text(document_id, text, chunk_size, chunk_overlap)
        - chunk_text(text, chunk_size, chunk_overlap)
        - chunk_text(document_id=..., text=..., chunk_size=..., chunk_overlap=...)
        """
        if text is not None:
            actual_text = text
            actual_doc_id = document_id or "doc"
            c_size = chunk_size
            c_overlap = chunk_overlap
        elif isinstance(text_or_chunk_size, str):
            actual_doc_id = text_or_doc_id or document_id or "doc"
            actual_text = text_or_chunk_size
            c_size = chunk_size
            c_overlap = chunk_overlap
        else:
            actual_doc_id = document_id or "doc"
            actual_text = text_or_doc_id
            c_size = int(text_or_chunk_size)
            c_overlap = chunk_size if chunk_size != 500 else chunk_overlap

        if not actual_text:
            return []

        chunks: list[Chunk] = []
        start = 0
        text_len = len(actual_text)
        index = 0

        while start < text_len:
            end = min(start + c_size, text_len)

            # Snap to word boundary if not at end of text
            if end < text_len:
                last_space = actual_text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk_content = actual_text[start:end].strip()
            if chunk_content:
                chunk_id = f"{actual_doc_id}_chunk_{index}"
                chunks.append(
                    Chunk(
                        identifier=chunk_id,
                        document_id=actual_doc_id,
                        content=chunk_content,
                        index=index,
                        start_char=start,
                        end_char=end,
                    )
                )
                index += 1

            if end >= text_len:
                break

            start = max(start + 1, end - c_overlap)

        return chunks

    def __len__(self) -> int:
        """Return the number of loaded knowledge collections."""
        return len(self.manager)

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the loader."""
        return f"{self.__class__.__name__}(collections={len(self)})"


# Canonical alias
Loader = KnowledgeLoader

__all__ = [
    "KnowledgeLoader",
    "Loader",
]
