"""
ScholarOS
CLI Commands

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Implements command-line presentation
operations without modifying the
ScholarOS core architecture.
"""

from __future__ import annotations

import sys
from typing import TextIO

import scholaros
from scholaros.platform import (
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


def run_info(
    output: TextIO,
) -> int:
    """
    Display basic ScholarOS package
    information.
    """

    print(
        "ScholarOS",
        file=output,
    )
    print(
        f"Version: {scholaros.__version__}",
        file=output,
    )
    print(
        "Description: "
        "A modular multi-agent AI "
        "research operating system.",
        file=output,
    )

    return 0


def run_status(
    output: TextIO,
) -> int:
    """
    Display basic ScholarOS status.

    This command intentionally performs
    only a package-level health check.
    It does not start the kernel,
    runtime, LLM providers, or external
    services.
    """

    try:
        version = scholaros.__version__

    except AttributeError:
        print(
            "ScholarOS status: ERROR",
            file=output,
        )
        return 1

    print(
        "ScholarOS status: READY",
        file=output,
    )
    print(
        f"Version: {version}",
        file=output,
    )

    return 0


def run_init(
    output: TextIO,
    force: bool = False,
) -> int:
    """
    Initialize user configuration and application data directories.

    Parameters
    ----------
    output:
        Target output stream.
    force:
        Whether to overwrite existing configuration files.
    """
    print("Initializing ScholarOS user environment...", file=output)
    try:
        dirs = initialize_user_environment(force=force)
        config_file = dirs["config_file"]
        print(f"Application root : {dirs['app']}", file=output)
        print(f"Configuration dir: {dirs['config']}", file=output)
        print(f"Data storage dir : {dirs['data']}", file=output)
        print(f"Cache dir        : {dirs['cache']}", file=output)
        print(f"Log dir          : {dirs['logs']}", file=output)
        print(f"Config file      : {config_file} (created/verified)", file=output)
        print("ScholarOS environment successfully initialized.", file=output)
        return 0
    except Exception as exc:
        print(f"Error initializing ScholarOS environment: {exc}", file=output)
        return 1


def run_config(
    output: TextIO,
) -> int:
    """
    Display platform directory paths and configuration status.
    """
    platform_name = "Windows" if is_windows() else ("macOS" if is_macos() else "Linux/POSIX")
    config_file = get_default_config_path()
    status = "found" if config_file.exists() else "not initialized (run 'scholaros init')"

    print("ScholarOS Platform & Configuration Paths", file=output)
    print("----------------------------------------", file=output)
    print(f"Platform         : {platform_name} ({sys.platform})", file=output)
    print(f"Application Dir  : {get_app_dir()}", file=output)
    print(f"Configuration Dir: {get_config_dir()}", file=output)
    print(f"Data Dir         : {get_data_dir()}", file=output)
    print(f"Cache Dir        : {get_cache_dir()}", file=output)
    print(f"Log Dir          : {get_log_dir()}", file=output)
    print(f"Config File Path : {config_file} [{status}]", file=output)
    return 0


def run_gui(
    output: TextIO,
) -> int:
    """
    Launch the ScholarOS desktop GUI application.
    """
    print("Starting ScholarOS Desktop GUI...", file=output)
    try:
        from scholaros.gui.launcher import launch_gui
        launch_gui()
        return 0
    except Exception as exc:
        print(f"Error starting ScholarOS Desktop GUI: {exc}", file=output)
        return 1


def run_research(
    output: TextIO,
    query: str,
    provider: str | None = None,
    model: str | None = None,
) -> int:
    """
    Execute an AI research query directly from the terminal.
    """
    from scholaros.ai.factory import AIFactory

    target_provider = (provider or "mock").lower()
    print(f"Executing ScholarOS research query: '{query}'", file=output)
    print(f"Provider: {target_provider} | Model: {model or 'default'}", file=output)

    try:
        client = AIFactory.create_client(
            providers=[target_provider],
            default_provider=target_provider,
        )
        response = client.generate(
            prompt_or_messages=query,
            model=model,
        )
        print("\nResponse:", file=output)
        print(response.content, file=output)
        return 0
    except Exception as exc:
        print(f"Error executing research query: {exc}", file=output)
        return 1
