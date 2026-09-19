"""
Unit and Integration Tests for Milestone 10V: V1.0 Release & Publication.

Verifies:
  1. Public API surface freeze and export immutability.
  2. Legal licensing (Apache 2.0) and copyright notices.
  3. Security policy, reporting channels, and response SLAs.
  4. Contributor guidelines, code standards, and PR templates.
  5. GitHub Issue Forms and template schema validity.
  6. Release notes completeness and cross-project version parity.
  7. Production frozen lockfile validity.
  8. Distribution package archives and SHA256 integrity manifest.
"""

from __future__ import annotations

from pathlib import Path
import re
import tomllib
import yaml

import pytest

import scholaros


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPublicApiFreeze:
    """Validates that the public API of ScholarOS is explicitly defined and frozen."""

    def test_version_string(self) -> None:
        assert hasattr(scholaros, "__version__")
        assert scholaros.__version__ == "1.0.0"

    def test_explicit_all_exports(self) -> None:
        assert hasattr(scholaros, "__all__")
        expected_exports = {
            "AIFactory",
            "Container",
            "EventBus",
            "GUIApplication",
            "HybridRetriever",
            "Kernel",
            "KnowledgeManager",
            "Plugin",
            "RAGPipeline",
            "ResearchAgent",
            "__version__",
        }
        assert set(scholaros.__all__) == expected_exports

    def test_exported_symbols_are_importable_and_valid(self) -> None:
        for symbol_name in scholaros.__all__:
            symbol = getattr(scholaros, symbol_name, None)
            assert symbol is not None, f"Exported symbol '{symbol_name}' is None or missing"


class TestLegalAndGovernance:
    """Validates open source licensing, security, and contribution governance files."""

    def test_license_file_validity(self) -> None:
        license_path = REPO_ROOT / "LICENSE"
        assert license_path.exists(), "LICENSE file must exist in repository root"
        content = license_path.read_text(encoding="utf-8")
        assert "Apache License" in content
        assert "Version 2.0" in content
        assert "Copyright 2026 Musa Khan and the ScholarOS Contributors" in content

    def test_security_policy_structure(self) -> None:
        security_path = REPO_ROOT / "SECURITY.md"
        assert security_path.exists(), "SECURITY.md must exist in repository root"
        content = security_path.read_text(encoding="utf-8")
        assert "1.0.x" in content
        assert "Reporting a Vulnerability" in content
        assert "48 hours" in content
        assert "Prompt Injection" in content

    def test_contributing_guidelines(self) -> None:
        contrib_path = REPO_ROOT / "CONTRIBUTING.md"
        assert contrib_path.exists(), "CONTRIBUTING.md must exist in repository root"
        content = contrib_path.read_text(encoding="utf-8")
        assert "Code of Conduct" in content
        assert "ruff check" in content
        assert "mypy" in content
        assert "pytest" in content
        assert "Conventional Commits" in content


class TestGitHubCommunityTemplates:
    """Validates GitHub issue forms, configuration, and PR templates."""

    def test_config_yml(self) -> None:
        config_path = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
        assert config_path.exists()
        parsed = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert parsed.get("blank_issues_enabled") is False
        assert len(parsed.get("contact_links", [])) >= 2

    @pytest.mark.parametrize(
        "template_name",
        ["bug_report.yml", "feature_request.yml", "research_workflow.yml"],
    )
    def test_issue_form_yaml_validity(self, template_name: str) -> None:
        template_path = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / template_name
        assert template_path.exists(), f"Missing template {template_name}"
        data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        assert "name" in data
        assert "description" in data
        assert "body" in data
        assert isinstance(data["body"], list)
        assert len(data["body"]) >= 3

    def test_pull_request_template(self) -> None:
        pr_template_path = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
        assert pr_template_path.exists()
        content = pr_template_path.read_text(encoding="utf-8")
        assert "Verification Checklist" in content
        assert "ruff check" in content
        assert "mypy" in content
        assert "pytest" in content


class TestReleaseDocumentationAndLockfile:
    """Validates release notes, lockfiles, and version consistency."""

    def test_release_notes(self) -> None:
        notes_path = REPO_ROOT / "RELEASE_NOTES.md"
        assert notes_path.exists()
        content = notes_path.read_text(encoding="utf-8")
        assert "ScholarOS V1.0.0 Release Notes" in content
        assert "Architecture & API Freeze" in content
        assert "Verification & Quality Benchmarks" in content
        assert "1,377 passed" in content

    def test_requirements_frozen(self) -> None:
        frozen_path = REPO_ROOT / "requirements-frozen.txt"
        assert frozen_path.exists()
        lines = [line.strip() for line in frozen_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
        assert len(lines) >= 30
        assert any("langchain==" in line for line in lines)
        assert any("pydantic==" in line for line in lines)

    def test_version_parity_across_repository(self) -> None:
        pyproject_path = REPO_ROOT / "pyproject.toml"
        pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        pyproject_version = pyproject_data["project"]["version"]

        code_version = scholaros.__version__

        changelog_path = REPO_ROOT / "CHANGELOG.md"
        changelog_content = changelog_path.read_text(encoding="utf-8")
        changelog_match = re.search(r"## \[(\d+\.\d+\.\d+)\]", changelog_content)
        assert changelog_match is not None
        changelog_version = changelog_match.group(1)

        assert pyproject_version == code_version == changelog_version == "1.0.0"

    def test_distribution_manifest_and_packages(self) -> None:
        dist_dir = REPO_ROOT / "dist"
        assert dist_dir.exists()
        checksum_file = dist_dir / "SHA256SUMS.txt"
        assert checksum_file.exists()
        checksum_content = checksum_file.read_text(encoding="utf-8")
        assert "scholaros-1.0.0-py3-none-any.whl" in checksum_content
        assert "scholaros-1.0.0.tar.gz" in checksum_content
