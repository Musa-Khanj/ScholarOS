from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AIResponse:
    """
    Represents a response returned by an AI model.
    """

    content: str

    model: str

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0