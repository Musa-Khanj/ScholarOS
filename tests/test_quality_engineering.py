"""
ScholarOS Quality Engineering & Architecture Invariants Test Suite.

Verifies:
1. AST Architecture Invariants:
   - Core & Kernel primitives are strictly isolated from presentation, applications, and domain layers.
   - Domain subsystems (knowledge, retrieval, ai, research, events, etc.) never import from presentation (GUI).
2. Dynamic Import & Circular Dependency Verification:
   - All ScholarOS subsystems can be imported dynamically without circular dependency deadlocks or import failures.
3. Release Metadata & Dependency Conformance:
   - pyproject.toml specification conforms to release standards (Python >=3.12, Apache-2.0 license, valid dependencies, ruff lint config).
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import tomllib

import pytest

REPO_ROOT = Path(__file__).parent.parent
SCHOLAROS_PKG = REPO_ROOT / "scholaros"


def extract_imported_modules(file_path: Path) -> set[str]:
    """Parse a python file with AST and return set of all top-level imported module names."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except Exception:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


class TestArchitectureInvariants:
    """Architectural boundary and dependency rules enforcement."""

    def test_core_and_kernel_isolation(self) -> None:
        """
        Core and Kernel packages must NEVER import from presentation (GUI),
        applications, or high-level domain subsystems (research, retrieval, ai).
        """
        forbidden_prefixes = (
            "scholaros.gui",
            "scholaros.applications",
            "scholaros.research",
            "scholaros.retrieval",
            "scholaros.ai",
            "scholaros.workflow",
        )

        violations: list[str] = []
        target_dirs = [SCHOLAROS_PKG / "core", SCHOLAROS_PKG / "kernel"]

        for target_dir in target_dirs:
            if not target_dir.exists():
                continue
            for py_file in target_dir.rglob("*.py"):
                imported = extract_imported_modules(py_file)
                for mod in imported:
                    for forbidden in forbidden_prefixes:
                        if mod == forbidden or mod.startswith(f"{forbidden}."):
                            rel_path = py_file.relative_to(REPO_ROOT)
                            violations.append(f"{rel_path} illegally imports '{mod}'")

        assert not violations, "Architecture Boundary Violations:\n" + "\n".join(violations)

    def test_domain_subsystems_gui_isolation(self) -> None:
        """
        Domain subsystems (knowledge, retrieval, ai, research, events, etc.)
        must NEVER import from presentation (scholaros.gui).
        """
        forbidden_prefix = "scholaros.gui"
        domain_subdirs = [
            "knowledge",
            "retrieval",
            "ai",
            "research",
            "events",
            "logging",
            "observability",
            "plugins",
            "security",
            "config",
            "storage",
            "container",
        ]

        violations: list[str] = []
        for subdir in domain_subdirs:
            target_dir = SCHOLAROS_PKG / subdir
            if not target_dir.exists():
                continue
            for py_file in target_dir.rglob("*.py"):
                imported = extract_imported_modules(py_file)
                for mod in imported:
                    if mod == forbidden_prefix or mod.startswith(f"{forbidden_prefix}."):
                        rel_path = py_file.relative_to(REPO_ROOT)
                        violations.append(f"{rel_path} illegally imports presentation '{mod}'")

        assert not violations, "Domain -> Presentation Leakage Violations:\n" + "\n".join(violations)


class TestCircularDependencies:
    """Ensure modules and packages import cleanly without circular dependency deadlocks."""

    @pytest.mark.parametrize(
        "subpackage",
        [
            "scholaros.agents",
            "scholaros.ai",
            "scholaros.applications",
            "scholaros.bootstrap",
            "scholaros.cli",
            "scholaros.collaboration",
            "scholaros.config",
            "scholaros.container",
            "scholaros.contracts",
            "scholaros.core",
            "scholaros.dependency",
            "scholaros.embeddings",
            "scholaros.events",
            "scholaros.execution",
            "scholaros.extensions",
            "scholaros.gui",
            "scholaros.hooks",
            "scholaros.kernel",
            "scholaros.knowledge",
            "scholaros.lifecycle",
            "scholaros.logging",
            "scholaros.memory",
            "scholaros.observability",
            "scholaros.planner",
            "scholaros.plugins",
            "scholaros.registry",
            "scholaros.research",
            "scholaros.retrieval",
            "scholaros.runtime",
            "scholaros.scheduler",
            "scholaros.security",
            "scholaros.services",
            "scholaros.tools",
            "scholaros.ui",
            "scholaros.workflow",
        ],
    )
    def test_subpackage_dynamic_import(self, subpackage: str) -> None:
        """Verify that each subsystem can be imported dynamically without runtime failure."""
        module = importlib.import_module(subpackage)
        assert module is not None
        assert hasattr(module, "__file__")


class TestProjectConfigurationAndLicensing:
    """Verify package configuration, metadata, and dependencies."""

    def test_pyproject_conformance(self) -> None:
        """pyproject.toml must declare required metadata and dependencies."""
        pyproject_file = REPO_ROOT / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml must exist at repo root"

        with open(pyproject_file, "rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        assert project.get("name") == "scholaros"
        assert project.get("version") == "1.0.0"
        assert project.get("requires-python") == ">=3.12"
        assert project.get("license", {}).get("text") == "Apache-2.0"

        # Dependencies validation
        deps = project.get("dependencies", [])
        dep_names = [d.split(">=")[0].split("<")[0].strip() for d in deps]
        assert "langchain" in dep_names
        assert "langchain-core" in dep_names
        assert "langchain-ollama" in dep_names

        # Dev dependencies
        optional_deps = project.get("optional-dependencies", {})
        dev_deps = optional_deps.get("dev", [])
        dev_names = [d.split(">=")[0].strip() for d in dev_deps]
        assert "pytest" in dev_names
        assert "ruff" in dev_names
        assert "mypy" in dev_names

        # Tool Ruff configuration
        tool = data.get("tool", {})
        ruff = tool.get("ruff", {})
        assert ruff.get("line-length") == 100
        assert ruff.get("target-version") == "py312"
        lint = ruff.get("lint", {})
        assert "E" in lint.get("select", [])
        assert "F" in lint.get("select", [])
        assert "W" in lint.get("select", [])
