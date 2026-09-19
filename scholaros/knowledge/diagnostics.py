"""
ScholarOS Knowledge Diagnostics.

Performs integrity checks detecting orphan chunks, duplicate identifiers,
missing sources, and invalid metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.knowledge.storage import KnowledgeStorage


@dataclass(slots=True, frozen=True)
class DiagnosticIssue:
    """A detected inconsistency or validation error."""

    issue_type: str
    description: str
    target_id: str | None = None


@dataclass(slots=True)
class DiagnosticReport:
    """Integrity check results across knowledge storage."""

    orphan_chunks: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)
    invalid_metadata: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)
    issues: list[DiagnosticIssue] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Return True if no integrity issues were detected."""
        return not bool(
            self.orphan_chunks
            or self.duplicate_ids
            or self.invalid_metadata
            or self.missing_sources
            or self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "is_healthy": self.is_healthy,
            "orphan_chunks_count": len(self.orphan_chunks),
            "duplicate_ids_count": len(self.duplicate_ids),
            "invalid_metadata_count": len(self.invalid_metadata),
            "missing_sources_count": len(self.missing_sources),
            "orphan_chunks": self.orphan_chunks,
            "duplicate_ids": self.duplicate_ids,
            "invalid_metadata": self.invalid_metadata,
            "missing_sources": self.missing_sources,
            "issues": [
                {"type": i.issue_type, "target": i.target_id, "description": i.description}
                for i in self.issues
            ],
        }


class KnowledgeDiagnostics:
    """
    Performs integrity audits across knowledge collections, documents, and chunks.
    """

    def run(
        self,
        target: Any = None,
        storage: Any = None,
    ) -> DiagnosticReport:
        """Run diagnostics on a collection or storage."""
        from scholaros.knowledge.collection import KnowledgeCollection
        from scholaros.knowledge.storage import InMemoryStorage

        actual = target if target is not None else storage
        if isinstance(actual, KnowledgeCollection):
            temp_storage = InMemoryStorage()
            temp_storage.clear()
            temp_storage.save_collection(actual)
            return self.run_checks(temp_storage)
        elif actual is not None:
            return self.run_checks(actual)
        return DiagnosticReport()

    def run_checks(self, storage: KnowledgeStorage) -> DiagnosticReport:
        """
        Execute comprehensive integrity audit.
        """
        report = DiagnosticReport()
        seen_doc_ids: set[str] = set()
        seen_chunk_ids: set[str] = set()
        valid_doc_ids: set[str] = set()

        for coll_name in storage.list_collections():
            docs = storage.list_documents(coll_name)
            for doc in docs:
                # 1. Check duplicate IDs
                if doc.identifier in seen_doc_ids:
                    report.duplicate_ids.append(doc.identifier)
                    report.issues.append(
                        DiagnosticIssue(
                            issue_type="duplicate_document_id",
                            description=f"Duplicate document ID '{doc.identifier}' in collection '{coll_name}'.",
                            target_id=doc.identifier,
                        )
                    )
                else:
                    seen_doc_ids.add(doc.identifier)
                    valid_doc_ids.add(doc.identifier)

                # 2. Check metadata
                if not doc.title or not doc.title.strip():
                    report.invalid_metadata.append(doc.identifier)
                    report.issues.append(
                        DiagnosticIssue(
                            issue_type="invalid_metadata",
                            description=f"Document '{doc.identifier}' has missing or empty title.",
                            target_id=doc.identifier,
                        )
                    )

                # 3. Check sources
                if doc.source is None:
                    report.missing_sources.append(doc.identifier)
                    report.issues.append(
                        DiagnosticIssue(
                            issue_type="missing_source",
                            description=f"Document '{doc.identifier}' has no associated source provenance.",
                            target_id=doc.identifier,
                        )
                    )

                # Collect chunks for this document
                chunks = doc.chunks or storage.get_chunks_for_document(doc.identifier)
                for chunk in chunks:
                    if chunk.identifier in seen_chunk_ids:
                        report.duplicate_ids.append(chunk.identifier)
                        report.issues.append(
                            DiagnosticIssue(
                                issue_type="duplicate_chunk_id",
                                description=f"Duplicate chunk ID '{chunk.identifier}'.",
                                target_id=chunk.identifier,
                            )
                        )
                    else:
                        seen_chunk_ids.add(chunk.identifier)

                    # Check orphan
                    if chunk.document_id not in valid_doc_ids and chunk.document_id != doc.identifier:
                        report.orphan_chunks.append(chunk.identifier)
                        report.issues.append(
                            DiagnosticIssue(
                                issue_type="orphan_chunk",
                                description=f"Chunk '{chunk.identifier}' references missing doc '{chunk.document_id}'.",
                                target_id=chunk.identifier,
                            )
                        )

        return report


__all__ = [
    "DiagnosticIssue",
    "DiagnosticReport",
    "KnowledgeDiagnostics",
]
