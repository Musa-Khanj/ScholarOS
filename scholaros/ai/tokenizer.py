"""
ScholarOS AI Tokenizer.

Provides token estimation, counting heuristics, and context window truncation.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scholaros.ai.message import Message


class Tokenizer:
    """
    Lightweight, provider-agnostic token estimator.
    """

    def __init__(self, chars_per_token: float = 4.0) -> None:
        self.chars_per_token = max(1.0, chars_per_token)

    def count(self, text: str) -> int:
        """
        Estimate the number of tokens in a string using word/punctuation heuristics.
        """
        if not text:
            return 0

        # Heuristic: split words and punctuation
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        by_words = len(tokens)
        by_chars = max(1, int(len(text) / self.chars_per_token))

        # Balanced average
        return max(1, int((by_words + by_chars) / 2))

    def count_messages(self, messages: list[Message]) -> int:
        """Estimate token total for a sequence of conversation messages."""
        total = 0
        for msg in messages:
            total += 4  # Metadata/role overhead per message
            total += self.count(msg.content)
            if msg.name:
                total += self.count(msg.name)
        total += 2  # Priming overhead
        return total

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximate max token limit."""
        if self.count(text) <= max_tokens:
            return text

        char_limit = int(max_tokens * self.chars_per_token)
        return text[:char_limit]


def count_tokens(text: str) -> int:
    """Convenience helper to estimate tokens in a string."""
    return Tokenizer().count(text)


__all__ = [
    "Tokenizer",
    "count_tokens",
]
