from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.loader import (
    RetrievalLoader,
)
from scholaros.retrieval.manager import (
    RetrievalManager,
)
from scholaros.retrieval.registry import (
    RetrievalRegistry,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_collection() -> RetrievalCollection:

    collection = RetrievalCollection()

    collection.add(
        RetrievalResult(
            source="knowledge:paper-001",
            content=(
                "Transformer models "
                "achieve state-of-the-art "
                "performance."
            ),
            score=0.96,
            metadata={
                "title": (
                    "Attention Is All You Need"
                ),
            },
        ),
    )

    return collection


def create_loader() -> RetrievalLoader:

    manager = RetrievalManager(
        RetrievalRegistry(),
    )

    return RetrievalLoader(
        manager,
    )


def test_loader_load():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is collection
    )


def test_loader_unload():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    loader.unload(
        "Research",
    )

    assert not loader.manager.contains(
        "Research",
    )


def test_loader_reload():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    loader.reload(
        "Research",
        collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is collection
    )


def test_loader_discover():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert (
        loader.discover()
        == [
            "Research",
        ]
    )


def test_loader_repr():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            loader,
        )
        == (
            "RetrievalLoader("
            "collections=1)"
        )
    )