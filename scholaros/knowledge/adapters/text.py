"""
ScholarOS Knowledge Text Adapter.

Loads and adapts plain text files and raw text content into knowledge documents.
"""

from __future__ import annotations

from pathlib import Path

from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.metadata import KnowledgeMetadata
from scholaros.knowledge.source import KnowledgeSource


class TextAdapter:
    """
    Adapter for ingesting plain text files into KnowledgeDocuments.
    """

    def read_file(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Read a text file from disk and convert to KnowledgeDocument."""
        path = Path(file_path)
        content = path.read_text(encoding="utf-8", errors="replace")
        doc_id = identifier or path.stem
        title = path.stem.replace("_", " ").title()

        source = KnowledgeSource(
            identifier=f"file:{path.name}",
            source_type="file",
            uri=str(path.resolve()),
        )
        metadata = KnowledgeMetadata(
            source=str(path.name),
            tags=("text", path.suffix.lstrip(".")),
        )

        return KnowledgeDocument(
            identifier=doc_id,
            title=title,
            content=content,
            metadata=metadata,
            source=source,
        )

    def load(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Alias for read_file."""
        return self.read_file(file_path, identifier)

    def from_text(
        self,
        content: str,
        identifier: str,
        title: str = "",
        metadata: KnowledgeMetadata | None = None,
    ) -> KnowledgeDocument:
        """Create a KnowledgeDocument from a raw text string."""
        return KnowledgeDocument(
            identifier=identifier,
            title=title or identifier,
            content=content,
            metadata=metadata or KnowledgeMetadata(),
        )


__all__ = [
    "TextAdapter",
]
