from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.ollama import OllamaLLM
from scholaros.container import Container
from scholaros.ai.prompt.executor import PromptExecutor


def register_ai_services(
    container: Container,
) -> None:

    container.add_singleton(
        LLM,
        OllamaLLM,
    )

    container.add_singleton(
        PromptExecutor,
        PromptExecutor,
    )