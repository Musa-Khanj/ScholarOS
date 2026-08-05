from scholaros.embeddings.embedding import (
    Embedding,
)


def create_embedding() -> Embedding:

    return Embedding(
        text=(
            "Transformer models "
            "improve natural language "
            "processing."
        ),
        vector=[
            0.12,
            0.34,
            0.56,
            0.78,
        ],
        metadata={
            "source": "paper-1",
            "title": (
                "Attention Is All You Need"
            ),
        },
    )


def test_text_property():

    embedding = create_embedding()

    assert (
        embedding.text
        ==
        "Transformer models "
        "improve natural language "
        "processing."
    )


def test_vector_property():

    embedding = create_embedding()

    assert (
        embedding.vector
        ==
        [
            0.12,
            0.34,
            0.56,
            0.78,
        ]
    )


def test_metadata_property():

    embedding = create_embedding()

    assert (
        embedding.metadata
        ==
        {
            "source": "paper-1",
            "title": (
                "Attention Is All You Need"
            ),
        }
    )


def test_vector_is_copy():

    embedding = create_embedding()

    vector = embedding.vector

    vector.append(
        1.00,
    )

    assert (
        len(
            embedding.vector,
        )
        == 4
    )


def test_metadata_is_copy():

    embedding = create_embedding()

    metadata = embedding.metadata

    metadata[
        "author"
    ] = "OpenAI"

    assert (
        "author"
        not in embedding.metadata
    )


def test_len():

    embedding = create_embedding()

    assert (
        len(
            embedding,
        )
        == 4
    )


def test_repr():

    embedding = create_embedding()

    assert (
        repr(
            embedding,
        )
        ==
        "Embedding(dimensions=4)"
    )