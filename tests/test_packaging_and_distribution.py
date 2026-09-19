"""
ScholarOS Packaging and Distribution Test Suite.

Verifies:
- pyproject.toml packaging metadata, classifiers, project URLs, and scripts
- Platform directory resolution across Windows, POSIX, and macOS conventions
- Environment variable overrides for sandboxing and multi-tenancy
- User environment initialization (config, data, cache, logs directories)
- CLI commands: info, status, config, init, run, gui
- Windows distribution packaging specifications and batch launcher
- Generated distribution archive integrity (wheel and sdist)
"""

from __future__ import annotations

import io
from pathlib import Path
import sys
import tomllib
from unittest.mock import patch

import pytest

from scholaros.cli.main import main as cli_main
from scholaros.platform.paths import (
    DEFAULT_STARTER_CONFIG,
    ensure_app_directories,
    get_app_dir,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_default_config_path,
    get_log_dir,
    initialize_user_environment,
    is_macos,
    is_windows,
)
from scripts.build_package import verify_sdist, verify_wheel


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def pyproject_data(repo_root: Path) -> dict:
    pyproject_file = repo_root / "pyproject.toml"
    assert pyproject_file.exists()
    with open(pyproject_file, "rb") as f:
        return tomllib.load(f)


class TestPackageMetadata:
    """Test pyproject.toml metadata and packaging standards."""

    def test_project_core_fields(self, pyproject_data: dict) -> None:
        project = pyproject_data.get("project", {})
        assert project.get("name") == "scholaros"
        assert project.get("version") == "1.0.0"
        assert "A modular multi-agent AI research operating system" in project.get("description", "")
        assert project.get("requires-python") in [">=3.12", ">=3.14"]
        assert project.get("license", {}).get("text") == "Apache-2.0"

    def test_project_classifiers(self, pyproject_data: dict) -> None:
        classifiers = pyproject_data.get("project", {}).get("classifiers", [])
        assert "Operating System :: Microsoft :: Windows" in classifiers
        assert "Operating System :: POSIX :: Linux" in classifiers
        assert "Operating System :: MacOS" in classifiers
        assert "Programming Language :: Python :: 3.14" in classifiers
        assert "Topic :: Scientific/Engineering :: Artificial Intelligence" in classifiers

    def test_project_urls(self, pyproject_data: dict) -> None:
        urls = pyproject_data.get("project", {}).get("urls", {})
        assert "Homepage" in urls
        assert "Documentation" in urls
        assert "Repository" in urls
        assert "Issues" in urls
        assert "Changelog" in urls

    def test_entrypoints_scripts(self, pyproject_data: dict) -> None:
        scripts = pyproject_data.get("project", {}).get("scripts", {})
        assert scripts.get("scholaros") == "scholaros.cli.main:main"
        assert scripts.get("scholaros-gui") == "scholaros.gui.launcher:main"

        gui_scripts = pyproject_data.get("project", {}).get("gui-scripts", {})
        assert gui_scripts.get("scholaros-desktop") == "scholaros.gui.launcher:main"

    def test_optional_dependencies(self, pyproject_data: dict) -> None:
        opt = pyproject_data.get("project", {}).get("optional-dependencies", {})
        assert "dev" in opt
        assert "gui" in opt
        assert "build" in opt
        assert "all" in opt
        assert any(d.startswith("pytest") for d in opt["dev"])
        assert any(b.startswith("build") for b in opt["build"])


