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

from scholaros.knowledge.document import (
    KnowledgeDocument,
)


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
            document.identifier
        ] = document

    def remove(
        self,
        identifier: str,
    ) -> None:
        """
        Remove a document from the
        collection.
        """

        self._documents.pop(
            identifier,
            None,
        )

    def get(
        self,
        identifier: str,
    ) -> KnowledgeDocument | None:
        """
        Return a document from the
        collection.
        """

        return self._documents.get(
            identifier,
        )

    def contains(
        self,
        identifier: str,
    ) -> bool:
        """
        Return whether a document
        exists.
        """

        return (
            identifier
            in self._documents
        )

    def identifiers(
        self,
    ) -> tuple[str, ...]:
        """
        Return all document
        identifiers.
        """

        return tuple(
            self._documents.keys(),
        )

    def values(
        self,
    ) -> tuple[
        KnowledgeDocument,
        ...,
    ]:
        """
        Return all documents.
        """

        return tuple(
            self._documents.values(),
        )

    def items(
        self,
    ) -> tuple[
        tuple[
            str,
            KnowledgeDocument,
        ],
        ...,
    ]:
        """
        Return all document items.
        """

        return tuple(
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

    def __contains__(
        self,
        identifier: str,
    ) -> bool:
        """
        Return whether the supplied
        identifier exists.
        """

        return self.contains(
            identifier,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the stored
        documents.
        """

        return iter(
            self._documents.values(),
        )

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