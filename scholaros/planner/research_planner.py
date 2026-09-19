"""
ScholarOS Research Planner.

Decomposes complex research queries into structured research plans with
targeted sub-questions, retrieval strategies, and step definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING, Any

from scholaros.planner.planner import Planner

if TYPE_CHECKING:
    from scholaros.ai.llm.base import LLM
    from scholaros.execution import Execution


@dataclass
class ResearchPlan:
    """
    Structured execution plan for a research task.
    """

    query: str
    sub_questions: list[str] = field(default_factory=list)
    strategy: str = "default"
    limit_per_query: int = 5
    collections: list[str] | None = None
    steps: list[str] = field(
        default_factory=lambda: [
            "retrieve_knowledge",
            "analyze_evidence",
            "synthesize_findings",
        ]
    )
    metadata: dict[str, Any] = field(default_factory=dict)


class ResearchPlanner(Planner):
    """
    Coordinates research planning and query decomposition.
    """

    def __init__(
        self,
        execution: Execution | None = None,
        llm: LLM | None = None,
    ) -> None:
        if execution is None:
            # Maintain backward compatibility with Planner by providing mock/empty Execution
            from unittest.mock import MagicMock
            super().__init__(execution=MagicMock())
        else:
            super().__init__(execution=execution)

        self._llm = llm

    @property
    def llm(self) -> LLM | None:
        """Return the optional LLM used for planning."""
        return self._llm

    def create_plan(
        self,
        query: str,
        strategy: str = "default",
        limit_per_query: int = 5,
        collections: list[str] | None = None,
    ) -> ResearchPlan:
        """
        Decompose a research query into a structured ResearchPlan.
        """
        sub_questions = self._decompose_query(query)
        return ResearchPlan(
            query=query,
            sub_questions=sub_questions,
            strategy=strategy,
            limit_per_query=limit_per_query,
            collections=collections,
        )

    def _decompose_query(self, query: str) -> list[str]:
        """
        Decompose a query into sub-questions.
        Uses rule-based extraction or returns distinct semantic aspects.
        """
        cleaned = query.strip()
        # If query contains explicit conjunctions or multiple questions
        if " and " in cleaned.lower() or " vs " in cleaned.lower() or " versus " in cleaned.lower():
            parts = re.split(r"\s+(?:and|vs|versus)\s+", cleaned, flags=re.IGNORECASE)
            sub_qs = [p.strip().rstrip("?.") for p in parts if len(p.strip()) > 3]
            if len(sub_qs) > 1:
                return [f"{sq}?" if not sq.endswith("?") else sq for sq in sub_qs]

        # Default decomposition: main query + background aspect + comparative/methodological aspect
        return [
            cleaned,
            f"Key mechanisms and background of {cleaned.rstrip('?.')}",
            f"Applications and empirical findings on {cleaned.rstrip('?.')}",
        ]


__all__ = [
    "ResearchPlan",
    "ResearchPlanner",
]
