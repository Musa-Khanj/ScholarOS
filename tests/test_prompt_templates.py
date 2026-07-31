from scholaros.ai.prompt import (
    PaperSummaryTemplate,
    ResearchAssistantTemplate,
    VisionAnalysisTemplate,
)


def test_research_template():

    prompt = ResearchAssistantTemplate().render(
        topic="Artificial Intelligence"
    )

    assert "Artificial Intelligence" in prompt.messages[0].content


def test_summary_template():

    prompt = PaperSummaryTemplate().render(
        paper="This is a research paper."
    )

    assert "research paper" in prompt.messages[0].content


def test_vision_template():

    prompt = VisionAnalysisTemplate().render(
        image="Microscope image"
    )

    assert "Microscope image" in prompt.messages[0].content