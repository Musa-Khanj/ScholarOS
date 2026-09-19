"""
ScholarOS AI Session Management.

Manages conversational context, default parameters, and stateful multi-turn interactions.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from scholaros.ai.conversation import Conversation
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamingIterator

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager


class AISession:
    """
    Stateful session orchestrating conversations with an AI model.
    """

    def __init__(
        self,
        manager: AIManager,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        session_id: str | None = None,
    ) -> None:
        self.manager = manager
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation = Conversation(system_prompt=system_prompt)

    def send(self, prompt: str, **overrides: Any) -> AIResponse:
        """
        Send a user message, record it in conversation history, and return the assistant response.
        """
        self.conversation.add_user(prompt)

        req = AIRequest(
            messages=self.conversation.messages,
            model=overrides.get("model", self.model),
            temperature=overrides.get("temperature", self.temperature),
            max_tokens=overrides.get("max_tokens", self.max_tokens),
            metadata={"session_id": self.session_id},
        )

        response = self.manager.generate(req)
        self.conversation.add_assistant(response.content)
        return response

    def stream(self, prompt: str, **overrides: Any) -> StreamingIterator:
        """
        Stream a user message and record the completed response in conversation history.
        """
        self.conversation.add_user(prompt)

        req = AIRequest(
            messages=self.conversation.messages,
            model=overrides.get("model", self.model),
            temperature=overrides.get("temperature", self.temperature),
            max_tokens=overrides.get("max_tokens", self.max_tokens),
            stream=True,
            metadata={"session_id": self.session_id},
        )

        stream_iter = self.manager.stream(req)

        # Wrap stream iterator to record text into history once stream finishes
        def tracking_generator():
            for chunk in stream_iter:
                yield chunk
            self.conversation.add_assistant(stream_iter.text)

        return StreamingIterator(
            generator=tracking_generator,
            model=stream_iter.model,
            provider=stream_iter.provider,
        )

    def reset(self, system_prompt: str | None = None) -> None:
        """Clear conversation history, optionally setting a new system prompt."""
        self.conversation = Conversation(system_prompt=system_prompt)

    def __repr__(self) -> str:
        return f"AISession(id={self.session_id!r}, messages={len(self.conversation)})"


__all__ = [
    "AISession",
]
