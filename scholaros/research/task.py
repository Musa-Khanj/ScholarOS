"""
ScholarOS
Research Task

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a reusable research operation.

Responsibilities
----------------
• Store the prompt template name
• Execute research through ResearchPipeline
• Serve as the base unit of research workflows
"""

from __future__ import annotations

from scholaros.research.pipeline import (
    ResearchPipeline,
)


class ResearchTask:
    """
    Represents a reusable research task.
    """

    def __init__(
        self,
        pipeline: ResearchPipeline,
        template: str,
    ) -> None:

        self._pipeline = pipeline
        self._template = template

    def execute(
        self,
        **variables: str,
    ):
        """
        Execute this research task using the
        configured ResearchPipeline.
        """

        return self._pipeline.execute(
            self._template,
            **variables,
        )

    def build(
        self,
        **variables: str,
    ) -> str:
        """
        Build the prompt for this research task
        without executing it.
        """

        return self._pipeline.build(
            self._template,
            **variables,
        )

    @property
    def pipeline(
        self,
    ) -> ResearchPipeline:
        """
        Return the associated ResearchPipeline.
        """

        return self._pipeline

    @property
    def template(
        self,
    ) -> str:
        """
        Return the template name used by this task.
        """

        return self._template

    def exists(
        self,
    ) -> bool:
        """
        Returns True if this task's template
        exists in the ResearchPipeline.
        """

        return self._pipeline.contains(
            self._template,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the ResearchTask.
        """

        return (
            f"{self.__class__.__name__}"
            f"(template={self._template!r})"
        )