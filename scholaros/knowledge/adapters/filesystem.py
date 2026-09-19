"""
ScholarOS Knowledge Filesystem Adapter.

Scans directories and loads documents using format-specific adapters based on extension.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scholaros.knowledge.adapters.json import JSONAdapter
from scholaros.knowledge.adapters.markdown import MarkdownAdapter
from scholaros.knowledge.adapters.pdf import PDFAdapter
from scholaros.knowledge.adapters.text import TextAdapter
from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument


class FilesystemAdapter:
    """
    Scans directories, discovers supported documents, and builds KnowledgeCollections.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        **kwargs: Any,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_adapter = TextAdapter()
        self.markdown_adapter = MarkdownAdapter()
        self.json_adapter = JSONAdapter()
        self.pdf_adapter = PDFAdapter()

    def read_file(self, file_path: str | Path) -> KnowledgeDocument:
        """Read a single file based on its extension."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext in (".md", ".markdown"):
            return self.markdown_adapter.read_file(path)
        elif ext == ".json":
            return self.json_adapter.read_file(path)
        elif ext == ".pdf":
            return self.pdf_adapter.read_file(path)
        else:
            return self.text_adapter.read_file(path)

    def scan_directory(
        self,
        directory_path: str | Path,
        collection_name: str | None = None,
        recursive: bool = True,
        extensions: tuple[str, ...] = (".txt", ".md", ".json", ".pdf"),
    ) -> KnowledgeCollection:
        """
        Scan directory for matching files and return a KnowledgeCollection.
        """
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        coll_name = collection_name or path.name
        collection = KnowledgeCollection(name=coll_name, description=f"Scanned from {path.resolve()}")

        pattern = "**/*" if recursive else "*"
        for file in path.glob(pattern):
            if file.is_file() and file.suffix.lower() in extensions:
                try:
                    doc = self.read_file(file)
                    collection.add(doc)
                except Exception:
                    continue

        return collection

    def load(self, file_path: str | Path) -> KnowledgeDocument:
        """Alias for read_file."""
        return self.read_file(file_path)

    def load_directory(
        self,
        directory_path: str | Path,
        collection_name: str | None = None,
        recursive: bool = True,
        extensions: tuple[str, ...] = (".txt", ".md", ".json", ".pdf"),
    ) -> list[KnowledgeDocument]:
        """Scan directory and return a list of KnowledgeDocuments."""
        coll = self.scan_directory(
            directory_path=directory_path,
            collection_name=collection_name,
            recursive=recursive,
            extensions=extensions,
        )
        return list(coll.values())


__all__ = [
    "FilesystemAdapter",
]
