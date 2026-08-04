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

from scholaros.knowledge.metadata import KnowledgeMetadata


class KnowledgeDocument:
    """
    Represents a single knowledge document.
    """

    def __init__(
    self,
    document_id: str,
    title: str,
    content: str,
    metadata: KnowledgeMetadata,
) -> None:
        """
        Initialize the knowledge document.
        """

        self._id = document_id
        self._title = title
        self._content = content
        self._metadata = metadata

    @property
    def id(
        self,
    ) -> str:
        """
        Return the document identifier.
        """

        return self._id

    @property
    def title(
        self,
    ) -> str:
        """
        Return the document title.
        """

        return self._title

    @property
    def content(
        self,
    ) -> str:
        """
        Return the document content.
        """

        return self._content

    @property
    def metadata(
        self,
    ) -> KnowledgeMetadata:
        """
        Return the document metadata.
        """

        return self._metadata

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the document.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"title={self.title!r}"
            f")"
        )