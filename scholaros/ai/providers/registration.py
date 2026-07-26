from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.ollama import OllamaLLM
from scholaros.container import Container


def register_ai_services(
    container: Container,
) -> None:

    container.add_singleton(
        LLM,
        OllamaLLM,
    )