from scholaros.knowledge.rag.context import (
    RAGContext,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_result(
    source: str = "doc-001",
    content: str = "ScholarOS knowledge.",
    score: float = 0.95,
) -> RetrievalResult:

    return RetrievalResult(
        source=source,
        content=content,
        score=score,
    )


def test_context_results():

    result = create_result()

    context = RAGContext(
        [
            result,
        ],
    )

    assert (
        context.results
        == (
            result,
        )
    )


def test_context_text():

    result = create_result()

    context = RAGContext(
        [
            result,
        ],
    )

    assert (
        context.text
        == (
            "[Source 1: doc-001]\n"
            "ScholarOS knowledge."
        )
    )


def test_context_multiple_results():

    first = create_result(
        source="doc-001",
        content="First document.",
        score=0.95,
    )

    second = create_result(
        source="doc-002",
        content="Second document.",
        score=0.85,
    )

    context = RAGContext(
        [
            first,
            second,
        ],
    )

    assert (
        context.text
        == (
            "[Source 1: doc-001]\n"
            "First document.\n\n"
            "[Source 2: doc-002]\n"
            "Second document."
        )
    )


def test_context_empty():

    context = RAGContext(
        [],
    )

    assert (
        context.text
        == ""
    )


def test_context_len():

    first = create_result()

    second = create_result(
        source="doc-002",
        content="Second document.",
        score=0.80,
    )

    context = RAGContext(
        [
            first,
            second,
        ],
    )

    assert (
        len(context)
        == 2
    )


def test_context_repr():

    context = RAGContext(
        [
            create_result(),
        ],
    )

    assert (
        repr(
            context,
        )
        == "RAGContext(results=1)"
    )