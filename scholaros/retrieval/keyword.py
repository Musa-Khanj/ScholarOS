"""
ScholarOS Keyword Retriever.

Performs lexical and term-frequency retrieval over knowledge collections,
documents, and chunks using the KnowledgeStorage abstraction.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Sequence

from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever

if TYPE_CHECKING:
    from scholaros.knowledge.chunk import Chunk
    from scholaros.knowledge.document import KnowledgeDocument
    from scholaros.knowledge.storage import KnowledgeStorage


def tokenize(text: str) -> list[str]:
    """Simple whitespace and punctuation word tokenizer."""
    return re.findall(r"\w+", text.lower())


class KeywordRetriever(BaseRetriever):
    """
    Retrieves candidates using lexical keyword matching and term frequency scoring.
    """

    def __init__(
        self,
        storage: KnowledgeStorage | None = None,
        name: str = "KeywordRetriever",
    ) -> None:
        super().__init__(name=name)
        self._storage = storage

    @property
    def storage(self) -> KnowledgeStorage | None:
        """Return the backing knowledge storage."""
        return self._storage

    def score_content(self, terms: Sequence[str], content: str) -> float:
        """
        Compute a normalized lexical matching score in [0.0, 1.0].
        Scores term occurrences, density, and exact phrase match.
        """
        if not terms or not content:
            return 0.0

        content_lower = content.lower()
        content_tokens = tokenize(content_lower)
        if not content_tokens:
            return 0.0

        # Term overlap
        token_set = set(content_tokens)
        matched_terms = [t for t in terms if t in token_set]
        coverage = len(matched_terms) / len(terms)

        # Term frequency bonus
        tf = sum(content_tokens.count(t) for t in matched_terms)
        tf_norm = min(1.0, tf / max(1, len(content_tokens)))

        # Phrase match bonus
        phrase = " ".join(terms)
        phrase_bonus = 0.2 if phrase in content_lower else 0.0

        raw_score = (coverage * 0.6) + (tf_norm * 0.2) + phrase_bonus
        return min(1.0, max(0.0, raw_score))

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Execute lexical search over knowledge storage.
        """
        if self._storage is None:
            return []

        terms = tokenize(query.text)
        if not terms:
            return []

        # Determine target collections
        collections = (
            query.collections
            if query.collections
            else self._storage.list_collections()
        )
        if not collections:
            collections = ["default"]

        results: list[RetrievalResult] = []

        for col_name in collections:
            docs: list[KnowledgeDocument] = self._storage.list_documents(col_name)
            for doc in docs:
                # If document has chunks, search chunks
                chunks: list[Chunk] = self._storage.get_chunks_for_document(doc.identifier)
                if chunks:
                    for chunk in chunks:
                        score = self.score_content(terms, chunk.content)
                        if score > 0.0 and score >= query.min_score:
                            results.append(
                                RetrievalResult.from_chunk(
                                    chunk=chunk,
                                    score=round(score, 4),
                                    collection=col_name,
                                )
                            )
                else:
                    # Search full document content
                    score = self.score_content(terms, doc.content)
                    if score > 0.0 and score >= query.min_score:
                        results.append(
                            RetrievalResult.from_document(
                                doc=doc,
                                score=round(score, 4),
                                collection=col_name,
                            )
                        )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[: query.limit]


__all__ = [
    "KeywordRetriever",
    "tokenize",
]
