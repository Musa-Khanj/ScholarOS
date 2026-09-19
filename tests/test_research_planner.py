"""
Tests for ScholarOS Research Planner.
"""

from __future__ import annotations


from scholaros.planner.research_planner import ResearchPlan, ResearchPlanner


class TestResearchPlan:
    """Tests for ResearchPlan dataclass."""

    def test_plan_defaults(self) -> None:
        plan = ResearchPlan(query="Attention mechanisms in NLP")
        assert plan.query == "Attention mechanisms in NLP"
        assert plan.sub_questions == []
        assert plan.strategy == "default"
        assert plan.limit_per_query == 5
        assert plan.collections is None
        assert len(plan.steps) == 3
        assert "retrieve_knowledge" in plan.steps
        assert "analyze_evidence" in plan.steps
        assert "synthesize_findings" in plan.steps

    def test_plan_custom_values(self) -> None:
        plan = ResearchPlan(
            query="Quantum Computing",
            sub_questions=["What is superposition?", "What is entanglement?"],
            strategy="hybrid",
            limit_per_query=8,
            collections=["quantum_physics"],
            steps=["stage1", "stage2"],
            metadata={"priority": "high"},
        )
        assert plan.strategy == "hybrid"
        assert plan.limit_per_query == 8
        assert plan.collections == ["quantum_physics"]
        assert len(plan.sub_questions) == 2
        assert plan.metadata["priority"] == "high"


class TestResearchPlanner:
    """Tests for ResearchPlanner."""

    def test_planner_initialization_defaults(self) -> None:
        planner = ResearchPlanner()
        assert planner is not None
        assert planner.llm is None

    def test_create_plan_simple_query(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan(
            query="Graph Neural Networks",
            strategy="semantic",
            limit_per_query=4,
            collections=["papers"],
        )
        assert plan.query == "Graph Neural Networks"
        assert plan.strategy == "semantic"
        assert plan.limit_per_query == 4
        assert plan.collections == ["papers"]
        assert len(plan.sub_questions) >= 3
        assert "Graph Neural Networks" in plan.sub_questions[0]
        assert any("mechanisms" in sq.lower() or "background" in sq.lower() for sq in plan.sub_questions)
        assert any("applications" in sq.lower() or "empirical" in sq.lower() for sq in plan.sub_questions)

    def test_create_plan_compound_query_and(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan(query="Transformers and Recurrent Neural Networks")
        assert len(plan.sub_questions) >= 2
        assert any("Transformers" in sq for sq in plan.sub_questions)
        assert any("Recurrent Neural Networks" in sq for sq in plan.sub_questions)

    def test_create_plan_compound_query_vs(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan(query="CNN vs Vision Transformers")
        assert len(plan.sub_questions) >= 2
        assert any("CNN" in sq for sq in plan.sub_questions)
        assert any("Vision Transformers" in sq for sq in plan.sub_questions)
