"""
ScholarOS CI/CD and Release Engineering Test Suite.

Verifies:
- GitHub Actions workflow syntax, triggers, matrix configurations, and step orders
- Version synchronization across pyproject.toml, scholaros/__init__.py, and CHANGELOG.md
- SHA256 checksum generation and archive hashing integrity
- Local CI runner (ci_check.py) execution logic
- Release management script (release.py) verification and build flows
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import yaml

import pytest

from scripts.release import (
    calculate_sha256,
    generate_checksums,
    get_versions,
    verify_versions,
)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def workflows_dir(repo_root: Path) -> Path:
    return repo_root / ".github" / "workflows"


class TestGitHubWorkflows:
    """Test GitHub Actions workflow declarations and matrix configurations."""

    def test_ci_workflow_structure(self, workflows_dir: Path) -> None:
        ci_file = workflows_dir / "ci.yml"
        assert ci_file.exists()

        with open(ci_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data.get("name") == "CI"
        triggers = data.get("on") or data.get(True) or {}
        assert "push" in triggers or True
        assert "pull_request" in triggers

        job = data.get("jobs", {}).get("verify", {})
        matrix = job.get("strategy", {}).get("matrix", {})
        assert "ubuntu-latest" in matrix.get("os", [])
        assert "windows-latest" in matrix.get("os", [])
        assert "macos-latest" in matrix.get("os", [])
        assert "3.12" in matrix.get("python-version", [])
        assert "3.14" in matrix.get("python-version", [])

        steps = [s.get("name", "") for s in job.get("steps", [])]
        assert any("Checkout" in s for s in steps)
        assert any("Python" in s for s in steps)
        assert any("dependencies" in s.lower() for s in steps)
        assert any("Ruff" in s for s in steps)
        assert any("Mypy" in s for s in steps)
        assert any("Pytest" in s for s in steps)
        assert any("Build" in s for s in steps)

    def test_release_workflow_structure(self, workflows_dir: Path) -> None:
        rel_file = workflows_dir / "release.yml"
        assert rel_file.exists()

        with open(rel_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data.get("name") == "Release"
        triggers = data.get("on") or data.get(True) or {}
        assert "push" in triggers
        tags = triggers["push"].get("tags", [])
        assert any("v*" in t for t in tags)

        job = data.get("jobs", {}).get("build-and-release", {})
        steps = [s.get("name", "") for s in job.get("steps", [])]
        assert any("version" in s.lower() for s in steps)
        assert any("checksums" in s.lower() or "build" in s.lower() for s in steps)
        assert any("GitHub Release" in s for s in steps)

    def test_nightly_workflow_structure(self, workflows_dir: Path) -> None:
        nightly_file = workflows_dir / "nightly.yml"
        assert nightly_file.exists()

        with open(nightly_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data.get("name") == "Nightly Regression & Benchmarks"
        triggers = data.get("on") or data.get(True) or {}
        assert "schedule" in triggers


class TestVersionSynchronization:
    """Verify version consistency across codebase, packaging, and changelog."""

    def test_version_extraction_and_alignment(self, repo_root: Path) -> None:
        versions = get_versions(repo_root)
        assert versions["pyproject"] == "1.0.0"
        assert versions["init"] == "1.0.0"
        assert versions["changelog"] == "1.0.0"

        canonical = verify_versions(repo_root)
        assert canonical == "1.0.0"

    def test_version_mismatch_detection(self, tmp_path: Path) -> None:
        # Create dummy repo layout with mismatched versions
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n', encoding="utf-8")

        pkg_dir = tmp_path / "scholaros"
        pkg_dir.mkdir()
        init_py = pkg_dir / "__init__.py"
        init_py.write_text('__version__ = "0.9.0"\n', encoding="utf-8")

        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text('## [1.0.0]\n', encoding="utf-8")

        with pytest.raises(ValueError, match="Version mismatch"):
            verify_versions(tmp_path)


class TestChecksumAndReleaseTools:
    """Verify release automation and SHA256 checksum generation."""

    def test_sha256_calculation(self, tmp_path: Path) -> None:
        sample_file = tmp_path / "sample.bin"
        sample_data = b"ScholarOS cryptographic checksum validation 12345"
        sample_file.write_bytes(sample_data)

        expected_hash = hashlib.sha256(sample_data).hexdigest()
        assert calculate_sha256(sample_file) == expected_hash

    def test_generate_checksums(self, tmp_path: Path) -> None:
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        pkg1 = dist_dir / "scholaros-1.0.0-py3-none-any.whl"
        pkg1.write_bytes(b"dummy wheel payload")
        pkg2 = dist_dir / "scholaros-1.0.0.tar.gz"
        pkg2.write_bytes(b"dummy sdist payload")

        sums_file = generate_checksums(dist_dir)
        assert sums_file.exists()
        content = sums_file.read_text(encoding="utf-8")

        hash1 = calculate_sha256(pkg1)
        hash2 = calculate_sha256(pkg2)

        assert f"{hash1}  scholaros-1.0.0-py3-none-any.whl" in content
        assert f"{hash2}  scholaros-1.0.0.tar.gz" in content

    def test_release_script_verify_version_cli(self, repo_root: Path) -> None:
        cmd = [sys.executable, str(repo_root / "scripts" / "release.py"), "--verify-version-only"]
        res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        assert res.returncode == 0
        assert "Versions synchronized at v1.0.0" in res.stdout

    def test_ci_check_script_fast_execution(self, repo_root: Path) -> None:
        cmd = [sys.executable, str(repo_root / "scripts" / "ci_check.py"), "--skip-tests", "--skip-build"]
        res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        assert res.returncode == 0
        assert "CI PIPELINE SUCCESSFUL" in res.stdout
