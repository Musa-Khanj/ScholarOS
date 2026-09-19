"""
ScholarOS
RAG

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Retrieval-Augmented Generation
components for ScholarOS.
"""

from scholaros.knowledge.rag.configuration import (
    RAGConfiguration,
)
from scholaros.knowledge.rag.context import (
    RAGContext,
)
from scholaros.knowledge.rag.events import (
    RAGCompleted,
    RAGEvent,
    RAGFailed,
    RAGFallbackTriggered,
    RAGStarted,
)
from scholaros.knowledge.rag.exceptions import (
    RAGConfigurationError,
    RAGContextError,
    RAGError,
    RAGGenerationError,
    RAGPipelineError,
    RAGTimeoutError,
)
from scholaros.knowledge.rag.pipeline import (
    RAGPipeline,
)
from scholaros.knowledge.rag.request import (
    RAGRequest,
)
from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.knowledge.rag.service import (
    RAGService,
)

__all__ = [
    "RAGCompleted",
    "RAGConfiguration",
    "RAGConfigurationError",
    "RAGContext",
    "RAGContextError",
    "RAGError",
    "RAGEvent",
    "RAGFailed",
    "RAGFallbackTriggered",
    "RAGGenerationError",
    "RAGPipeline",
    "RAGPipelineError",
    "RAGRequest",
    "RAGResponse",
    "RAGService",
    "RAGStarted",
    "RAGTimeoutError",
]
