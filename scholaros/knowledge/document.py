"""
ScholarOS
Knowledge Document

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single knowledge document
within ScholarOS.
"""

from __future__ import annotations

from scholaros.knowledge.metadata import (
    KnowledgeMetadata,
)


class KnowledgeDocument:
    """
    Represents a single knowledge
    document.
    """

    def __init__(
        self,
        identifier: str,
        title: str,
        content: str,
        metadata: KnowledgeMetadata | None = None,
    ) -> None:
        """
        Initialize the knowledge
        document.
        """

        self._identifier = identifier
        self._title = title
        self._content = content
        self._metadata = (
            metadata
            if metadata is not None
            else KnowledgeMetadata()
        )

    @property
    def identifier(
        self,
    ) -> str:
        """
        Return the document
        identifier.
        """

        return self._identifier

    @property
    def title(
        self,
    ) -> str:
        """
        Return the document
        title.
        """

        return self._title

    @property
    def content(
        self,
    ) -> str:
        """
        Return the document
        content.
        """

        return self._content

    @property
    def metadata(
        self,
    ) -> KnowledgeMetadata:
        """
        Return the document
        metadata.
        """

        return self._metadata

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        document.
        """

        return (
            f"{self.__class__.__name__}("
            f"identifier="
            f"{self.identifier!r}, "
            f"title="
            f"{self.title!r}"
            f")"
        )