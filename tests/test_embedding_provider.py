from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.provider import (
    EmbeddingProvider,
)


class DummyEmbeddingProvider(
    EmbeddingProvider,
):

    @property
    def name(
        self,
    ) -> str:

        return "Dummy"

    @property
    def description(
        self,
    ) -> str:

        return (
            "Dummy embedding provider."
        )

    @property
    def version(
        self,
    ) -> str:

        return "1.0.0"

    def embed(
        self,
        text: str,
    ) -> Embedding:

        return Embedding(
            text=text,
            vector=[
                0.10,
                0.20,
                0.30,
            ],
            metadata={},
        )


def create_provider() -> DummyEmbeddingProvider:

    return DummyEmbeddingProvider()


def test_name_property():

    provider = create_provider()

    assert (
        provider.name
        == "Dummy"
    )


def test_description_property():

    provider = create_provider()

    assert (
        provider.description
        ==
        "Dummy embedding provider."
    )


def test_version_property():

    provider = create_provider()

    assert (
        provider.version
        == "1.0.0"
    )


def test_embed():

    provider = create_provider()

    embedding = provider.embed(
        "ScholarOS",
    )

    assert isinstance(
        embedding,
        Embedding,
    )

    assert (
        embedding.text
        == "ScholarOS"
    )

    assert (
        embedding.vector
        ==
        [
            0.10,
            0.20,
            0.30,
        ]
    )


def test_repr():

    provider = create_provider()

    assert (
        repr(
            provider,
        )
        ==
        "DummyEmbeddingProvider("
        "name='Dummy', "
        "version='1.0.0'"
        ")"
    )