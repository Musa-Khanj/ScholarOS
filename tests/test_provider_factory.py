from __future__ import annotations

import pytest

from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message
from scholaros.ai.llm.response import LLMResponse
from scholaros.ai.providers.factory import (
    ProviderFactory,
)
from scholaros.ai.providers.manager import (
    ProviderManager,
)


class DummyLLM(LLM):

    def __init__(
        self,
        value: int = 0,
    ) -> None:

        self.value = value

    def generate(
        self,
        messages: list[Message] | str,
    ) -> LLMResponse:

        return LLMResponse(
            content="dummy",
            model="dummy",
        )

    @property
    def model(
        self,
    ) -> str:

        return "dummy"


class InvalidProvider:

    pass


def test_manager_property() -> None:

    manager = ProviderManager()

    factory = ProviderFactory(
        manager,
    )

    assert factory.manager is manager


def test_create_provider() -> None:

    manager = ProviderManager()

    manager.register(
        "dummy",
        DummyLLM,
    )

    factory = ProviderFactory(
        manager,
    )

    llm = factory.create(
        "dummy",
    )

    assert isinstance(
        llm,
        DummyLLM,
    )


def test_create_passes_arguments() -> None:

    manager = ProviderManager()

    manager.register(
        "dummy",
        DummyLLM,
    )

    factory = ProviderFactory(
        manager,
    )

    llm = factory.create(
        "dummy",
        value=123,
    )

    assert llm.value == 123


def test_unknown_provider() -> None:

    manager = ProviderManager()

    factory = ProviderFactory(
        manager,
    )

    with pytest.raises(
        KeyError,
    ):
        factory.create(
            "missing",
        )


def test_invalid_provider_type() -> None:

    manager = ProviderManager()

    manager.register(
        "invalid",
        InvalidProvider,
    )

    factory = ProviderFactory(
        manager,
    )

    with pytest.raises(
        TypeError,
    ):
        factory.create(
            "invalid",
        )


def test_repr() -> None:

    manager = ProviderManager()

    factory = ProviderFactory(
        manager,
    )

    text = repr(
        factory,
    )

    assert "ProviderFactory" in text

    assert "providers=" in text


def test_multiple_instances_are_distinct() -> None:

    manager = ProviderManager()

    manager.register(
        "dummy",
        DummyLLM,
    )

    factory = ProviderFactory(
        manager,
    )

    first = factory.create(
        "dummy",
    )

    second = factory.create(
        "dummy",
    )

    assert first is not second


def test_case_insensitive_lookup() -> None:

    manager = ProviderManager()

    manager.register(
        "Dummy",
        DummyLLM,
    )

    factory = ProviderFactory(
        manager,
    )

    llm = factory.create(
        "DUMMY",
    )

    assert isinstance(
        llm,
        DummyLLM,
    )