from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0