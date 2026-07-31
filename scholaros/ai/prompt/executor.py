from __future__ import annotations

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.prompt.prompt import Prompt


class PromptExecutor:
    """
    Executes rendered prompts using the configured LLM.
    """

    def __init__(
        self,
        llm: LLM,
    ) -> None:

        self._llm = llm

    def execute(
        self,
        prompt: Prompt,
    ) -> LLMResponse:

        return self._llm.generate(
            prompt.messages
        )