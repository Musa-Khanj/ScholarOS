"""
ScholarOS
Vector Store

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Abstract base class
for vector stores.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scholaros.embeddings.embedding import (
    Embedding,
)


class VectorStore(
    ABC,
):
    """
    Abstract vector
    store.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the vector
        store name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return the vector
        store description.
        """

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the vector
        store version.
        """

    @abstractmethod
    def add(
        self,
        embedding: Embedding,
    ) -> None:
        """
        Store an embedding.
        """

    @abstractmethod
    def remove(
        self,
        embedding: Embedding,
    ) -> None:
        """
        Remove an embedding.
        """

    @abstractmethod
    def clear(
        self,
    ) -> None:
        """
        Remove all stored
        embeddings.
        """

    @abstractmethod
    def embeddings(
        self,
    ) -> list[
        Embedding
    ]:
        """
        Return all stored
        embeddings.
        """

    @abstractmethod
    def search(
        self,
        query: Embedding,
        limit: int = 5,
    ) -> list[
        Embedding
    ]:
        """
        Search for similar
        embeddings.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        vector store.
        """

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}'"
            f")"
        )