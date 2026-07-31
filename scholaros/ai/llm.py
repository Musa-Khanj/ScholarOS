"""
ScholarOS
Language Model Abstractions

Version : 2.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the common language model interfaces and
message types used throughout ScholarOS.

Responsibilities
----------------
• Define message roles
• Define chat message structure
• Define the abstract LLM interface
• Provide provider-specific implementations
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from scholaros.ai.ollama_client import OllamaClient

from scholaros.ai.response import AIResponse

class MessageRole(str, Enum):
    """
    Supported chat message roles.
    """

    SYSTEM = "system"

    USER = "user"

    ASSISTANT = "assistant"

@dataclass(slots=True, frozen=True)
class Message:
    """
    Represents a single chat message.
    """

    role: MessageRole

    content: str

class LLM(ABC):
    """
    Abstract base class for all language model
    providers.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
    ) -> AIResponse:
        """
        Generate a response from the supplied
        conversation.
        """

        raise NotImplementedError

    def __call__(
        self,
        messages: list[Message],
    ) -> AIResponse:
        """
        Allow an LLM instance to be called like a
        function.
        """

        return self.generate(messages)


class OllamaLLM(LLM):
    """
    Ollama implementation of the abstract LLM.
    """

    def __init__(
        self,
        client: OllamaClient | None = None,
        model: str = "qwen2.5:1.5b",
    ) -> None:

        self._client = client or OllamaClient()
        self._model = model

    @property
    def model(self) -> str:
        """
        Returns the configured model name.
        """

        return self._model

    def generate(
        self,
        messages: list[Message],
    ) -> AIResponse:
        """
        Generate a response from the conversation.
        """

        prompt = "\n".join(
            message.content
            for message in messages
        )

        return self._client.generate(
            model=self._model,
            prompt=prompt,
        )

    def with_model(
        self,
        model: str,
    ) -> "OllamaLLM":
        """
        Return a new OllamaLLM configured with a
        different model.
        """

        return OllamaLLM(
            client=self._client,
            model=model,
        )

    def supports(
        self,
        model: str,
    ) -> bool:
        """
        Returns True if this instance is configured
        for the supplied model.
        """

        return self._model == model

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(model={self._model!r})"
        )

__all__ = [
    "LLM",
    "Message",
    "MessageRole",
    "OllamaLLM",
]