from __future__ import annotations

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.response import LLMResponse


class OllamaLLM(LLM):

    def __init__(
        self,
        model: str = "qwen2.5:1.5b",
        temperature: float = 0.0,
        base_url: str = "http://localhost:11434",
    ) -> None:

        self._model = model

        self._client = ChatOllama(
            model=model,
            temperature=temperature,
            base_url=base_url,
        )

    def generate(
        self,
        messages: list[Message],
    ) -> LLMResponse:

        response = self._client.invoke(
            self._convert(messages)
        )

        return LLMResponse(
            content=response.content,
            model=self._model,
        )

    def _convert(
        self,
        messages: list[Message],
    ):

        converted = []

        for message in messages:

            if message.role == MessageRole.SYSTEM:
                converted.append(
                    SystemMessage(
                        content=message.content
                    )
                )

            elif message.role == MessageRole.USER:
                converted.append(
                    HumanMessage(
                        content=message.content
                    )
                )

            elif message.role == MessageRole.ASSISTANT:
                converted.append(
                    AIMessage(
                        content=message.content
                    )
                )

            else:
                raise ValueError(
                    f"Unknown role: {message.role}"
                )

        return converted