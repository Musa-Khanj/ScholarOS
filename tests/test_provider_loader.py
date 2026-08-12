from __future__ import annotations

from scholaros.ai.llm.anthropic import (
    AnthropicLLM,
)
from scholaros.ai.llm.ollama import (
    OllamaLLM,
)
from scholaros.ai.llm.openai import (
    OpenAILLM,
)
from scholaros.ai.providers.loader import (
    ProviderLoader,
)
from scholaros.ai.providers.manager import (
    ProviderManager,
)


def test_manager_property() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    assert loader.manager is manager


def test_load_registers_builtin_providers() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    loader.load()

    assert manager.contains(
        "ollama",
    )

    assert manager.contains(
        "openai",
    )

    assert manager.contains(
        "anthropic",
    )

    assert len(
        manager,
    ) == 3


def test_load_registers_correct_classes() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    loader.load()

    assert (
        manager.get(
            "ollama",
        )
        is OllamaLLM
    )

    assert (
        manager.get(
            "openai",
        )
        is OpenAILLM
    )

    assert (
        manager.get(
            "anthropic",
        )
        is AnthropicLLM
    )


def test_load_is_idempotent() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    loader.load()

    loader.load()

    assert len(
        manager,
    ) == 3


def test_load_preserves_existing_providers() -> None:

    class DummyProvider:
        pass

    manager = ProviderManager()

    manager.register(
        "dummy",
        DummyProvider,
    )

    loader = ProviderLoader(
        manager,
    )

    loader.load()

    assert manager.contains(
        "dummy",
    )

    assert (
        manager.get(
            "dummy",
        )
        is DummyProvider
    )

    assert len(
        manager,
    ) == 4


def test_names_after_load() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    loader.load()

    assert manager.names() == (
        "ollama",
        "openai",
        "anthropic",
    )


def test_repr() -> None:

    manager = ProviderManager()

    loader = ProviderLoader(
        manager,
    )

    text = repr(
        loader,
    )

    assert "ProviderLoader" in text

    assert "providers=" in text