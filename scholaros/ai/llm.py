"""
ScholarOS
LLM Compatibility Module

Version : 1.0
Status  : Stable

Description
-----------
Backward-compatible re-exports for the
ScholarOS LLM package.

This module exists for compatibility with older
imports. The canonical implementation now lives
under scholaros.ai.llm.
"""

from scholaros.ai.llm.base import (
    LLM,
)
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.ollama import (
    OllamaLLM,
)
from scholaros.ai.llm.response import (
    LLMResponse,
)

__all__ = [
    "LLM",
    "LLMResponse",
    "Message",
    "MessageRole",
    "OllamaLLM",
]