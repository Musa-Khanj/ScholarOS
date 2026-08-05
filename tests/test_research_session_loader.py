from scholaros.research.loader import (
    ResearchSessionLoader,
)
from scholaros.research.manager import (
    ResearchSessionManager,
)


def create_loader() -> ResearchSessionLoader:

    return ResearchSessionLoader()


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        ResearchSessionManager,
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
        "ResearchSessionLoader("
        "manager="
        "ResearchSessionManager"
        ")"
    )