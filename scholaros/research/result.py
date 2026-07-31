"""
ScholarOS
Research Result

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the result of a completed
research task.

Responsibilities
----------------
• Wrap AIResponse
• Expose research-oriented properties
• Provide a stable API for the research layer
"""

from __future__ import annotations

from scholaros.ai.response import AIResponse


class ResearchResult:
    """
    Represents the result of a research task.
    """

    def __init__(
        self,
        response: AIResponse,
    ) -> None:

        self._response = response

    @property
    def response(
        self,
    ) -> AIResponse:
        """
        Return the underlying AI response.
        """

        return self._response

    @property
    def content(
        self,
    ) -> str:
        """
        Return the generated research content.
        """

        return self._response.content

    @property
    def model(
        self,
    ) -> str:
        """
        Return the language model used to
        generate this result.
        """

        return self._response.model

    def has_content(
        self,
    ) -> bool:
        """
        Check whether research content exists.
        """

        return bool(self.content.strip())

    def is_empty(
        self,
    ) -> bool:
        """
        Check whether this result contains
        no meaningful content.
        """

        return not self.has_content()

    def to_dict(
        self,
    ) -> dict[str, str]:
        """
        Convert research result into
        dictionary representation.
        """

        return {
            "content": self.content,
            "model": self.model,
        }

    def __str__(
        self,
    ) -> str:
        """
        Return human-readable representation.
        """

        return self.content

    def __repr__(
        self,
    ) -> str:
        """
        Return developer-friendly representation.
        """

        return (
            f"ResearchResult("
            f"model={self.model!r}, "
            f"content_length={len(self.content)}"
            f")"
        )

    def __bool__(
        self,
    ) -> bool:
        """
        Return whether this result
        contains meaningful content.
        """

        return self.has_content()