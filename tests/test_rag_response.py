from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_result() -> RetrievalResult:

    return RetrievalResult(
        source="doc-001",
        content="ScholarOS knowledge.",
        score=0.95,
    )


def create_response() -> RAGResponse:

    result = create_result()

    return RAGResponse(
        content="ScholarOS is a research operating system.",
        model="qwen2.5:1.5b",
        results=(
            result,
        ),
        prompt_tokens=10,
        completion_tokens=8,
        total_tokens=18,
    )


def test_response_content():

    response = create_response()

    assert (
        response.content
        == "ScholarOS is a research operating system."
    )


def test_response_model():

    response = create_response()

    assert (
        response.model
        == "qwen2.5:1.5b"
    )


def test_response_results():

    response = create_response()

    assert (
        len(
            response.results,
        )
        == 1
    )

    assert (
        response.results[0].source
        == "doc-001"
    )


def test_response_prompt_tokens():

    response = create_response()

    assert (
        response.prompt_tokens
        == 10
    )


def test_response_completion_tokens():

    response = create_response()

    assert (
        response.completion_tokens
        == 8
    )


def test_response_total_tokens():

    response = create_response()

    assert (
        response.total_tokens
        == 18
    )


def test_response_len():

    response = create_response()

    assert (
        len(response)
        == 1
    )


def test_response_repr():

    response = create_response()

    assert (
        repr(
            response,
        )
        == (
            "RAGResponse("
            "model='qwen2.5:1.5b', "
            "results=1)"
        )
    )