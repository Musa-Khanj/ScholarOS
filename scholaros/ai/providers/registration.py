from scholaros.ai.llm.anthropic import AnthropicLLM
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.mock import MockLLM
from scholaros.ai.llm.ollama import OllamaLLM
from scholaros.ai.llm.openai import OpenAILLM
from scholaros.ai.prompt.executor import PromptExecutor
from scholaros.config.model import LLMConfig
from scholaros.container import Container
from scholaros.container.lifetime import ServiceLifetime


def register_ai_services(
    container: Container,
) -> None:
    def llm_factory() -> LLM:
        if container.registry.contains(LLMConfig):
            cfg = container.resolve(LLMConfig)
            provider_name = cfg.provider.strip().lower()
            if provider_name == "openai":
                return OpenAILLM(
                    api_key=cfg.api_key or "sk-test",
                    model=cfg.model,
                    base_url=cfg.base_url,
                )
            elif provider_name == "anthropic":
                return AnthropicLLM(
                    api_key=cfg.api_key or "test",
                    model=cfg.model,
                    base_url=cfg.base_url,
                )
            elif provider_name == "mock":
                return MockLLM(model=cfg.model)
            else:
                return OllamaLLM(
                    model=cfg.model,
                    base_url=cfg.base_url,
                )
        return OllamaLLM()

    container.add_factory(
        LLM,
        llm_factory,
        lifetime=ServiceLifetime.SINGLETON,
    )

    container.add_singleton(
        PromptExecutor,
        PromptExecutor,
    )
