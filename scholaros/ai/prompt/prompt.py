from __future__ import annotations

from dataclasses import dataclass

from scholaros.ai.llm.message import Message


@dataclass(slots=True, frozen=True)
class Prompt:
    """
    Immutable prompt exchanged between the prompt engine
    and the LLM provider.
    """

    messages: list[Message]