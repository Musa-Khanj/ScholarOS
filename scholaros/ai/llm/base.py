from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse


class LLM(ABC):
    """
    Base interface for every language model provider.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
    ) -> LLMResponse:
        """
        Generate a response from a sequence of messages.
        """
        raise NotImplementedError