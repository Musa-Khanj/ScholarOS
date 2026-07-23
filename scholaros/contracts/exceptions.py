class ScholarOSError(Exception):
    """Base exception for ScholarOS."""


class ConfigurationError(ScholarOSError):
    """Configuration failure."""


class PluginError(ScholarOSError):
    """Plugin failure."""


class ToolError(ScholarOSError):
    """Tool failure."""


class AgentError(ScholarOSError):
    """Agent failure."""


class RegistryError(ScholarOSError):
    """Registry failure."""


class MemoryError(ScholarOSError):
    """Memory subsystem failure."""


class VisionError(ScholarOSError):
    """Vision subsystem failure."""


class LLMError(ScholarOSError):
    """LLM subsystem failure."""


class RAGError(ScholarOSError):
    """RAG subsystem failure."""