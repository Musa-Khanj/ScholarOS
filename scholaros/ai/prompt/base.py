from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.ai.prompt.prompt import Prompt


class PromptTemplate(ABC):
    """
    Base class for every prompt template.
    """

    @abstractmethod
    def render(
        self,
        **variables: object,
    ) -> Prompt:
        """
        Produce a Prompt from template variables.
        """
        raise NotImplementedError