from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.loader import (
    EmbeddingLoader,
)
from scholaros.embeddings.manager import (
    EmbeddingManager,
)
from scholaros.embeddings.registry import (
    EmbeddingRegistry,
)


def create_loader() -> EmbeddingLoader:

    return EmbeddingLoader(
        EmbeddingManager(
            EmbeddingRegistry(),
        ),
    )


def create_collection() -> EmbeddingCollection:

    return EmbeddingCollection()


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        EmbeddingManager,
    )


def test_load():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "default",
        collection,
    )

    assert (
        loader.manager.get(
            "default",
        )
        is collection
    )


def test_unload():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "default",
        collection,
    )

    loader.unload(
        "default",
    )

    assert (
        loader.manager.get(
            "default",
        )
        is None
    )


def test_reload():

    loader = create_loader()

    first = create_collection()

    second = create_collection()

    loader.load(
        "default",
        first,
    )

    loader.reload(
        "default",
        second,
    )

    assert (
        loader.manager.get(
            "default",
        )
        is second
    )


def test_discover():

    loader = create_loader()

    loader.load(
        "one",
        create_collection(),
    )

    loader.load(
        "two",
        create_collection(),
    )

    assert (
        loader.discover()
        ==
        [
            "one",
            "two",
        ]
    )


def test_repr():

    loader = create_loader()

    loader.load(
        "default",
        create_collection(),
    )

    assert (
        repr(
            loader,
        )
        ==
        "EmbeddingLoader("
        "collections=1)"
    )