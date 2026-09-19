"""
ScholarOS Sensitive Logging Prevention.

Scrubs API keys, authentication tokens, passwords, and private secrets
from log records and messages before emission.
"""

from __future__ import annotations

import logging
import re


# Patterns identifying sensitive credentials in strings
SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("anthropic_key", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{16,}")),
    ("openai_key", re.compile(r"sk-[a-zA-Z0-9_\-]{20,}")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}")),
    ("github_token", re.compile(r"gh[pous]_[a-zA-Z0-9]{36,}")),
    ("key_assignment", re.compile(r"(?i)(password|secret|api_key|access_token|private_key)\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?")),
]


def redact_sensitive_text(text: str) -> str:
    """
    Scan string and replace sensitive tokens with [REDACTED].

    Parameters
    ----------
    text : str
        Input string.

    Returns
    -------
    str
        Redacted string safe for logging.
    """
    if not text:
        return ""

    result = str(text)

    # Specific token formats
    for name, pattern in SENSITIVE_PATTERNS:
        if name == "key_assignment":
            # Keep key name, mask the secret value
            result = pattern.sub(r"\1=[REDACTED]", result)
        elif name == "bearer_token":
            result = pattern.sub("Bearer [REDACTED]", result)
        else:
            result = pattern.sub("[REDACTED_KEY]", result)

    return result


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that intercepts and redacts sensitive data from LogRecord instances.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize message and formatting arguments in place."""
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_text(record.msg)

        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(
                    redact_sensitive_text(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
            elif isinstance(record.args, dict):
                record.args = {
                    k: (redact_sensitive_text(str(v)) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }

        return True


def install_sensitive_data_filter(logger: logging.Logger | None = None) -> None:
    """
    Attach SensitiveDataFilter to the specified logger and all its existing handlers.
    """
    target = logger or logging.getLogger("ScholarOS")
    scrubber = SensitiveDataFilter()
    target.addFilter(scrubber)
    for handler in target.handlers:
        handler.addFilter(scrubber)


__all__ = [
    "SENSITIVE_PATTERNS",
    "SensitiveDataFilter",
    "install_sensitive_data_filter",
    "redact_sensitive_text",
]
