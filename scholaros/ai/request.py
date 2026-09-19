"""
ScholarOS AI Request Model.

Defines the strongly typed request object shared across all AI providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scholaros.ai.message import Message


@dataclass(slots=True)
class AIRequest:
    """
    Standard request payload submitted to AI providers.
    """

    messages: list[Message] = field(default_factory=list)
    prompt: str | None = None
    model: str | None = None
    provider: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float = 1.0
    stop: list[str] | None = None
    stream: bool = False
    tools: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None

    def __post_init__(self) -> None:
        if self.prompt is not None and not self.messages:
            self.messages = [Message.user(self.prompt)]

    @classmethod
    def from_prompt(
        cls,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> AIRequest:
        """Create an AIRequest from a prompt string and optional system prompt."""
        msgs: list[Message] = []
        if system_prompt:
            msgs.append(Message.system(system_prompt))
        msgs.append(Message.user(prompt))

        return cls(
            messages=msgs,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            timeout=timeout,
            **kwargs,
        )

    def copy(self, **overrides: Any) -> AIRequest:
        """Return a copy of the request with optional attribute overrides."""
        kwargs: dict[str, Any] = {
            "messages": list(self.messages),
            "prompt": self.prompt,
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop": list(self.stop) if self.stop else None,
            "stream": self.stream,
            "tools": list(self.tools) if self.tools else None,
            "metadata": dict(self.metadata),
            "timeout": self.timeout,
        }
        kwargs.update(overrides)
        return AIRequest(**kwargs)


# Alias for prompt completion use cases
CompletionRequest = AIRequest

__all__ = [
    "AIRequest",
    "CompletionRequest",
]
