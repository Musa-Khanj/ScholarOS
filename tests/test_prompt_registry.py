from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)


def test_register_template():

    registry = PromptRegistry()

    template = PromptTemplate(
        name="research",
        template="Summarize {topic}",
        description="Research summary",
    )

    registry.register(template)

    assert registry.contains("research")


def test_get_template():

    registry = PromptRegistry()

    template = PromptTemplate(
        name="research",
        template="Summarize {topic}",
    )

    registry.register(template)

    result = registry.get("research")

    assert result is template


def test_all_templates():

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="one",
            template="Prompt One",
        )
    )

    registry.register(
        PromptTemplate(
            name="two",
            template="Prompt Two",
        )
    )

    templates = registry.all()

    assert len(templates) == 2

    assert templates[0].name == "one"

    assert templates[1].name == "two"


def test_registry_length():

    registry = PromptRegistry()

    assert len(registry) == 0

    registry.register(
        PromptTemplate(
            name="example",
            template="Example Prompt",
        )
    )

    assert len(registry) == 1


def test_contains_unknown_template():

    registry = PromptRegistry()

    assert not registry.contains("unknown")


def test_get_unknown_template_raises():

    registry = PromptRegistry()

    try:

        registry.get("missing")

        assert False

    except KeyError:

        assert True