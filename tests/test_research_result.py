from scholaros.ai.response import AIResponse
from scholaros.research.result import ResearchResult


def test_research_result_initialization():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert result.response == response


def test_response_property():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert (
        result.response
        == response
    )


def test_content_property():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert (
        result.content
        == "Research findings"
    )


def test_model_property():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert (
        result.model
        == "qwen2.5:1.5b"
    )


def test_has_content():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert result.has_content()


def test_empty_result():

    response = AIResponse(
        content="",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert not result.has_content()

    assert result.is_empty()

    assert not bool(result)


def test_to_dict():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert (
        result.to_dict()
        ==
        {
            "content": "Research findings",
            "model": "qwen2.5:1.5b",
        }
    )


def test_string_representation():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert (
        str(result)
        ==
        "Research findings"
    )


def test_repr_representation():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    representation = repr(result)

    assert (
        "ResearchResult"
        in representation
    )

    assert (
        "qwen2.5:1.5b"
        in representation
    )


def test_boolean_conversion():

    response = AIResponse(
        content="Research findings",
        model="qwen2.5:1.5b",
    )

    result = ResearchResult(
        response,
    )

    assert bool(result)