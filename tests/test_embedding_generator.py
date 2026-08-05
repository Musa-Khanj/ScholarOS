from scholaros.embeddings.embedding import (
    Embedding,
)
from scholaros.embeddings.generator import (
    EmbeddingGenerator,
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


def create_generator() -> EmbeddingGenerator:

    return EmbeddingGenerator(
        DummyEmbeddingProvider(),
    )


def test_provider_property():

    generator = create_generator()

    assert isinstance(
        generator.provider,
        EmbeddingProvider,
    )


def test_generate():

    generator = create_generator()

    embedding = generator.generate(
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

    generator = create_generator()

    assert (
        repr(
            generator,
        )
        ==
        "EmbeddingGenerator("
        "provider='Dummy'"
        ")"
    )