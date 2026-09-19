"""
ScholarOS Mock LLM.

Provides a deterministic LLM implementation for offline testing, unit tests,
and simulated generation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse


class MockLLM(LLM):
    """
    Deterministic LLM mock for unit testing and offline development.
    """

    def __init__(
        self,
        default_response: str = "Mock LLM response.",
        model: str = "mock-llm",
        canned_responses: dict[str, str] | None = None,
        handler: Callable[[list[Any] | str], str] | None = None,
    ) -> None:
        self._default_response = default_response
        self._model = model
        self._canned_responses = dict(canned_responses) if canned_responses else {}
        self._handler = handler
        self.call_count: int = 0
        self.history: list[dict[str, Any]] = []

    @property
    def model(self) -> str:
        return self._model

    def generate(
        self,
        messages: list[Message] | list[Any] | str,
        **kwargs: Any,
    ) -> LLMResponse:
        self.call_count += 1
        self.history.append({"messages": messages, "kwargs": kwargs})

        # 1. Custom handler callback
        if self._handler is not None:
            content = self._handler(messages)
        else:
            # 2. Extract text to inspect canned responses
            text_query = ""
            if isinstance(messages, str):
                text_query = messages
            elif messages and hasattr(messages[-1], "content"):
                text_query = str(messages[-1].content)
            elif messages:
                text_query = str(messages[-1])

            content = self._default_response
            for key, canned in self._canned_responses.items():
                if key.lower() in text_query.lower():
                    content = canned
                    break

        prompt_tokens = 10
        completion_tokens = max(1, len(content.split()))

        return LLMResponse(
            content=content,
            model=self._model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )


__all__ = [
    "MockLLM",
]
