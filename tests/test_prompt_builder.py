from scholaros.ai.prompt_builder import (
    PromptBuilder,
)
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)


def create_builder() -> PromptBuilder:

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="summary",
            template="Summarize {topic}.",
        )
    )

    return PromptBuilder(registry)


def test_build_prompt():

    builder = create_builder()

    prompt = builder.build(
        "summary",
        topic="Artificial Intelligence",
    )

    assert (
        prompt
        == "Summarize Artificial Intelligence."
    )


def test_contains():

    builder = create_builder()

    assert builder.contains(
        "summary"
    )

    assert not builder.contains(
        "missing"
    )


def test_template():

    builder = create_builder()

    template = builder.template(
        "summary"
    )

    assert (
        template.name
        == "summary"
    )

    assert (
        template.template
        == "Summarize {topic}."
    )


def test_registry():

    builder = create_builder()

    registry = builder.registry()

    assert registry.contains(
        "summary"
    )


def test_repr():

    builder = create_builder()

    representation = repr(builder)

    assert "PromptBuilder" in representation

    assert "templates=1" in representation


def test_build_unknown_template():

    builder = create_builder()

    try:

        builder.build(
            "missing",
        )

        assert False

    except KeyError:

        assert True


def test_missing_variable():

    builder = create_builder()

    try:

        builder.build(
            "summary",
        )

        assert False

    except KeyError:

        assert True