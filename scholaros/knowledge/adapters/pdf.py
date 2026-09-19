"""
ScholarOS Knowledge PDF Adapter.

Extracts text and metadata from PDF documents.
"""

from __future__ import annotations

from pathlib import Path

from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.metadata import KnowledgeMetadata
from scholaros.knowledge.source import KnowledgeSource


class PDFAdapter:
    """
    Adapter for ingesting PDF files into KnowledgeDocuments.
    """

    def read_file(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Extract text from a PDF file using pypdf/pypdf2 or fallback to text decoding."""
        path = Path(file_path)
        doc_id = identifier or path.stem
        title = path.stem.replace("_", " ").title()

        extracted_text = ""
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            extracted_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            # Fallback if pypdf is not installed: attempt binary string extraction
            try:
                raw_bytes = path.read_bytes()
                extracted_text = raw_bytes.decode("latin-1", errors="ignore")
            except Exception:
                extracted_text = f"PDF Document: {path.name}"

        source = KnowledgeSource(
            identifier=f"file:{path.name}",
            source_type="pdf",
            uri=str(path.resolve()),
        )
        metadata = KnowledgeMetadata(
            source=str(path.name),
            tags=("pdf", "document"),
        )

        return KnowledgeDocument(
            identifier=doc_id,
            title=title,
            content=extracted_text,
            metadata=metadata,
            source=source,
        )

    def load(self, file_path: str | Path, identifier: str | None = None) -> KnowledgeDocument:
        """Alias for read_file."""
        return self.read_file(file_path, identifier)


__all__ = [
    "PDFAdapter",
]
