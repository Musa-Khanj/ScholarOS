"""
ScholarOS AI Streaming.

Provides provider-independent token streaming primitives and streaming iterators.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from scholaros.ai.response import AIResponse


@dataclass(slots=True, frozen=True)
class StreamChunk:
    """
    Incremental chunk produced during token streaming.
    """

    delta: str
    index: int = 0
    model: str = ""
    finish_reason: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class StreamingIterator:
    """
    Unified synchronous and asynchronous stream wrapper.

    Accumulates streamed tokens and can reconstruct a complete AIResponse.
    """

    def __init__(
        self,
        generator: Iterator[StreamChunk] | Callable[[], Iterator[StreamChunk]],
        model: str = "",
        provider: str | None = None,
    ) -> None:
        self._generator = generator() if callable(generator) else generator
        self.model = model
        self.provider = provider
        self._accumulated: list[str] = []
        self._chunks: list[StreamChunk] = []
        self._finish_reason: str | None = None
        self._total_prompt_tokens: int = 0
        self._total_completion_tokens: int = 0

    def __iter__(self) -> Iterator[StreamChunk]:
        for chunk in self._generator:
            self._record_chunk(chunk)
            yield chunk

    async def __aiter__(self) -> AsyncIterator[StreamChunk]:
        for chunk in self:
            yield chunk

    def _record_chunk(self, chunk: StreamChunk) -> None:
        self._chunks.append(chunk)
        if chunk.delta:
            self._accumulated.append(chunk.delta)
        if chunk.finish_reason is not None:
            self._finish_reason = chunk.finish_reason
        if chunk.prompt_tokens > 0:
            self._total_prompt_tokens = chunk.prompt_tokens
        if chunk.completion_tokens > 0:
            self._total_completion_tokens = chunk.completion_tokens
        else:
            self._total_completion_tokens += 1

    @property
    def text(self) -> str:
        """Return all text accumulated so far."""
        return "".join(self._accumulated)

    def to_response(self) -> AIResponse:
        """Construct a complete AIResponse from consumed chunks."""
        content = "".join(self._accumulated)
        return AIResponse(
            content=content,
            model=self.model,
            prompt_tokens=self._total_prompt_tokens,
            completion_tokens=self._total_completion_tokens,
            total_tokens=self._total_prompt_tokens + self._total_completion_tokens,
            finish_reason=self._finish_reason or "stop",
            provider=self.provider,
        )


__all__ = [
    "StreamChunk",
    "StreamingIterator",
]
