"""
ScholarOS System Security Auditing.

Performs vulnerability scanning on runtime configuration, environment variables,
file system paths, and network endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass(slots=True)
class SecurityFinding:
    """Represents a single security audit finding."""

    severity: str  # "HIGH", "MEDIUM", "LOW", "INFO"
    category: str  # "configuration", "environment", "filesystem", "network"
    title: str
    description: str
    remediation: str


@dataclass(slots=True)
class SecurityAuditReport:
    """Summary report of security audit findings."""

    findings: list[SecurityFinding] = field(default_factory=list)

    @property
    def is_secure(self) -> bool:
        """Return True if no HIGH severity security vulnerabilities are present."""
        return not any(f.severity == "HIGH" for f in self.findings)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "HIGH")

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "MEDIUM")

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "LOW")

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_secure": self.is_secure,
            "total_findings": len(self.findings),
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "title": f.title,
                    "description": f.description,
                    "remediation": f.remediation,
                }
                for f in self.findings
            ],
        }


def audit_system_security(
    config: Any = None,
    workspace: Path | None = None,
) -> SecurityAuditReport:
    """
    Perform a comprehensive security audit of ScholarOS configuration and environment.

    Parameters
    ----------
    config : Any
        Active AppConfig or ConfigManager instance.
    workspace : Path | None
        Optional workspace directory.

    Returns
    -------
    SecurityAuditReport
        Detailed audit findings report.
    """
    findings: list[SecurityFinding] = []

    # 1. Configuration checks
    if config is not None:
        cfg = getattr(config, "config", config)
        env = getattr(cfg, "environment", "development")
        debug = getattr(cfg, "debug", False)

        if env.lower() == "production" and debug:
            findings.append(
                SecurityFinding(
                    severity="HIGH",
                    category="configuration",
                    title="Debug Mode Enabled in Production",
                    description="Debug mode exposes internal traces and potential memory dumps.",
                    remediation="Set debug = false in production configuration.",
                )
            )

        # AI Base URL transport check
        ai_cfg = getattr(cfg, "ai", None)
        if ai_cfg is not None:
            base_url = getattr(ai_cfg, "base_url", "")
            if base_url:
                parsed = urlparse(base_url)
                is_local = parsed.hostname in ("localhost", "127.0.0.1", "::1")
                if parsed.scheme == "http" and not is_local:
                    findings.append(
                        SecurityFinding(
                            severity="HIGH",
                            category="network",
                            title="Insecure Plain HTTP AI Endpoint",
                            description=f"Remote AI provider endpoint '{base_url}' uses unencrypted HTTP.",
                            remediation="Use HTTPS for remote provider endpoints to prevent credential sniffing.",
                        )
                    )

    # 2. Environment checks for exposed secrets
    env_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "SCHOLAROS_AI_API_KEY"]
    for k in env_keys:
        val = os.environ.get(k)
        if val and len(val) < 10:
            findings.append(
                SecurityFinding(
                    severity="MEDIUM",
                    category="environment",
                    title=f"Weak API Key in Environment ({k})",
                    description=f"Environment variable {k} contains an abnormally short or placeholder value.",
                    remediation="Ensure valid, high-entropy API keys are configured.",
                )
            )

    # 3. Workspace check
    if workspace is not None:
        ws_dir = Path(workspace)
    elif config is not None and hasattr(config, "storage") and hasattr(config.storage, "workspace"):
        ws_dir = Path(config.storage.workspace)
    else:
        ws_dir = Path("workspace")
    if ws_dir.exists() and not os.access(ws_dir, os.W_OK):
        findings.append(
            SecurityFinding(
                severity="MEDIUM",
                category="filesystem",
                title="Workspace Directory Not Writable",
                description=f"Workspace path '{ws_dir}' exists but is not writable.",
                remediation="Adjust filesystem permissions on the workspace directory.",
            )
        )

    return SecurityAuditReport(findings=findings)


__all__ = [
    "SecurityAuditReport",
    "SecurityFinding",
    "audit_system_security",
]
