"""
ScholarOS Provider-to-LLM Adapter.

Adapts any AIProvider or AIManager to the LLM interface, enabling complete provider
independence for RAG pipelines and Research agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message as LLMMessage
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.message import Message as AIMessage
from scholaros.ai.request import AIRequest

if TYPE_CHECKING:
    from scholaros.ai.manager import AIManager
    from scholaros.ai.provider import AIProvider


class ProviderLLM(LLM):
    """
    Adapter bridging ScholarOS AIProvider or AIManager to the LLM interface.
    """

    def __init__(
        self,
        provider: AIProvider | None = None,
        manager: AIManager | None = None,
        model: str | None = None,
        timeout: float | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> None:
        if provider is None and manager is None:
            raise ValueError("ProviderLLM requires either an AIProvider or an AIManager instance.")
        self._provider = provider
        self._manager = manager
        self._model = model or (provider.default_model if provider else None) or "default"
        self._timeout = timeout
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> AIProvider | None:
        return self._provider

    @property
    def manager(self) -> AIManager | None:
        return self._manager

    def generate(
        self,
        messages: list[LLMMessage] | list[AIMessage] | list[Any] | str,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate response using the underlying AIProvider or AIManager.
        """
        ai_messages: list[AIMessage] = []

        if isinstance(messages, str):
            ai_messages = [AIMessage.user(messages)]
        else:
            for m in messages:
                if isinstance(m, AIMessage):
                    ai_messages.append(m)
                elif hasattr(m, "role") and hasattr(m, "content"):
                    role_val = m.role.value if hasattr(m.role, "value") else str(m.role)
                    ai_messages.append(AIMessage(role=role_val, content=m.content))
                else:
                    ai_messages.append(AIMessage.user(str(m)))

        model = kwargs.get("model", self._model)
        temperature = kwargs.get("temperature", self._temperature)
        max_tokens = kwargs.get("max_tokens", self._max_tokens)
        timeout = kwargs.get("timeout", self._timeout)

        req = AIRequest(
            messages=ai_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            provider=self._provider.name if self._provider else None,
        )

        if self._manager is not None:
            ai_response = self._manager.generate(req)
        elif self._provider is not None:
            ai_response = self._provider.generate(req)
        else:
            raise RuntimeError("No provider or manager available to handle generation.")

        return LLMResponse(
            content=ai_response.content,
            model=ai_response.model or model,
            prompt_tokens=ai_response.prompt_tokens,
            completion_tokens=ai_response.completion_tokens,
            total_tokens=ai_response.total_tokens,
        )


__all__ = [
    "ProviderLLM",
]
