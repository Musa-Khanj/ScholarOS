from scholaros.collaboration.agent_loader import (
    AgentLoader,
)
from scholaros.collaboration.agent_manager import (
    AgentManager,
)


def create_loader() -> AgentLoader:

    return AgentLoader()


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        AgentManager,
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
        "AgentLoader("
        "manager="
        "AgentManager"
        ")"
    )