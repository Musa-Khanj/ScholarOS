"""
ScholarOS Observability - Execution & RAG Tracing.

Captures comprehensive end-to-end execution traces for RAG and research queries:
Query -> Strategy -> Retrieved Documents -> Scores -> Context -> Prompt -> Model -> Response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class RetrievedChunkTrace:
    """Diagnostic trace for an individual retrieved knowledge chunk."""

    document_id: str
    chunk_id: str
    score: float
    content_snippet: str
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "score": round(self.score, 4),
            "content_snippet": self.content_snippet,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class RAGTrace:
    """
    End-to-end diagnostic trace of a RAG query execution.

    Allows developers and users to reconstruct why a specific answer was generated.
    """

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    query: str = ""
    strategy: str = "default"
    retrieved_chunks: list[RetrievedChunkTrace] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    context_text: str = ""
    context_tokens: int = 0
    system_prompt: str | None = None
    formatted_prompt: str = ""
    model: str = ""
    response_content: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    retrieval_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    fallback_triggered: bool = False
    fallback_reason: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Return True if execution completed without error."""
        return self.error is None

    @property
    def chunks_count(self) -> int:
        """Return the number of retrieved chunks."""
        return len(self.retrieved_chunks)

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "strategy": self.strategy,
            "retrieved_chunks": [c.to_dict() for c in self.retrieved_chunks],
            "scores": [round(s, 4) for s in self.scores],
            "context_tokens": self.context_tokens,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "response_content": self.response_content,
            "tokens": {
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "total": self.total_tokens,
            },
            "latencies_ms": {
                "retrieval": round(self.retrieval_latency_ms, 2),
                "llm": round(self.llm_latency_ms, 2),
                "total": round(self.total_latency_ms, 2),
            },
            "fallback_triggered": self.fallback_triggered,
            "fallback_reason": self.fallback_reason,
            "error": self.error,
            "metadata": dict(self.metadata),
        }

    def to_markdown(self) -> str:
        """
        Generate a comprehensive diagnostic inspection markdown report.
        Answers: 'Why did the model generate this answer?'
        """
        status_badge = "FAILED" if self.error else ("FALLBACK" if self.fallback_triggered else "SUCCESS")
        lines = [
            f"# RAG Diagnostic Trace: `{self.trace_id}`",
            "",
            f"- **Status**: {status_badge}",
            f"- **Timestamp**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"- **Query**: {self.query}",
            f"- **Model**: {self.model or 'N/A'}",
            f"- **Strategy**: `{self.strategy}`",
            "",
            "## 1. Latency & Performance",
            "",
            "| Stage | Latency (ms) | Percentage |",
            "| :--- | :--- | :--- |",
        ]

        total = max(self.total_latency_ms, 0.001)
        r_pct = round((self.retrieval_latency_ms / total) * 100, 1)
        l_pct = round((self.llm_latency_ms / total) * 100, 1)

        lines.extend([
            f"| Retrieval | {self.retrieval_latency_ms:.2f} ms | {r_pct}% |",
            f"| LLM Generation | {self.llm_latency_ms:.2f} ms | {l_pct}% |",
            f"| **Total** | **{self.total_latency_ms:.2f} ms** | 100.0% |",
            "",
            f"- **Tokens**: {self.prompt_tokens} prompt + {self.completion_tokens} completion = {self.total_tokens} total",
            "",
            "## 2. Retrieved Knowledge & Scores",
            "",
        ])

        if not self.retrieved_chunks:
            lines.append("*No knowledge chunks retrieved.*")
            if self.fallback_triggered:
                lines.append(f"\n> [!NOTE]\n> Fallback triggered: `{self.fallback_reason}`")
        else:
            lines.append("| Rank | Document ID | Chunk ID | Score | Source | Snippet Preview |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for idx, c in enumerate(self.retrieved_chunks, 1):
                snippet = c.content_snippet.replace("\n", " ")[:60] + "..." if len(c.content_snippet) > 60 else c.content_snippet
                lines.append(
                    f"| {idx} | `{c.document_id}` | `{c.chunk_id}` | {c.score:.4f} | {c.source or 'N/A'} | {snippet} |"
                )

        lines.extend([
            "",
            "## 3. Assembled Context",
            "",
            "```text",
            self.context_text if self.context_text else "(empty context)",
            "```",
            "",
            "## 4. LLM Prompt Sent",
            "",
            "```text",
            self.formatted_prompt if self.formatted_prompt else f"System: {self.system_prompt}\nUser: {self.query}",
            "```",
            "",
            "## 5. Model Response",
            "",
            self.response_content if self.response_content else "*(no response)*",
        ])

        if self.error:
            lines.extend([
                "",
                "## Execution Error",
                "",
                f"```text\n{self.error}\n```",
            ])

        return "\n".join(lines)


__all__ = [
    "RetrievedChunkTrace",
    "RAGTrace",
]
