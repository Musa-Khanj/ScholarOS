"""
ScholarOS
Knowledge Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a collection of knowledge
documents.
"""

from __future__ import annotations

from scholaros.knowledge.document import KnowledgeDocument


class KnowledgeCollection:
    """
    Represents a collection of
    knowledge documents.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the knowledge
        collection.
        """

        self._documents: dict[
            str,
            KnowledgeDocument,
        ] = {}

    def add(
        self,
        document: KnowledgeDocument,
    ) -> None:
        """
        Add a document to the
        collection.
        """

        self._documents[
            document.id
        ] = document

    def remove(
        self,
        document_id: str,
    ) -> None:
        """
        Remove a document from the
        collection.
        """

        self._documents.pop(
            document_id,
            None,
        )

    def get(
        self,
        document_id: str,
    ) -> KnowledgeDocument | None:
        """
        Return a document from the
        collection.
        """

        return self._documents.get(
            document_id,
        )

    def contains(
        self,
        document_id: str,
    ) -> bool:
        """
        Return whether a document
        exists.
        """

        return (
            document_id
            in self._documents
        )

    def ids(
        self,
    ) -> list[str]:
        """
        Return all document
        identifiers.
        """

        return list(
            self._documents.keys(),
        )

    def values(
        self,
    ) -> list[KnowledgeDocument]:
        """
        Return all documents.
        """

        return list(
            self._documents.values(),
        )

    def items(
        self,
    ) -> list[
        tuple[
            str,
            KnowledgeDocument,
        ]
    ]:
        """
        Return all document items.
        """

        return list(
            self._documents.items(),
        )

    def clear(
        self,
    ) -> None:
        """
        Remove every document from
        the collection.
        """

        self._documents.clear()

    def __len__(
        self,
    ) -> int:
        """
        Return the number of
        documents.
        """

        return len(
            self._documents,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        collection.
        """

        return (
            f"{self.__class__.__name__}("
            f"documents={len(self)}"
            f")"
        )