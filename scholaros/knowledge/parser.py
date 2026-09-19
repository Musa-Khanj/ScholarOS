"""
ScholarOS Knowledge Parser.

Dispatches content parsing based on format, extracting clean text and structural metadata.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterator


@dataclass(slots=True)
class ParsedDocument:
    """
    Result of parsing document content.
    Supports attribute access (.content, .metadata, .title)
    and unpacking as a 2-tuple (content, metadata).
    """

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    title: str = ""

    def __iter__(self) -> Iterator[Any]:
        return iter((self.content, self.metadata))

    def __getitem__(self, index: int) -> Any:
        return (self.content, self.metadata)[index]

    def __len__(self) -> int:
        return 2


class DocumentParser(ABC):
    """
    Abstract base parser converting raw content into clean text and metadata.
    """

    @abstractmethod
    def parse(
        self,
        raw_content: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedDocument:
        """
        Parse raw content into a ParsedDocument (unpacks as (content, metadata)).
        """


class PlainTextParser(DocumentParser):
    """Parses plain UTF-8 text."""

    def parse(
        self,
        raw_content: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedDocument:
        text = raw_content.decode("utf-8", errors="replace") if isinstance(raw_content, bytes) else str(raw_content)
        meta = dict(metadata) if metadata else {}
        return ParsedDocument(content=text, metadata=meta, title=meta.get("title", ""))


class MarkdownParser(DocumentParser):
    """Parses Markdown, extracting YAML frontmatter and title if present."""

    _FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    _HEADING_REGEX = re.compile(r"^#\s+(.+)$", re.MULTILINE)

    def parse(
        self,
        raw_content: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedDocument:
        text = raw_content.decode("utf-8", errors="replace") if isinstance(raw_content, bytes) else str(raw_content)
        meta = dict(metadata) if metadata else {}
        title = meta.get("title", "")

        # Check for YAML frontmatter
        match = self._FRONTMATTER_REGEX.match(text)
        if match:
            frontmatter_text = match.group(1)
            text = text[match.end():]
            for line in frontmatter_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
                    if k.strip().lower() == "title" and not title:
                        title = v.strip()

        # Extract title from first markdown header if not set
        if not title:
            heading_match = self._HEADING_REGEX.search(text)
            if heading_match:
                title = heading_match.group(1).strip()
                meta.setdefault("title", title)

        return ParsedDocument(content=text, metadata=meta, title=title)


class JSONDocumentParser(DocumentParser):
    """Parses JSON content, converting it to formatted text and metadata."""

    def parse(
        self,
        raw_content: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedDocument:
        text = raw_content.decode("utf-8", errors="replace") if isinstance(raw_content, bytes) else str(raw_content)
        meta = dict(metadata) if metadata else {}
        title = meta.get("title", "")

        try:
            data = json.loads(text)
            if isinstance(data, dict):
                content = data.get("content") or data.get("text") or json.dumps(data, indent=2)
                for k, v in data.items():
                    if k not in ("content", "text"):
                        meta[k] = v
                title = str(data.get("title", title))
                return ParsedDocument(content=str(content), metadata=meta, title=title)
            elif isinstance(data, list):
                content = "\n".join(str(item) for item in data)
                return ParsedDocument(content=content, metadata=meta, title=title)
            return ParsedDocument(content=text, metadata=meta, title=title)
        except Exception:
            return ParsedDocument(content=text, metadata=meta, title=title)



class PDFDocumentParser(DocumentParser):
    """Parses PDF binary content or delegates to PDF extraction."""

    def parse(
        self,
        raw_content: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedDocument:
        meta = dict(metadata) if metadata else {}
        title = meta.get("title", "")

        raw_bytes = raw_content if isinstance(raw_content, bytes) else raw_content.encode("latin-1", errors="ignore")
        text = ""

        try:
            import io
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            if reader.metadata:
                if reader.metadata.title and not title:
                    title = str(reader.metadata.title)
                for k, v in reader.metadata.items():
                    if v:
                        meta[str(k)] = str(v)
        except Exception:
            # Fallback: attempt latin-1 decode
            try:
                text = raw_bytes.decode("latin-1", errors="ignore")
            except Exception:
                text = ""

        return ParsedDocument(content=text, metadata=meta, title=title)


class _GetParserDescriptor:
    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            if ParserRegistry._shared_instance is None:
                ParserRegistry._shared_instance = ParserRegistry()
            return lambda ext: ParserRegistry._shared_instance._get_parser_instance(ext)
        return lambda ext: instance._get_parser_instance(ext)


class ParserRegistry:
    """
    Maintains a mapping of file extensions and MIME types to parsers.
    Supports both instance-level and class-level retrieval.
    """

    _shared_instance: ClassVar[ParserRegistry | None] = None
    get_parser = _GetParserDescriptor()

    def __init__(self) -> None:
        self._parsers: dict[str, DocumentParser] = {}
        self._default_parser: DocumentParser = PlainTextParser()

        # Register standard parsers
        self.register([".txt", "text/plain"], PlainTextParser())
        self.register([".md", ".markdown", "text/markdown"], MarkdownParser())
        self.register([".json", "application/json"], JSONDocumentParser())
        self.register([".pdf", "application/pdf"], PDFDocumentParser())

    def register(self, extensions: str | list[str], parser: DocumentParser) -> None:
        """Register a parser for one or more extensions or MIME types."""
        ext_list = [extensions] if isinstance(extensions, str) else extensions
        for ext in ext_list:
            self._parsers[ext.lower().strip()] = parser

    def _get_parser_instance(self, extension_or_mime: str) -> DocumentParser:
        """Retrieve parser by extension or MIME type, falling back to PlainTextParser."""
        canonical = extension_or_mime.lower().strip()
        return self._parsers.get(canonical, self._default_parser)


__all__ = [
    "DocumentParser",
    "JSONDocumentParser",
    "MarkdownParser",
    "PDFDocumentParser",
    "ParsedDocument",
    "ParserRegistry",
    "PlainTextParser",
]

