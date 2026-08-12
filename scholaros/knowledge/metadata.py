"""
ScholarOS
Knowledge Metadata

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents metadata associated with
a knowledge document.
"""

from __future__ import annotations


class KnowledgeMetadata:
    """
    Represents metadata for a
    knowledge document.
    """

    def __init__(
        self,
        author: str = "",
        source: str = "",
        language: str = "",
        version: str = "",
        tags: tuple[
            str,
            ...,
        ] | None = None,
    ) -> None:
        """
        Initialize the knowledge
        metadata.
        """

        self._author = author
        self._source = source
        self._language = language
        self._version = version
        self._tags = tuple(
            tags or ()
        )

    @property
    def author(
        self,
    ) -> str:
        """
        Return the document author.
        """

        return self._author

    @property
    def source(
        self,
    ) -> str:
        """
        Return the document source.
        """

        return self._source

    @property
    def language(
        self,
    ) -> str:
        """
        Return the document language.
        """

        return self._language

    @property
    def version(
        self,
    ) -> str:
        """
        Return the document version.
        """

        return self._version

    @property
    def tags(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Return the document tags.
        """

        return self._tags

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        metadata.
        """

        return (
            f"{self.__class__.__name__}("
            f"author={self.author!r}, "
            f"source={self.source!r}, "
            f"language={self.language!r}, "
            f"version={self.version!r}, "
            f"tags={self.tags!r}"
            f")"
        )