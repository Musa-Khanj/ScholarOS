"""
ScholarOS
Prompt Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Central registry for reusable prompt templates.

Responsibilities
----------------
• Store reusable prompt templates
• Provide metadata for templates
• Serve as the foundation for prompt lookup
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PromptTemplate:
    """
    Represents a reusable prompt template.
    """

    name: str

    template: str

    description: str = ""

class PromptRegistry:
    """
    Stores and retrieves prompt templates.
    """

    def __init__(self) -> None:

        self._templates: dict[
            str,
            PromptTemplate,
        ] = {}

    def register(
        self,
        template: PromptTemplate,
    ) -> None:
        """
        Register a prompt template.
        """

        self._templates[
            template.name
        ] = template

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Returns True if a template with the given
        name exists.
        """

        return (
            name
            in self._templates
        )

    def get(
        self,
        name: str,
    ) -> PromptTemplate:
        """
        Return the registered prompt template.

        Raises
        ------
        KeyError
            If the template is not registered.
        """

        return self._templates[name]

    def all(
        self,
    ) -> list[PromptTemplate]:
        """
        Return all registered prompt templates.
        """

        return list(
            self._templates.values()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered
        prompt templates.
        """

        return len(
            self._templates
        )