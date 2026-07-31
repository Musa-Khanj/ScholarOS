"""
ScholarOS
Prompt Builder

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Builds executable prompts from registered
prompt templates.

Responsibilities
----------------
• Retrieve templates from PromptRegistry
• Build prompts from template variables
• Keep prompt composition separate from execution
"""

from __future__ import annotations

from scholaros.ai.prompt_registry import (
    PromptRegistry,
)


class PromptBuilder:
    """
    Builds prompts using a PromptRegistry.
    """

    def __init__(
        self,
        registry: PromptRegistry,
    ) -> None:

        self._registry = registry

    def build(
        self,
        name: str,
        **variables: str,
    ) -> str:
        """
        Build a prompt from a registered template.
        """

        template = self._registry.get(name)

        return template.template.format(
            **variables,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Returns True if the requested template
        exists.
        """

        return self._registry.contains(
            name,
        )

    def template(
        self,
        name: str,
    ):
        """
        Return the registered prompt template.
        """

        return self._registry.get(
            name,
        )

    def registry(
        self,
    ) -> PromptRegistry:
        """
        Return the underlying PromptRegistry.
        """

        return self._registry

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the PromptBuilder.
        """

        return (
            f"{self.__class__.__name__}"
            f"(templates={len(self._registry)})"
        )

    