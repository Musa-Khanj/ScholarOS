"""
ScholarOS
Prompt Catalog

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides a centralized collection of built-in
prompt templates.

Responsibilities
----------------
• Define built-in prompt templates
• Serve as the default prompt catalog
"""

from __future__ import annotations

from scholaros.ai.prompt_registry import (
    PromptTemplate,
)


class PromptCatalog:
    """
    Collection of built-in prompt templates.
    """

    def __init__(self) -> None:

        self._templates: list[
            PromptTemplate
        ] = []

    def register(
        self,
        template: PromptTemplate,
    ) -> None:
        """
        Register a built-in prompt template.
        """

        self._templates.append(
            template
        )

    def load_defaults(
        self,
    ) -> None:
        """
        Load the default ScholarOS prompt templates.
        """

        self.register(
            PromptTemplate(
                name="research_summary",
                template=(
                    "Summarize the following "
                    "research paper:\n\n{text}"
                ),
                description=(
                    "Generate a concise research "
                    "paper summary."
                ),
            )
        )

        self.register(
            PromptTemplate(
                name="code_review",
                template=(
                    "Review the following code "
                    "and provide suggestions:\n\n{code}"
                ),
                description=(
                    "Analyze source code for "
                    "quality improvements."
                ),
            )
        )

        self.register(
            PromptTemplate(
                name="literature_review",
                template=(
                    "Write a literature review "
                    "about:\n\n{topic}"
                ),
                description=(
                    "Generate a structured "
                    "literature review."
                ),
            )
        )

    def templates(
        self,
    ) -> list[PromptTemplate]:
        """
        Return all registered prompt templates.
        """

        return list(
            self._templates
        )

    def load_into(
        self,
        registry,
    ) -> None:
        """
        Load every template into the supplied
        PromptRegistry.
        """

        for template in self._templates:

            registry.register(template)

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered prompt
        templates.
        """

        return len(
            self._templates
        )
    