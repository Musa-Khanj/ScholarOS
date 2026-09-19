"""
ScholarOS Knowledge Adapters Package.

Provides input format adapters for filesystem, text, markdown, json, and pdf sources.
"""

from __future__ import annotations

from scholaros.knowledge.adapters.filesystem import FilesystemAdapter
from scholaros.knowledge.adapters.json import JSONAdapter
from scholaros.knowledge.adapters.markdown import MarkdownAdapter
from scholaros.knowledge.adapters.pdf import PDFAdapter
from scholaros.knowledge.adapters.text import TextAdapter

__all__ = [
    "FilesystemAdapter",
    "JSONAdapter",
    "MarkdownAdapter",
    "PDFAdapter",
    "TextAdapter",
]
