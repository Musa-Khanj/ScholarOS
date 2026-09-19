"""
ScholarOS High-Level AI Client.

Provides an intuitive developer-facing entry point for prompting, chatting, streaming, and embeddings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.message import Message
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamingIterator

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager
    from scholaros.ai.session import AISession
    from scholaros.services.health import ServiceHealth


class AIClient:
    """
    High-level client for AI operations across all providers.
    """

    def __init__(self, manager: AIManager) -> None:
        self.manager = manager

    def generate(
        self,
        prompt_or_messages: str | list[Message],
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        """
        Execute an AI text generation request.
        """
        if isinstance(prompt_or_messages, str):
            request = AIRequest.from_prompt(
                prompt=prompt_or_messages,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        else:
            msgs = list(prompt_or_messages)
            if system_prompt and (not msgs or msgs[0].role != "system"):
                msgs.insert(0, Message.system(system_prompt))
            request = AIRequest(
                messages=msgs,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

        return self.manager.generate(request)

    def stream(
        self,
        prompt_or_messages: str | list[Message],
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> StreamingIterator:
        """
        Execute an AI streaming generation request.
        """
        if isinstance(prompt_or_messages, str):
            request = AIRequest.from_prompt(
                prompt=prompt_or_messages,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
        else:
            msgs = list(prompt_or_messages)
            if system_prompt and (not msgs or msgs[0].role != "system"):
                msgs.insert(0, Message.system(system_prompt))
            request = AIRequest(
                messages=msgs,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )

        return self.manager.stream(request)

    def embed(
        self,
        text_or_texts: str | list[str],
        model: str | None = None,
        **kwargs: Any,
    ) -> EmbeddingResponse:
        """
        Generate dense vector embeddings.
        """
        if isinstance(text_or_texts, str):
            req = EmbeddingRequest.from_text(text_or_texts, model=model, **kwargs)
        else:
            req = EmbeddingRequest.from_texts(text_or_texts, model=model, **kwargs)

        return self.manager.embed(req)

    def session(
        self,
        model: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AISession:
        """Create a stateful conversation session."""
        return self.manager.create_session(
            model=model,
            system_prompt=system_prompt,
            **kwargs,
        )

    def health(self) -> ServiceHealth:
        """Query AI subsystem health."""
        return self.manager.health()


__all__ = [
    "AIClient",
]
