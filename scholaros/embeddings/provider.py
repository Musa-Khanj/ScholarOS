"""
ScholarOS
Embedding Provider

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Abstract base class
for embedding providers.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from collections.abc import Sequence

from scholaros.embeddings.embedding import (
    Embedding,
)


class EmbeddingProvider(
    ABC,
):
    """
    Abstract embedding
    provider.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the provider
        name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return the provider
        description.
        """

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the provider
        version.
        """

    @abstractmethod
    def embed(
        self,
        text: str,
    ) -> Embedding:
        """
        Generate an embedding
        from text.
        """

    def embed_batch(
        self,
        texts: Sequence[str],
    ) -> list[Embedding]:
        """
        Generate embeddings for multiple texts.
        Providers may override this with vectorized bulk requests.
        """
        return [self.embed(t) for t in texts]

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        provider.
        """

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}'"
            f")"
        )
