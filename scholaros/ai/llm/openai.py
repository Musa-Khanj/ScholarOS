from typing import Any

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.response import LLMResponse


class OpenAILLM(LLM):

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        base_url: str | None = None,
    ) -> None:

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAI support requires the 'openai' package.\n"
                "Install it using:\n"
                "pip install openai"
            ) from exc

        self._model = model

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def generate(
        self,
        messages: list[Message] | str,
    ) -> LLMResponse:

        if isinstance(messages, str):
            messages = [
                Message(
                    role=MessageRole.USER,
                    content=messages,
                )
            ]

        payload_messages: list[Any] = self._convert(messages)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=payload_messages,
        )

        usage = response.usage

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=self._model,
            prompt_tokens=(
                usage.prompt_tokens
                if usage
                else 0
            ),
            completion_tokens=(
                usage.completion_tokens
                if usage
                else 0
            ),
            total_tokens=(
                usage.total_tokens
                if usage
                else 0
            ),
        )

    @property
    def model(self) -> str:
        return self._model

    def _convert(
        self,
        messages: list[Message],
    ) -> list[dict[str, str]]:

        converted: list[dict[str, str]] = []

        for message in messages:

            converted.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        return converted