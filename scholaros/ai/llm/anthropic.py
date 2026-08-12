from __future__ import annotations

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.response import LLMResponse


class AnthropicLLM(LLM):

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-latest",
        base_url: str | None = None,
    ) -> None:

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "Anthropic support requires the "
                "'anthropic' package.\n"
                "Install it using:\n"
                "pip install anthropic"
            ) from exc

        self._model = model

        self._client = Anthropic(
            api_key=api_key,
            base_url=base_url,
        )

    def generate(
        self,
        messages: list[Message],
    ) -> LLMResponse:

        system = None
        converted = []

        for message in messages:

            if message.role == MessageRole.SYSTEM:
                system = message.content

            else:
                converted.append(
                    {
                        "role": (
                            "assistant"
                            if message.role
                            == MessageRole.ASSISTANT
                            else "user"
                        ),
                        "content": message.content,
                    }
                )

        response = self._client.messages.create(
            model=self._model,
            system=system,
            messages=converted,
            max_tokens=4096,
        )

        usage = response.usage

        return LLMResponse(
            content=response.content[0].text,
            model=self._model,
            prompt_tokens=(
                usage.input_tokens
                if usage
                else 0
            ),
            completion_tokens=(
                usage.output_tokens
                if usage
                else 0
            ),
            total_tokens=(
                (
                    usage.input_tokens
                    + usage.output_tokens
                )
                if usage
                else 0
            ),
        )

    @property
    def model(
        self,
    ) -> str:

        return self._model