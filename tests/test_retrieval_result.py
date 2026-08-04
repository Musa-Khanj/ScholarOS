from scholaros.retrieval.result import RetrievalResult


def create_result() -> RetrievalResult:

    return RetrievalResult(
        source="knowledge:paper-001",
        content="Transformer models achieve state-of-the-art performance.",
        score=0.96,
        metadata={
            "title": "Attention Is All You Need",
        },
    )


def test_source_property():

    result = create_result()

    assert (
        result.source
        == "knowledge:paper-001"
    )


def test_content_property():

    result = create_result()

    assert (
        result.content
        == "Transformer models achieve "
        "state-of-the-art performance."
    )


def test_score_property():

    result = create_result()

    assert (
        result.score
        == 0.96
    )


def test_metadata_property():

    result = create_result()

    assert (
        result.metadata
        == {
            "title": (
                "Attention Is All You Need"
            ),
        }
    )


def test_to_dict():

    result = create_result()

    assert (
        result.to_dict()
        == {
            "source": (
                "knowledge:paper-001"
            ),
            "content": (
                "Transformer models "
                "achieve state-of-the-art "
                "performance."
            ),
            "score": 0.96,
            "metadata": {
                "title": (
                    "Attention Is All You Need"
                ),
            },
        }
    )


def test_repr():

    result = create_result()

    assert (
        repr(
            result,
        )
        == (
            "RetrievalResult("
            "source='knowledge:paper-001', "
            "score=0.96)"
        )
    )


def test_default_metadata():

    result = RetrievalResult(
        source="memory:user",
        content="User prefers IEEE.",
        score=0.90,
    )

    assert result.metadata == {}