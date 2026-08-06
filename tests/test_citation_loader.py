from scholaros.research.citation_loader import (
    CitationLoader,
)
from scholaros.research.citation_manager import (
    CitationManager,
)


def create_loader() -> CitationLoader:

    return CitationLoader()


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        CitationManager,
    )


def test_manager_is_singleton():

    loader = create_loader()

    assert (
        loader.manager
        is loader.manager
    )


def test_repr():

    loader = create_loader()

    assert (
        repr(
            loader,
        )
        ==
        "CitationLoader("
        "manager="
        "CitationManager"
        ")"
    )