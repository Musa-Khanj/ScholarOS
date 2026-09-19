"""
ScholarOS
Research Session

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a single
research session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from scholaros.memory.memory import Memory
from scholaros.research.result import ResearchResult

if TYPE_CHECKING:
    from scholaros.knowledge.document import KnowledgeDocument


@dataclass(
    slots=True,
)
class ResearchSession:
    """
    Represents an ongoing research session with working memory,
    conversation context, and interaction history.
    """

    query: str = ""

    context: list[str] = field(
        default_factory=list,
    )

    notes: list[str] = field(
        default_factory=list,
    )

    result: ResearchResult | None = None

    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    title: str = ""

    memory: Memory = field(
        default_factory=Memory,
    )

    history: list[dict[str, Any]] = field(
        default_factory=list,
    )

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def add_note(self, note: str) -> None:
        """Add a researcher note to the session and working memory."""
        self.notes.append(note)
        self.memory.set(f"note_{len(self.notes)}", note)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_context(self, item: str) -> None:
        """Add background context or premise to the session."""
        self.context.append(item)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def record_interaction(
        self,
        query: str,
        result: ResearchResult,
        notes: list[str] | None = None,
    ) -> None:
        """
        Record a completed research turn into session history.
        """
        self.query = query
        self.result = result
        if notes:
            self.notes.extend(notes)

        turn_record: dict[str, Any] = {
            "query": query,
            "content": result.content,
            "model": result.model,
            "sources": list(result.sources),
            "timestamp": time.time(),
        }
        if result.report is not None:
            turn_record["report_id"] = result.report.id
            turn_record["citations"] = [
                {"title": c.title, "source": c.source} for c in result.report.citations
            ]
        if result.workflow_context is not None:
            turn_record["workflow_id"] = result.workflow_context.workflow_id
            turn_record["steps"] = [s.name for s in result.workflow_context.steps]

        self.history.append(turn_record)
        self.memory.set(f"turn_{len(self.history)}", turn_record)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def get_conversation_context(self, limit: int = 3) -> str:
        """
        Return recent notes, context, and interactions formatted for grounding prompts.
        """
        parts: list[str] = []
        if self.context:
            parts.append("Background Context:\n" + "\n".join(f"- {c}" for c in self.context))

        if self.notes:
            parts.append("Session Notes:\n" + "\n".join(f"- {n}" for n in self.notes[-5:]))

        if self.history:
            recent_turns = self.history[-limit:]
            history_lines: list[str] = []
            for i, turn in enumerate(recent_turns, 1):
                q = turn.get("query", "")
                ans = turn.get("content", "")
                snippet = ans[:300] + ("..." if len(ans) > 300 else "")
                history_lines.append(f"Turn {i}:\nUser: {q}\nFindings: {snippet}")
            parts.append("Prior Research in this Session:\n" + "\n\n".join(history_lines))

        return "\n\n".join(parts)

    def to_knowledge_document(
        self,
        collection_name: str = "research_notes",
        title: str | None = None,
    ) -> KnowledgeDocument:
        """
        Export session findings, notes, and report as a KnowledgeDocument
        suitable for ingestion into the Knowledge Library.
        """
        from scholaros.knowledge.document import KnowledgeDocument
        from scholaros.knowledge.metadata import KnowledgeMetadata

        doc_title = title or self.title or f"Research Session: {self.query or self.id}"
        sections: list[str] = [f"# {doc_title}\n"]

        if self.notes:
            sections.append("## Session Notes\n" + "\n".join(f"- {n}" for n in self.notes))

        if self.result and self.result.has_content():
            sections.append(f"## Current Findings\n{self.result.content}")

        if self.history:
            sections.append("## Research Turns")
            for idx, turn in enumerate(self.history, 1):
                q = turn.get("query", "")
                c = turn.get("content", "")
                sections.append(f"### Turn {idx}: {q}\n{c}")

        content_body = "\n\n".join(sections)
        meta = KnowledgeMetadata(
            title=doc_title,
            author="ScholarOS Research Session",
            tags=["session_report", collection_name],
            extra={
                "session_id": self.id,
                "query": self.query,
                "turn_count": len(self.history),
                "notes_count": len(self.notes),
            },
        )
        return KnowledgeDocument(
            identifier=f"session-{self.id}",
            title=doc_title,
            content=content_body,
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "query": self.query,
            "context": list(self.context),
            "notes": list(self.notes),
            "history": list(self.history),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"id='{self.id}', "
            f"query={self.query!r}"
            f")"
        )


