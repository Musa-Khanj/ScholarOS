from unittest.mock import Mock

from scholaros.ai.llm.base import (
    LLM,
)
from scholaros.ai.llm.message import (
    MessageRole,
)
from scholaros.ai.llm.response import (
    LLMResponse,
)
from scholaros.knowledge.rag.pipeline import (
    RAGPipeline,
)
from scholaros.knowledge.rag.request import (
    RAGRequest,
)
from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.retrieval.pipeline import (
    RetrievalPipeline,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_result() -> RetrievalResult:

    return RetrievalResult(
        source="doc-001",
        content="ScholarOS is an AI research system.",
        score=0.95,
    )


def create_llm_response() -> LLMResponse:

    return LLMResponse(
        content="ScholarOS is an AI research system.",
        model="test-model",
        prompt_tokens=20,
        completion_tokens=10,
        total_tokens=30,
    )


def create_llm() -> Mock:

    llm = Mock(
        spec=LLM,
    )

    llm.generate.return_value = (
        create_llm_response()
    )

    return llm


def create_retrieval_pipeline() -> Mock:

    pipeline = Mock(
        spec=RetrievalPipeline,
    )

    pipeline.run.return_value = [
        create_result(),
    ]

    return pipeline


def create_pipeline():

    retrieval_pipeline = (
        create_retrieval_pipeline()
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


def test_pipeline_retrieval_pipeline_property():

    pipeline, retrieval_pipeline, _ = (
        create_pipeline()
    )

    assert (
        pipeline.retrieval_pipeline
        is retrieval_pipeline
    )


def test_pipeline_llm_property():

    pipeline, _, llm = create_pipeline()

    assert (
        pipeline.llm
        is llm
    )


def test_pipeline_run_returns_response():

    pipeline, _, _ = create_pipeline()

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


def test_pipeline_calls_retrieval_pipeline():

    (
        pipeline,
        retrieval_pipeline,
        _,
    ) = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
        minimum_score=0.75,
    )

    pipeline.run(
        request,
    )

    retrieval_pipeline.run.assert_called_once_with(
        "What is ScholarOS?",
        0.75,
    )


def test_pipeline_calls_llm():

    (
        pipeline,
        _,
        llm,
    ) = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    pipeline.run(
        request,
    )

    llm.generate.assert_called_once()


def test_pipeline_builds_system_message():

    (
        pipeline,
        _,
        llm,
    ) = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    pipeline.run(
        request,
    )

    messages = (
        llm.generate.call_args.args[0]
    )

    assert (
        messages[0].role
        == MessageRole.SYSTEM
    )

    assert (
        messages[0].content
        == (
            "You are a research assistant "
            "for ScholarOS. Answer the "
            "user's question using the "
            "provided knowledge context. "
            "If the context does not "
            "contain sufficient information "
            "to answer the question, say so "
            "instead of inventing facts."
        )
    )


def test_pipeline_builds_user_message():

    (
        pipeline,
        _,
        llm,
    ) = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    pipeline.run(
        request,
    )

    messages = (
        llm.generate.call_args.args[0]
    )

    assert (
        messages[1].role
        == MessageRole.USER
    )

    assert (
        messages[1].content
        == (
            "Knowledge Context:\n"
            "[Source 1: doc-001]\n"
            "ScholarOS is an AI research system.\n\n"
            "User Question:\n"
            "What is ScholarOS?"
        )
    )


def test_pipeline_response_content():

    pipeline, _, _ = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    response = pipeline.run(
        request,
    )

    assert (
        response.content
        == "ScholarOS is an AI research system."
    )


def test_pipeline_response_model():

    pipeline, _, _ = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    response = pipeline.run(
        request,
    )

    assert (
        response.model
        == "test-model"
    )


def test_pipeline_preserves_retrieval_results():

    pipeline, _, _ = create_pipeline()

    request = RAGRequest(
        query="What is ScholarOS?",
    )

    response = pipeline.run(
        request,
    )

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


def test_pipeline_preserves_token_usage():

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


def test_pipeline_empty_retrieval_results():

    retrieval_pipeline = Mock(
        spec=RetrievalPipeline,
    )

    retrieval_pipeline.run.return_value = []

    llm = create_llm()

    pipeline = RAGPipeline(
        retrieval_pipeline,
        llm,
    )

    request = RAGRequest(
        query="Unknown question",
    )

    response = pipeline.run(
        request,
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
            "Unknown question"
        )
    )


def test_pipeline_repr():

    pipeline, _, llm = create_pipeline()

    assert (
        repr(
            pipeline,
        )
        == (
            "RAGPipeline("
            f"llm={llm!r}"
            ")"
        )
    )