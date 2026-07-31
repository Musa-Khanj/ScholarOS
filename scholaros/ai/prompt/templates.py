from __future__ import annotations

from scholaros.ai.prompt.base import PromptTemplate
from scholaros.ai.prompt.prompt import Prompt
from scholaros.ai.prompt.renderer import PromptRenderer


class ResearchAssistantTemplate(PromptTemplate):

    def __init__(self) -> None:
        self._renderer = PromptRenderer()

    def render(
        self,
        **variables: object,
    ) -> Prompt:

        return self._renderer.render(
            (
                "You are ScholarOS, an advanced AI research assistant.\n\n"
                "Research Topic:\n"
                "{{topic}}\n\n"
                "Provide a detailed academic analysis."
            ),
            topic=variables["topic"],
        )


class PaperSummaryTemplate(PromptTemplate):

    def __init__(self) -> None:
        self._renderer = PromptRenderer()

    def render(
        self,
        **variables: object,
    ) -> Prompt:

        return self._renderer.render(
            (
                "Summarize the following research paper.\n\n"
                "{{paper}}"
            ),
            topic=variables.get("topic", ""),
            paper=variables["paper"],
        )


class VisionAnalysisTemplate(PromptTemplate):

    def __init__(self) -> None:
        self._renderer = PromptRenderer()

    def render(
        self,
        **variables: object,
    ) -> Prompt:

        return self._renderer.render(
            (
                "Analyze the following image in detail.\n\n"
                "Image Description:\n"
                "{{image}}"
            ),
            image=variables["image"],
        )