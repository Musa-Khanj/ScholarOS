"""
ScholarOS Artificial Intelligence Subsystem.

Comprehensive AI architecture providing:
- Unified provider interface (generate, stream, embed, health)
- Multi-provider model routing, retries, and failovers
- Middleware pipeline for logging, safety, caching, and telemetry
- Stateful sessions and multi-turn conversations
- Token streaming and dense vector embeddings
- Service framework and DI container integration
"""

from __future__ import annotations

from scholaros.ai.cache import ResponseCache
from scholaros.ai.client import AIClient
from scholaros.ai.conversation import Conversation
from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.exceptions import (
    AIError,
    AuthenticationError,
    ContextLengthExceededError,
    EmbeddingError,
    MiddlewareError,
    ModelNotFoundError,
    ProviderError,
    ProviderNotFoundError,
    RateLimitError,
    SafetyViolationError,
    StreamingError,
)
from scholaros.ai.factory import AIFactory
from scholaros.ai.llm import LLM
from scholaros.ai.manager import (
    AIEvent,
    AIManager,
    AIProviderChanged,
    AIRequestCompleted,
    AIRequestFailed,
    AIRequestStarted,
    AIStreamCompleted,
    AIStreamStarted,
)
from scholaros.ai.message import Message, MessageRole, Role
from scholaros.ai.metrics import AIMetrics
from scholaros.ai.middleware import (
    AIMiddleware,
    CachingMiddleware,
    LoggingMiddleware,
    MiddlewarePipeline,
    SafetyMiddleware,
    TelemetryMiddleware,
)
from scholaros.ai.models import (
    KNOWN_MODELS,
    ModelCapability,
    ModelSpec,
    ModelTier,
    get_model_spec,
)
from scholaros.ai.ollama_client import OllamaClient
from scholaros.ai.provider import AIProvider
from scholaros.ai.registry import ProviderRegistry
from scholaros.ai.request import AIRequest, CompletionRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.retry import FailoverChain, RetryPolicy
from scholaros.ai.service import AIService
from scholaros.ai.session import AISession
from scholaros.ai.streaming import StreamChunk, StreamingIterator
from scholaros.ai.tokenizer import Tokenizer, count_tokens

__all__ = [
    # Core & Legacy
    "AIClient",
    "AIError",
    "AIEvent",
    "AIFactory",
    "AIManager",
    "AIMetrics",
    "AIMiddleware",
    "AIProvider",
    "AIProviderChanged",
    "AIRequest",
    "AIRequestCompleted",
    "AIRequestFailed",
    "AIRequestStarted",
    "AIResponse",
    "AIService",
    "AISession",
    "AIStreamCompleted",
    "AIStreamStarted",
    "AuthenticationError",
    "CachingMiddleware",
    "CompletionRequest",
    "ContextLengthExceededError",
    "Conversation",
    "EmbeddingError",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "FailoverChain",
    "KNOWN_MODELS",
    "LLM",
    "LoggingMiddleware",
    "Message",
    "MessageRole",
    "MiddlewareError",
    "MiddlewarePipeline",
    "ModelCapability",
    "ModelNotFoundError",
    "ModelSpec",
    "ModelTier",
    "OllamaClient",
    "ProviderError",
    "ProviderNotFoundError",
    "ProviderRegistry",
    "RateLimitError",
    "ResponseCache",
    "RetryPolicy",
    "Role",
    "SafetyMiddleware",
    "SafetyViolationError",
    "StreamChunk",
    "StreamingError",
    "StreamingIterator",
    "TelemetryMiddleware",
    "Tokenizer",
    "count_tokens",
    "get_model_spec",
]
