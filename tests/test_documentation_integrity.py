"""
ScholarOS Documentation Integrity Test Suite.

Verifies:
- All required user, developer, and architecture documentation files exist and are populated
- All relative markdown links resolve to valid, existing local files (no 404 broken links)
- Architecture reference document covers all required subsystems
- Python code snippets within documentation parse as valid Python syntax
"""

from __future__ import annotations

import ast
from pathlib import Path
import re

import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def docs_dir(repo_root: Path) -> Path:
    return repo_root / "docs"


class TestDocumentationFiles:
    """Verify presence and non-emptiness of all documented topics."""

    REQUIRED_DOCS = [
        "README.md",
        "docs/index.md",
        # User documentation
        "docs/user/installation.md",
        "docs/user/first_launch.md",
        "docs/user/llm_configuration.md",
        "docs/user/ai_chat.md",
        "docs/user/research_workflow.md",
        "docs/user/knowledge_library.md",
        "docs/user/rag_configuration.md",
        "docs/user/plugins.md",
        "docs/user/troubleshooting.md",
        # Developer documentation
        "docs/developer/getting_started.md",
        "docs/developer/architecture.md",
        "docs/developer/module_structure.md",
        "docs/developer/extension_points.md",
        "docs/developer/plugin_development.md",
        "docs/developer/provider_development.md",
        "docs/developer/testing.md",
        "docs/developer/contributing.md",
        # Architecture documentation
        "docs/architecture/reference.md",
        "docs/architecture/diagrams.md",
    ]

    @pytest.mark.parametrize("rel_path", REQUIRED_DOCS)
    def test_doc_file_exists_and_populated(self, repo_root: Path, rel_path: str) -> None:
        target = repo_root / rel_path
        assert target.exists(), f"Missing required documentation file: {rel_path}"
        assert target.is_file()
        content = target.read_text(encoding="utf-8")
        assert len(content.strip()) > 150, f"Documentation file is suspiciously short: {rel_path}"


class TestLinkIntegrity:
    """Verify all internal relative links in markdown documentation point to real files."""

    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def test_all_relative_links_resolve(self, repo_root: Path) -> None:
        md_files = list(repo_root.glob("docs/**/*.md")) + [repo_root / "README.md"]
        broken_links = []

        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            for match in self.LINK_PATTERN.finditer(content):
                link_target = match.group(2).strip()

                # Skip external URLs, email, anchor-only, or badge shields
                if (
                    link_target.startswith("http://")
                    or link_target.startswith("https://")
                    or link_target.startswith("mailto:")
                    or link_target.startswith("#")
                ):
                    continue

                # Strip internal anchor if present (e.g. file.md#section)
                target_path_str = link_target.split("#")[0]
                if not target_path_str:
                    continue

                # Resolve target relative to current md file
                resolved = (md_file.parent / target_path_str).resolve()
                if not resolved.exists():
                    broken_links.append(f"{md_file.relative_to(repo_root)} -> {link_target}")

        assert not broken_links, f"Found broken relative documentation links: {broken_links}"


class TestArchitectureCoverage:
    """Verify that architecture documentation covers all mandatory subsystems."""

    MANDATORY_SUBSYSTEMS = [
        "Core",
        "AI",
        "Research",
        "Knowledge",
        "RAG",
        "Retrieval",
        "Embeddings",
        "Memory",
        "Tools",
        "Plugins",
        "GUI",
        "Services",
        "Events",
        "DI",
        "Configuration",
        "Security",
        "Observability",
    ]

    def test_all_subsystems_documented(self, repo_root: Path) -> None:
        arch_ref = repo_root / "docs" / "architecture" / "reference.md"
        assert arch_ref.exists()
        content = arch_ref.read_text(encoding="utf-8").lower()

        missing = []
        for sub in self.MANDATORY_SUBSYSTEMS:
            if sub.lower() not in content:
                missing.append(sub)

        assert not missing, f"Architecture reference is missing documentation for: {missing}"


class TestDocumentationCodeSnippets:
    """Verify Python code snippets in documentation are syntactically valid."""

    PYTHON_BLOCK_PATTERN = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL)

    def test_python_snippets_parse(self, repo_root: Path) -> None:
        md_files = list(repo_root.glob("docs/**/*.md"))
        syntax_errors = []

        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            for idx, block in enumerate(self.PYTHON_BLOCK_PATTERN.findall(content)):
                # If snippet has placeholders or ellipses, skip pure syntax check if not parseable
                code = block.strip()
                if not code:
                    continue
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    syntax_errors.append(f"{md_file.relative_to(repo_root)} (block {idx + 1}): {e}")

        assert not syntax_errors, f"Syntax errors in documentation code snippets: {syntax_errors}"
