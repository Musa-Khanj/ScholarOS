"""
ScholarOS
Prompt Session

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single prompt execution session.

Responsibilities
----------------
• Hold a PromptBuilder
• Hold an LLM
• Coordinate prompt execution
"""

from __future__ import annotations

from scholaros.ai.llm import LLM
from scholaros.ai.prompt_builder import PromptBuilder


class PromptSession:
    """
    Coordinates prompt execution.
    """

    def __init__(
        self,
        builder: PromptBuilder,
        llm: LLM,
    ) -> None:

        self._builder = builder
        self._llm = llm

    def execute(
        self,
        template: str,
        **variables: str,
    ):
        """
        Build a prompt and execute it using
        the configured language model.
        """

        prompt = self._builder.build(
            template,
            **variables,
        )

        return self._llm.generate(
            prompt,
        )

    @property
    def builder(
        self,
    ) -> PromptBuilder:
        """
        Return the associated PromptBuilder.
        """

        return self._builder

    @property
    def llm(
        self,
    ) -> LLM:
        """
        Return the associated LLM.
        """

        return self._llm

    def build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a prompt without executing it.
        """

        return self._builder.build(
            template,
            **variables,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the PromptSession.
        """

        return (
            f"{self.__class__.__name__}"
            f"(templates={len(self._builder.registry())}, "
            f"model={self._llm.model!r})"
        )