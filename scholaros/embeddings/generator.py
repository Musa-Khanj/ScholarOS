"""
ScholarOS
Embedding Generator

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Generates embeddings
using an embedding
provider.
"""

from __future__ import annotations

from collections.abc import Sequence

from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.provider import (
    EmbeddingProvider,
)


class EmbeddingGenerator:
    """
    Generates embeddings
    using an embedding
    provider.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
    ) -> None:
        """
        Initialize the
        embedding generator.
        """

        self._provider = provider

    @property
    def provider(
        self,
    ) -> EmbeddingProvider:
        """
        Return the embedding
        provider.
        """

        return self._provider

    def generate(
        self,
        text: str,
    ) -> Embedding:
        """
        Generate an embedding
        from text.
        """

        return self._provider.embed(
            text,
        )

    def generate_batch(
        self,
        texts: Sequence[str],
        batch_size: int = 32,
    ) -> list[Embedding]:
        """
        Generate embeddings for multiple texts in configurable batches.
        """
        if not texts:
            return []

        results: list[Embedding] = []
        batch_size = max(1, batch_size)
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            if hasattr(self._provider, "embed_batch"):
                results.extend(self._provider.embed_batch(chunk))
            else:
                results.extend(self._provider.embed(t) for t in chunk)
        return results

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        embedding generator.
        """

        return (
            f"{self.__class__.__name__}("
            f"provider="
            f"'{self.provider.name}'"
            f")"
        )
