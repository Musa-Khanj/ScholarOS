"""
ScholarOS Knowledge Normalizer.

Provides text cleaning, unicode normalization, whitespace collapsing, and formatting.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


class _NormalizeDescriptor:
    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return lambda text: TextNormalizer()._normalize_impl(text)
        return lambda text: instance._normalize_impl(text)


class TextNormalizer:
    """
    Normalizes text for downstream chunking, indexing, and vectorization.
    """

    normalize = _NormalizeDescriptor()

    def __init__(
        self,
        collapse_whitespace: bool = True,
        strip_control_chars: bool = True,
        lowercase: bool = False,
    ) -> None:
        self.collapse_whitespace = collapse_whitespace
        self.strip_control_chars = strip_control_chars
        self.lowercase = lowercase

    def _normalize_impl(self, text: str) -> str:
        """
        Apply unicode normalization, character cleaning, and whitespace standardizing.
        """
        if not text:
            return ""

        # Unicode normalization (NFKC compatibility)
        result = unicodedata.normalize("NFKC", text)

        # Strip non-printable control characters except standard whitespace
        if self.strip_control_chars:
            result = "".join(
                ch for ch in result
                if unicodedata.category(ch)[0] != "C" or ch in "\n\r\t"
            )

        # Standardize line endings to \n
        result = result.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse excessive blank lines and spaces
        if self.collapse_whitespace:
            result = re.sub(r"\s+", " ", result)

        if self.lowercase:
            result = result.lower()

        return result.strip()


__all__ = [
    "TextNormalizer",
]
