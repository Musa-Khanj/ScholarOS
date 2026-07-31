from scholaros.ai.prompt_catalog import (
    PromptCatalog,
)
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)


def test_register_template():

    catalog = PromptCatalog()

    template = PromptTemplate(
        name="example",
        template="Example prompt",
    )

    catalog.register(template)

    assert len(catalog) == 1


def test_load_defaults():

    catalog = PromptCatalog()

    catalog.load_defaults()

    assert len(catalog) == 3


def test_templates():

    catalog = PromptCatalog()

    catalog.load_defaults()

    templates = catalog.templates()

    assert len(templates) == 3

    assert templates[0].name == "research_summary"

    assert templates[1].name == "code_review"

    assert templates[2].name == "literature_review"


def test_load_into_registry():

    catalog = PromptCatalog()

    catalog.load_defaults()

    registry = PromptRegistry()

    catalog.load_into(registry)

    assert registry.contains(
        "research_summary"
    )

    assert registry.contains(
        "code_review"
    )

    assert registry.contains(
        "literature_review"
    )

    assert len(registry) == 3


def test_empty_catalog():

    catalog = PromptCatalog()

    assert len(catalog) == 0

    assert catalog.templates() == []