"""
Artificial Intelligence subsystem.
"""

from scholaros.ai.llm import LLM
from scholaros.ai.ollama_client import OllamaClient
from scholaros.ai.response import AIResponse

__all__ = [
    "AIResponse",
    "LLM",
    "OllamaClient",
]