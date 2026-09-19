"""
ScholarOS Knowledge JSON Adapter.

Loads and deserializes JSON documents into KnowledgeDocuments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.metadata import KnowledgeMetadata
from scholaros.knowledge.source import KnowledgeSource


class JSONAdapter:
    """
    Adapter for converting JSON files and payloads into KnowledgeDocuments.
    """

    def read_file(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Read a JSON file from disk into a KnowledgeDocument."""
        path = Path(file_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        doc_id = identifier or str(data.get("identifier") or data.get("id") or path.stem)
        title = str(data.get("title") or path.stem.replace("_", " ").title())
        content = str(data.get("content") or data.get("text") or json.dumps(data, indent=2))

        source = KnowledgeSource(
            identifier=f"file:{path.name}",
            source_type="file",
            uri=str(path.resolve()),
        )
        metadata = KnowledgeMetadata(
            author=str(data.get("author", "")),
            source=str(path.name),
            tags=tuple(data.get("tags", ("json",))),
            extra={k: v for k, v in data.items() if k not in ("identifier", "title", "content")},
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

    def from_dict(self, data: dict[str, Any], identifier: str | None = None) -> KnowledgeDocument:
        """Create a KnowledgeDocument from a dictionary payload."""
        doc_id = identifier or str(data.get("identifier") or data.get("id") or "doc")
        title = str(data.get("title") or doc_id)
        content = str(data.get("content") or data.get("text") or json.dumps(data))

        return KnowledgeDocument(
            identifier=doc_id,
            title=title,
            content=content,
            metadata=KnowledgeMetadata(tags=("json",)),
        )


__all__ = [
    "JSONAdapter",
]
