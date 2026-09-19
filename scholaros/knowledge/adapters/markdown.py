"""
ScholarOS Knowledge Markdown Adapter.

Loads Markdown documents, parses YAML frontmatter, and extracts headers/tags.
"""

from __future__ import annotations

from pathlib import Path

from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.metadata import KnowledgeMetadata
from scholaros.knowledge.parser import MarkdownParser
from scholaros.knowledge.source import KnowledgeSource


class MarkdownAdapter:
    """
    Adapter for ingesting Markdown files with frontmatter support into KnowledgeDocuments.
    """

    def __init__(self, parser: MarkdownParser | None = None) -> None:
        self.parser = parser or MarkdownParser()

    def read_file(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Read and parse a markdown file."""
        path = Path(file_path)
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        content, extracted_meta = self.parser.parse(raw_text)

        doc_id = identifier or path.stem
        title = extracted_meta.get("title") or path.stem.replace("_", " ").title()
        author = extracted_meta.get("author", "")
        tags = tuple(extracted_meta.get("tags", "").split(",")) if "tags" in extracted_meta else ("markdown",)

        source = KnowledgeSource(
            identifier=f"file:{path.name}",
            source_type="file",
            uri=str(path.resolve()),
        )
        metadata = KnowledgeMetadata(
            author=author,
            source=str(path.name),
            tags=tags,
            extra=extracted_meta,
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

    def from_markdown(
        self,
        raw_markdown: str,
        identifier: str,
        title: str = "",
    ) -> KnowledgeDocument:
        """Create a KnowledgeDocument from a raw markdown string."""
        content, extracted_meta = self.parser.parse(raw_markdown)
        doc_title = title or extracted_meta.get("title") or identifier

        return KnowledgeDocument(
            identifier=identifier,
            title=doc_title,
            content=content,
            metadata=KnowledgeMetadata(tags=("markdown",), extra=extracted_meta),
        )


__all__ = [
    "MarkdownAdapter",
]
