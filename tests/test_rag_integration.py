from unittest.mock import Mock

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.response import LLMResponse
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.result import RetrievalResult


def create_retrieval_result(
    source: str = "doc-001",
    content: str = "ScholarOS is an AI research system.",
    score: float = 0.95,
) -> RetrievalResult:

    return RetrievalResult(
        source=source,
        content=content,
        score=score,
    )


def create_llm_response() -> LLMResponse:

    return LLMResponse(
        content="ScholarOS is an AI research system.",
        model="test-model",
        prompt_tokens=20,
        completion_tokens=10,
        total_tokens=30,
    )


def create_retrieval_pipeline(
    results: list[RetrievalResult] | None = None,
) -> Mock:

    retrieval_pipeline = Mock(
        spec=RetrievalPipeline,
    )

    retrieval_pipeline.run.return_value = (
        results
        if results is not None
        else [
            create_retrieval_result(),
        ]
    )

    return retrieval_pipeline


def create_llm() -> Mock:

    llm = Mock(
        spec=LLM,
    )

    llm.generate.return_value = (
        create_llm_response()
    )

    return llm


def create_pipeline(
    results: list[RetrievalResult] | None = None,
):

    retrieval_pipeline = (
        create_retrieval_pipeline(
            results,
        )
    )

    llm = create_llm()

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
    )

    return (
        pipeline,
        retrieval_pipeline,
        llm,
    )


def test_rag_integration_retrieval_to_llm():

    (
        pipeline,
        retrieval_pipeline,
        llm,
    ) = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
        minimum_score=0.75,
    )

    response = pipeline.run(
        request,
    )

    retrieval_pipeline.run.assert_called_once_with(
        "What is ScholarOS?",
        0.75,
    )

    llm.generate.assert_called_once()

    assert isinstance(
        response,
        RAGResponse,
    )


def test_rag_integration_multiple_results():

    results = [
        create_retrieval_result(
            source="doc-001",
            content="First research document.",
            score=0.95,
        ),
        create_retrieval_result(
            source="doc-002",
            content="Second research document.",
            score=0.90,
        ),
        create_retrieval_result(
            source="doc-003",
            content="Third research document.",
            score=0.85,
        ),
    ]

    pipeline, _, _ = create_pipeline(
        results,
    )

    request = RAGRequest(
        query="Research question",
    )

    response = pipeline.run(
        request,
    )

    assert (
        response.results
        == tuple(results)
    )

    assert len(
        response.results,
    ) == 3


def test_rag_integration_source_preservation():

    result = create_retrieval_result(
        source="research-paper-001",
        content="Important research evidence.",
        score=0.91,
    )

    pipeline, _, llm = create_pipeline(
        [result],
    )

    request = RAGRequest(
        query="What does the research show?",
    )

    response = pipeline.run(
        request,
    )

    assert (
        response.results[0].source
        == "research-paper-001"
    )

    assert (
        response.results[0].content
        == "Important research evidence."
    )

    assert (
        response.results[0].score
        == 0.91
    )

    messages = (
        llm.generate.call_args.args[0]
    )

    assert (
        "research-paper-001"
        in messages[1].content
    )

    assert (
        "Important research evidence."
        in messages[1].content
    )


def test_rag_integration_empty_retrieval():

    (
        pipeline,
        retrieval_pipeline,
        llm,
    ) = create_pipeline(
        [],
    )

    request = RAGRequest(
        query="Unknown research question",
    )

    response = pipeline.run(
        request,
    )

    assert (
        retrieval_pipeline.run.called
    )

    assert (
        response.results
        == ()
    )

    messages = (
        llm.generate.call_args.args[0]
    )

    assert (
        messages[1].content
        == (
            "Knowledge Context:"
            "\n"
            "\n"
            "\n"
            "User Question:\n"
            "Unknown research question"
        )
    )


def test_rag_integration_retrieval_failure():

    retrieval_pipeline = Mock(
        spec=RetrievalPipeline,
    )

    retrieval_pipeline.run.side_effect = (
        RuntimeError(
            "Retrieval failed."
        )
    )

    llm = create_llm()

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
    )

    request = RAGRequest(
        query="Research question",
    )

    with pytest.raises(
        RuntimeError,
        match="Retrieval failed.",
    ):
        pipeline.run(
            request,
        )

    llm.generate.assert_not_called()


def test_rag_integration_llm_failure():

    retrieval_pipeline = (
        create_retrieval_pipeline()
    )

    llm = Mock(
        spec=LLM,
    )

    llm.generate.side_effect = (
        RuntimeError(
            "LLM generation failed."
        )
    )

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
    )

    request = RAGRequest(
        query="Research question",
    )

    with pytest.raises(
        RuntimeError,
        match="LLM generation failed.",
    ):
        pipeline.run(
            request,
        )


def test_rag_integration_request_validation():

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        RAGRequest(
            query="",
        )

    with pytest.raises(
        TypeError,
        match="must be a string",
    ):
        RAGRequest(
            query=123,
        )

    with pytest.raises(
        TypeError,
        match="must be a number",
    ):
        RAGRequest(
            query="Research",
            minimum_score="0.5",
        )

    with pytest.raises(
        ValueError,
        match="must be finite",
    ):
        RAGRequest(
            query="Research",
            minimum_score=float("nan"),
        )


def test_rag_integration_token_usage():

    pipeline, _, _ = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    response = pipeline.run(
        request,
    )

    assert (
        response.prompt_tokens
        == 20
    )

    assert (
        response.completion_tokens
        == 10
    )

    assert (
        response.total_tokens
        == 30
    )


def test_rag_integration_provider_independence():

    retrieval_pipeline = (
        create_retrieval_pipeline()
    )

    llm = Mock(
        spec=LLM,
    )

    llm.generate.return_value = (
        create_llm_response()
    )

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
    )

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    response = pipeline.run(
        request,
    )

    assert isinstance(
        response,
        RAGResponse,
    )

    assert (
        response.model
        == "test-model"
    )

    llm.generate.assert_called_once()
    