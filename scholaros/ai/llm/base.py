from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse


class LLM(ABC):

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
    ) -> LLMResponse:
        raise NotImplementedError

    @property
    @abstractmethod
    def model(self) -> str:
        raise NotImplementedError