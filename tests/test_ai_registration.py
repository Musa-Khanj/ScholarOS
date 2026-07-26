from scholaros.ai.llm import LLM
from scholaros.ai.llm.ollama import OllamaLLM
from scholaros.ai.providers import register_ai_services
from scholaros.container import Container


def test_register_ai_services():

    container = Container()

    register_ai_services(container)

    llm = container.resolve(LLM)

    assert isinstance(
        llm,
        OllamaLLM,
    )