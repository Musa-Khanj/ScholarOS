"""
ScholarOS Security Subsystem.

Provides comprehensive defenses for:
- RAG security, prompt injection boundaries, and untrusted context isolation
- Plugin capability verification and sandboxing
- Path traversal mitigation and safe file I/O
- Sensitive credential scrubbing and log filtering
- System security audits and vulnerability checks
"""

from __future__ import annotations

from scholaros.security.audit import (
    SecurityAuditReport,
    SecurityFinding,
    audit_system_security,
)
from scholaros.security.exceptions import (
    CapabilityViolationError,
    PathTraversalError,
    PromptInjectionError,
    SecretLeakError,
    SecurityError,
)
from scholaros.security.logging import (
    SENSITIVE_PATTERNS,
    SensitiveDataFilter,
    install_sensitive_data_filter,
    redact_sensitive_text,
)
from scholaros.security.path import (
    safe_read_text,
    safe_write_text,
    validate_safe_path,
)
from scholaros.security.plugins import (
    STANDARD_CAPABILITIES,
    SecureCapabilitySandbox,
    validate_plugin_manifest,
)
from scholaros.security.rag import (
    INJECTION_SIGNATURES,
    SYSTEM_DEFENSE_DIRECTIVE,
    detect_prompt_injection,
    escape_context_delimiters,
    format_isolated_chunk,
    format_secure_rag_context,
)

__all__ = [
    "CapabilityViolationError",
    "INJECTION_SIGNATURES",
    "PathTraversalError",
    "PromptInjectionError",
    "SENSITIVE_PATTERNS",
    "SYSTEM_DEFENSE_DIRECTIVE",
    "SecretLeakError",
    "SecureCapabilitySandbox",
    "SecurityAuditReport",
    "SecurityError",
    "SecurityFinding",
    "SensitiveDataFilter",
    "STANDARD_CAPABILITIES",
    "audit_system_security",
    "detect_prompt_injection",
    "escape_context_delimiters",
    "format_isolated_chunk",
    "format_secure_rag_context",
    "install_sensitive_data_filter",
    "redact_sensitive_text",
    "safe_read_text",
    "safe_write_text",
    "validate_plugin_manifest",
    "validate_safe_path",
]
