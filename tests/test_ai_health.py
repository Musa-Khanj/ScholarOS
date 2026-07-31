from scholaros.ai.health import (
    AIHealth,
    AIHealthChecker,
)


def test_health_success():

    checker = AIHealthChecker(
        provider="ollama",
        model="qwen2.5:1.5b",
    )

    health = checker.check()

    assert isinstance(
        health,
        AIHealth,
    )

    assert health.available

    assert health.healthy

    assert (
        health.provider
        == "ollama"
    )

    assert (
        health.model
        == "qwen2.5:1.5b"
    )


def test_health_failure():

    class FailingChecker(
        AIHealthChecker,
    ):

        def _probe(self) -> None:

            raise RuntimeError(
                "Provider unavailable."
            )

    checker = FailingChecker(
        provider="ollama",
        model="qwen2.5:1.5b",
    )

    health = checker.check()

    assert not health.available

    assert not health.healthy

    assert (
        health.message
        == "Provider unavailable."
    )


def test_provider_property():

    checker = AIHealthChecker(
        provider="ollama",
        model="qwen2.5:1.5b",
    )

    assert (
        checker.provider
        == "ollama"
    )


def test_model_property():

    checker = AIHealthChecker(
        provider="ollama",
        model="qwen2.5:1.5b",
    )

    assert (
        checker.model
        == "qwen2.5:1.5b"
    )