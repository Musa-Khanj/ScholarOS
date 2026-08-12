from __future__ import annotations

import pytest

from scholaros.ai.providers.registry import (
    ProviderRegistry,
)


class DummyProvider:
    pass


def test_register_provider() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    assert registry.contains(
        "ollama",
    )

    assert len(
        registry,
    ) == 1


def test_register_duplicate_provider() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    with pytest.raises(
        ValueError,
    ):
        registry.register(
            "ollama",
            DummyProvider,
        )


def test_register_empty_name() -> None:

    registry = ProviderRegistry()

    with pytest.raises(
        ValueError,
    ):
        registry.register(
            "",
            DummyProvider,
        )


def test_get_provider() -> None:

    registry = ProviderRegistry()

    registry.register(
        "openai",
        DummyProvider,
    )

    provider = registry.get(
        "openai",
    )

    assert provider is DummyProvider


def test_get_unknown_provider() -> None:

    registry = ProviderRegistry()

    with pytest.raises(
        KeyError,
    ):
        registry.get(
            "unknown",
        )


def test_contains() -> None:

    registry = ProviderRegistry()

    registry.register(
        "anthropic",
        DummyProvider,
    )

    assert registry.contains(
        "anthropic",
    )

    assert not registry.contains(
        "openai",
    )


def test_names() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    registry.register(
        "openai",
        DummyProvider,
    )

    assert registry.names() == (
        "ollama",
        "openai",
    )


def test_clear() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    registry.register(
        "openai",
        DummyProvider,
    )

    registry.clear()

    assert len(
        registry,
    ) == 0

    assert registry.names() == ()


def test_len() -> None:

    registry = ProviderRegistry()

    assert len(
        registry,
    ) == 0

    registry.register(
        "ollama",
        DummyProvider,
    )

    assert len(
        registry,
    ) == 1


def test_contains_operator() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    assert "ollama" in registry

    assert "openai" not in registry


def test_iter() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    registry.register(
        "openai",
        DummyProvider,
    )

    items = list(
        registry,
    )

    assert items == [
        (
            "ollama",
            DummyProvider,
        ),
        (
            "openai",
            DummyProvider,
        ),
    ]


def test_repr() -> None:

    registry = ProviderRegistry()

    registry.register(
        "ollama",
        DummyProvider,
    )

    text = repr(
        registry,
    )

    assert "ProviderRegistry" in text

    assert "ollama" in text


def test_case_insensitive_registration() -> None:

    registry = ProviderRegistry()

    registry.register(
        "OpenAI",
        DummyProvider,
    )

    assert registry.contains(
        "openai",
    )

    assert registry.contains(
        "OPENAI",
    )

    assert registry.get(
        "OPENAI",
    ) is DummyProvider