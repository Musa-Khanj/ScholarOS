"""
ScholarOS Local CI Runner.

Executes the standard Continuous Integration verification pipeline locally:
  1. Environment & Dependency Check
  2. Ruff Linting
  3. Mypy Static Type Analysis
  4. Pytest Test Suite
  5. Package Build (Wheel & Sdist)
  6. Package Archive & Entrypoint Verification

Usage:
    python scripts/ci_check.py [--skip-build] [--skip-tests] [--verbose]
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time


def print_step_header(step_num: int, total_steps: int, title: str) -> None:
    print("\n" + "=" * 70)
    print(f"[{step_num}/{total_steps}] {title.upper()}")
    print("=" * 70)


def run_command(
    cmd: list[str],
    cwd: Path,
    description: str,
    verbose: bool = False,
) -> float:
    """Execute a subprocess command and measure elapsed time."""
    start_time = time.perf_counter()
    print(f"--> Executing: {' '.join(cmd)}")

    if verbose:
        result = subprocess.run(cmd, cwd=cwd, text=True)
    else:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    elapsed = time.perf_counter() - start_time

    if result.returncode != 0:
        print(f"\n[FAILED] {description} (exit code: {result.returncode})")
        if not verbose and hasattr(result, "stdout"):
            if result.stdout:
                print("\n--- Standard Output ---")
                print(result.stdout)
            if result.stderr:
                print("\n--- Standard Error ---")
                print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Step '{description}' failed with code {result.returncode}")

    print(f"[PASSED] {description} in {elapsed:.2f}s")
    return elapsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ScholarOS local CI validation runner")
    parser.add_argument("--skip-build", action="store_true", help="Skip packaging build steps")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest execution")
    parser.add_argument("--verbose", action="store_true", help="Show live subprocess output")

    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent

    total_steps = 6
    if args.skip_tests:
        total_steps -= 1
    if args.skip_build:
        total_steps -= 2

    current_step = 1
    timings: dict[str, float] = {}

    start_total = time.perf_counter()

    try:
        # Step 1: Environment Check
        print_step_header(current_step, total_steps, "Environment & Dependency Validation")
        env_cmd = [
            sys.executable,
            "-c",
            "import scholaros, pytest, ruff, mypy, build, setuptools, wheel; "
            "print('All core tools importable.')",
        ]
        timings["Environment Check"] = run_command(
            env_cmd, repo_root, "Environment Check", args.verbose
        )
        current_step += 1

        # Step 2: Ruff Lint Check
        print_step_header(current_step, total_steps, "Ruff Linting & Code Style")
        ruff_cmd = [sys.executable, "-m", "ruff", "check", "scholaros", "tests", "scripts"]
        timings["Ruff Lint"] = run_command(ruff_cmd, repo_root, "Ruff Linting", args.verbose)
        current_step += 1

        # Step 3: Mypy Static Type Analysis
        print_step_header(current_step, total_steps, "Mypy Static Type Analysis")
        mypy_cmd = [sys.executable, "-m", "mypy", "scholaros", "scripts"]
        timings["Mypy Type Check"] = run_command(
            mypy_cmd, repo_root, "Mypy Type Analysis", args.verbose
        )
        current_step += 1

        # Step 4: Pytest Suite
        if not args.skip_tests:
            print_step_header(current_step, total_steps, "Pytest Regression Suite")
            pytest_cmd = [sys.executable, "-m", "pytest", "-p", "no:langsmith", "-q"]
            timings["Pytest Suite"] = run_command(
                pytest_cmd, repo_root, "Pytest Regression Suite", args.verbose
            )
            current_step += 1

        # Step 5 & 6: Packaging Build & Verification
        if not args.skip_build:
            print_step_header(current_step, total_steps, "Distribution Package Build (Wheel & Sdist)")
            build_cmd = [sys.executable, "scripts/build_package.py", "--clean"]
            timings["Package Build"] = run_command(
                build_cmd, repo_root, "Package Build", args.verbose
            )
            current_step += 1

            print_step_header(current_step, total_steps, "Package Archive & Entrypoint Verification")
            verify_cmd = [sys.executable, "scripts/build_package.py", "--verify-only"]
            timings["Package Verification"] = run_command(
                verify_cmd, repo_root, "Package Verification", args.verbose
            )
            current_step += 1

        total_elapsed = time.perf_counter() - start_total

        # Summary Report
        print("\n" + "=" * 70)
        print("CI PIPELINE SUCCESSFUL - ALL GATES PASSED")
        print("=" * 70)
        for stage, duration in timings.items():
            print(f"  [PASS] {stage:<35} : {duration:.2f}s")
        print("-" * 70)
        print(f"Total Execution Time: {total_elapsed:.2f}s\n")
        return 0

    except Exception as exc:
        print(f"\n[CI PIPELINE ABORTED] Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
