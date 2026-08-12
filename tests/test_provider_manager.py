from __future__ import annotations

from scholaros.ai.providers.manager import (
    ProviderManager,
)
from scholaros.ai.providers.registry import (
    ProviderRegistry,
)


class DummyProvider:
    pass


def test_default_registry() -> None:

    manager = ProviderManager()

    assert isinstance(
        manager.registry,
        ProviderRegistry,
    )


def test_custom_registry() -> None:

    registry = ProviderRegistry()

    manager = ProviderManager(
        registry,
    )

    assert manager.registry is registry


def test_register_provider() -> None:

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    assert manager.contains(
        "ollama",
    )

    assert len(
        manager,
    ) == 1


def test_get_provider() -> None:

    manager = ProviderManager()

    manager.register(
        "openai",
        DummyProvider,
    )

    provider = manager.get(
        "openai",
    )

    assert provider is DummyProvider


def test_contains() -> None:

    manager = ProviderManager()

    manager.register(
        "anthropic",
        DummyProvider,
    )

    assert manager.contains(
        "anthropic",
    )

    assert not manager.contains(
        "ollama",
    )


def test_names() -> None:

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    manager.register(
        "openai",
        DummyProvider,
    )

    assert manager.names() == (
        "ollama",
        "openai",
    )


def test_clear() -> None:

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    manager.register(
        "openai",
        DummyProvider,
    )

    manager.clear()

    assert len(
        manager,
    ) == 0

    assert manager.names() == ()


def test_len() -> None:

    manager = ProviderManager()

    assert len(
        manager,
    ) == 0

    manager.register(
        "ollama",
        DummyProvider,
    )

    assert len(
        manager,
    ) == 1


def test_contains_operator() -> None:

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    assert "ollama" in manager

    assert "openai" not in manager


def test_iter() -> None:

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    manager.register(
        "openai",
        DummyProvider,
    )

    items = list(
        manager,
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

    manager = ProviderManager()

    manager.register(
        "ollama",
        DummyProvider,
    )

    text = repr(
        manager,
    )

    assert "ProviderManager" in text

    assert "ollama" in text


def test_case_insensitive_lookup() -> None:

    manager = ProviderManager()

    manager.register(
        "OpenAI",
        DummyProvider,
    )

    assert manager.get(
        "openai",
    ) is DummyProvider

    assert manager.get(
        "OPENAI",
    ) is DummyProvider


def test_registry_property() -> None:

    manager = ProviderManager()

    registry = manager.registry

    registry.register(
        "ollama",
        DummyProvider,
    )

    assert manager.contains(
        "ollama",
    )

    assert manager.get(
        "ollama",
    ) is DummyProvider