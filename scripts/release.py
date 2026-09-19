"""
ScholarOS Release Orchestrator & Integrity Verification.

Validates version consistency across pyproject.toml, scholaros/__init__.py,
and CHANGELOG.md, builds distribution archives, and calculates SHA256 checksums.

Usage:
    python scripts/release.py [--verify-version-only] [--build] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
import tomllib


def get_versions(repo_root: Path) -> dict[str, str]:
    """Extract declared versions across repository sources."""
    # 1. pyproject.toml
    pyproject_file = repo_root / "pyproject.toml"
    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
        pyproject_version = data.get("project", {}).get("version", "")

    # 2. scholaros/__init__.py
    init_file = repo_root / "scholaros" / "__init__.py"
    init_content = init_file.read_text(encoding="utf-8")
    init_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    pkg_version = init_match.group(1) if init_match else ""

    # 3. CHANGELOG.md
    changelog_file = repo_root / "CHANGELOG.md"
    changelog_content = changelog_file.read_text(encoding="utf-8") if changelog_file.exists() else ""
    changelog_match = re.search(r'##\s*\[([^\]]+)\]', changelog_content)
    changelog_version = changelog_match.group(1) if changelog_match else ""

    return {
        "pyproject": pyproject_version,
        "init": pkg_version,
        "changelog": changelog_version,
    }


def verify_versions(repo_root: Path) -> str:
    """Verify that all version strings match exactly."""
    versions = get_versions(repo_root)
    pyproject_v = versions["pyproject"]
    init_v = versions["init"]
    changelog_v = versions["changelog"]

    print("Version Synchronization Check:")
    print(f"  * pyproject.toml       : {pyproject_v}")
    print(f"  * scholaros/__init__.py: {init_v}")
    print(f"  * CHANGELOG.md         : {changelog_v}")

    if not pyproject_v:
        raise ValueError("Missing version in pyproject.toml")
    if pyproject_v != init_v:
        raise ValueError(f"Version mismatch: pyproject.toml ({pyproject_v}) != scholaros/__init__.py ({init_v})")
    if pyproject_v != changelog_v:
        raise ValueError(f"Version mismatch: pyproject.toml ({pyproject_v}) != CHANGELOG.md latest ({changelog_v})")

    print(f"\n[OK] Versions synchronized at v{pyproject_v}")
    return pyproject_v


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 cryptographic hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_checksums(dist_dir: Path) -> Path:
    """Generate SHA256SUMS.txt for all distribution archives."""
    archives = sorted(list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz")))
    if not archives:
        raise RuntimeError(f"No distribution packages found in {dist_dir}")

    sums_file = dist_dir / "SHA256SUMS.txt"
    lines = []
    print("\nCalculating SHA256 Checksums:")
    for archive in archives:
        digest = calculate_sha256(archive)
        print(f"  {digest}  {archive.name}")
        lines.append(f"{digest}  {archive.name}\n")

    sums_file.write_text("".join(lines), encoding="utf-8")
    print(f"\nChecksums saved to: {sums_file}")
    return sums_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ScholarOS release management tool")
    parser.add_argument("--verify-version-only", action="store_true", help="Only verify version consistency")
    parser.add_argument("--build", action="store_true", help="Build packages and calculate SHA256 checksums")
    parser.add_argument("--dry-run", action="store_true", help="Perform verification without writing artifacts")

    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"

    try:
        canonical_version = verify_versions(repo_root)

        if args.verify_version_only:
            return 0

        if args.build or not args.dry_run:
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))
            from scripts.build_package import build_distribution, clean_dist, verify_sdist, verify_wheel

            print(f"\nBuilding release packages for ScholarOS v{canonical_version}...")
            clean_dist(dist_dir)
            build_distribution(repo_root, dist_dir, wheel=True, sdist=True)

            # Verification
            wheels = list(dist_dir.glob("*.whl"))
            for w in wheels:
                verify_wheel(w)
            sdists = list(dist_dir.glob("*.tar.gz"))
            for s in sdists:
                verify_sdist(s)

            # Checksums
            generate_checksums(dist_dir)

            print(f"\n[SUCCESS] ScholarOS v{canonical_version} release bundle prepared in dist/")

        return 0

    except Exception as exc:
        print(f"\n[RELEASE FAILED] Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