class TestPlatformPaths:
    """Test OS-specific directory resolution and environment overrides."""

    def test_platform_identification(self) -> None:
        win = is_windows()
        mac = is_macos()
        if sys.platform == "win32":
            assert win is True
            assert mac is False
        elif sys.platform == "darwin":
            assert win is False
            assert mac is True
        else:
            assert win is False
            assert mac is False

    def test_environment_variable_overrides(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        custom_home = tmp_path / "custom_home"
        custom_config = tmp_path / "custom_config"
        custom_data = tmp_path / "custom_data"
        custom_cache = tmp_path / "custom_cache"
        custom_logs = tmp_path / "custom_logs"

        monkeypatch.setenv("SCHOLAROS_HOME", str(custom_home))
        monkeypatch.setenv("SCHOLAROS_CONFIG_DIR", str(custom_config))
        monkeypatch.setenv("SCHOLAROS_DATA_DIR", str(custom_data))
        monkeypatch.setenv("SCHOLAROS_CACHE_DIR", str(custom_cache))
        monkeypatch.setenv("SCHOLAROS_LOG_DIR", str(custom_logs))

        assert get_app_dir() == custom_home
        assert get_config_dir() == custom_config
        assert get_data_dir() == custom_data
        assert get_cache_dir() == custom_cache
        assert get_log_dir() == custom_logs
        assert get_default_config_path() == custom_config / "config.toml"

    def test_directory_creation_and_initialization(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        sandbox = tmp_path / "sandbox"
        monkeypatch.setenv("SCHOLAROS_HOME", str(sandbox))
        monkeypatch.delenv("SCHOLAROS_CONFIG_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_DATA_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_CACHE_DIR", raising=False)
        monkeypatch.delenv("SCHOLAROS_LOG_DIR", raising=False)

        dirs = ensure_app_directories()
        for d in dirs.values():
            assert d.exists()
            assert d.is_dir()

        init_res = initialize_user_environment()
        config_file = init_res["config_file"]
        assert config_file.exists()
        assert config_file.read_text(encoding="utf-8") == DEFAULT_STARTER_CONFIG

        # Modify config, verify force=False does not overwrite
        config_file.write_text("custom_content = true\n", encoding="utf-8")
        initialize_user_environment(force=False)
        assert config_file.read_text(encoding="utf-8") == "custom_content = true\n"

        # force=True should restore starter config
        initialize_user_environment(force=True)
        assert config_file.read_text(encoding="utf-8") == DEFAULT_STARTER_CONFIG


class TestCLIIntegration:
    """Test CLI commands and subcommands."""

    def test_cli_info_command(self) -> None:
        stream = io.StringIO()
        exit_code = cli_main(["info"], output=stream)
        assert exit_code == 0
        output = stream.getvalue()
        assert "ScholarOS" in output
        assert "Version:" in output
        assert "Description:" in output

    def test_cli_status_command(self) -> None:
        stream = io.StringIO()
        exit_code = cli_main(["status"], output=stream)
        assert exit_code == 0
        output = stream.getvalue()
        assert "ScholarOS status: READY" in output

    def test_cli_config_command(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SCHOLAROS_HOME", str(tmp_path / "cli_test_home"))
        stream = io.StringIO()
        exit_code = cli_main(["config"], output=stream)
        assert exit_code == 0
        output = stream.getvalue()
        assert "ScholarOS Platform & Configuration Paths" in output
        assert "Application Dir" in output
        assert "Configuration Dir" in output
        assert "Data Dir" in output

    def test_cli_init_command(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        sandbox = tmp_path / "cli_init_sandbox"
        monkeypatch.setenv("SCHOLAROS_HOME", str(sandbox))
        stream = io.StringIO()
        exit_code = cli_main(["init"], output=stream)
        assert exit_code == 0
        output = stream.getvalue()
        assert "Initializing ScholarOS user environment" in output
        assert "ScholarOS environment successfully initialized" in output
        assert (sandbox / "config" / "config.toml").exists()

    def test_cli_run_command_mock_provider(self) -> None:
        stream = io.StringIO()
        exit_code = cli_main(
            ["run", "What is transformer architecture?", "--provider", "mock", "--model", "mock-v1"],
            output=stream,
        )
        assert exit_code == 0
        output = stream.getvalue()
        assert "Executing ScholarOS research query" in output
        assert "Provider: mock" in output
        assert "Response:" in output

    def test_cli_gui_command(self) -> None:
        stream = io.StringIO()
        with patch("scholaros.gui.launcher.launch_gui") as mock_launch:
            exit_code = cli_main(["gui"], output=stream)
            assert exit_code == 0
            mock_launch.assert_called_once()
            assert "Starting ScholarOS Desktop GUI" in stream.getvalue()


class TestWindowsDistributionAssets:
    """Verify Windows packaging specs and launch scripts."""

    def test_pyinstaller_spec_asset(self, repo_root: Path) -> None:
        spec_path = repo_root / "packaging" / "windows" / "scholaros.spec"
        assert spec_path.exists()
        content = spec_path.read_text(encoding="utf-8")
        assert "Analysis(" in content
        assert "hiddenimports=" in content
        assert "scholaros.gui.launcher" in content
        assert "EXE(" in content
        assert "COLLECT(" in content

    def test_windows_batch_launcher(self, repo_root: Path) -> None:
        bat_path = repo_root / "packaging" / "windows" / "run_scholaros.bat"
        assert bat_path.exists()
        content = bat_path.read_text(encoding="utf-8")
        assert "ScholarOS Windows Desktop Launcher" in content
        assert "pythonw.exe" in content
        assert "scholaros.gui.launcher" in content


class TestBuiltPackageArchives:
    """Verify generated distribution packages if present."""

    def test_wheel_and_sdist_contents(self, repo_root: Path) -> None:
        dist_dir = repo_root / "dist"
        wheels = list(dist_dir.glob("*.whl"))
        sdists = list(dist_dir.glob("*.tar.gz"))

        if not wheels or not sdists:
            pytest.skip("Packages not yet built in dist/; run scripts/build_package.py first.")

        for wheel in wheels:
            info = verify_wheel(wheel)
            assert len(info["files"]) > 50
            entry_points_str = "\n".join(info["entry_points"])
            assert "scholaros = scholaros.cli.main:main" in entry_points_str
            assert "scholaros-gui = scholaros.gui.launcher:main" in entry_points_str
            assert "scholaros-desktop = scholaros.gui.launcher:main" in entry_points_str

        for sdist in sdists:
            files = verify_sdist(sdist)
            assert len(files) > 50
            assert any("pyproject.toml" in f for f in files)
            assert any("scholaros/__init__.py" in f for f in files)
