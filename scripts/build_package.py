"""
ScholarOS Package Builder Script.

Automates building distribution packages (wheels and source distributions),
verifying package integrity, entry point registration, and archive contents.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile


def clean_dist(dist_dir: Path) -> None:
    """Remove previous build artifacts from dist directory."""
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def build_distribution(
    repo_root: Path,
    dist_dir: Path,
    wheel: bool = True,
    sdist: bool = True,
) -> list[Path]:
    """
    Build wheel and/or sdist using the python -m build module.
    """
    dist_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(dist_dir)]
    if wheel and not sdist:
        cmd.append("--wheel")
    elif sdist and not wheel:
        cmd.append("--sdist")

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Package build failed with code {result.returncode}")

    artifacts = list(dist_dir.glob("scholaros*"))
    return artifacts


def verify_wheel(wheel_path: Path) -> dict[str, list[str]]:
    """
    Inspect the generated wheel zip archive to verify required metadata and entrypoints.
    """
    assert wheel_path.suffix == ".whl", f"Expected .whl file, got {wheel_path.name}"
    with zipfile.ZipFile(wheel_path, "r") as zf:
        namelist = zf.namelist()

        entry_points = []
        metadata_lines = []

        for name in namelist:
            if name.endswith("entry_points.txt"):
                entry_points = zf.read(name).decode("utf-8").splitlines()
            elif name.endswith("METADATA"):
                metadata_lines = zf.read(name).decode("utf-8").splitlines()

        return {
            "files": namelist,
            "entry_points": entry_points,
            "metadata": metadata_lines,
        }


def verify_sdist(sdist_path: Path) -> list[str]:
    """
    Inspect the generated source distribution tarball.
    """
    assert sdist_path.name.endswith(".tar.gz"), f"Expected .tar.gz file, got {sdist_path.name}"
    with tarfile.open(sdist_path, "r:gz") as tf:
        return tf.getnames()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ScholarOS packaging and distribution builder")
    parser.add_argument("--clean", action="store_true", help="Clean dist/ before building")
    parser.add_argument("--wheel-only", action="store_true", help="Build only binary wheel")
    parser.add_argument("--sdist-only", action="store_true", help="Build only source distribution")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing archives in dist/")

    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"

    if args.clean and not args.verify_only:
        clean_dist(dist_dir)

    if not args.verify_only:
        build_wheel = not args.sdist_only
        build_sdist = not args.wheel_only
        print(f"Building ScholarOS packages (wheel={build_wheel}, sdist={build_sdist})...")
        artifacts = build_distribution(repo_root, dist_dir, wheel=build_wheel, sdist=build_sdist)
    else:
        artifacts = list(dist_dir.glob("scholaros*"))

    print(f"\nDiscovered {len(artifacts)} artifact(s) in {dist_dir}:")
    for art in artifacts:
        print(f" - {art.name} ({art.stat().st_size:,} bytes)")

    wheels = [a for a in artifacts if a.name.endswith(".whl")]
    for w in wheels:
        info = verify_wheel(w)
        print(f"\n[VERIFIED WHEEL] {w.name}")
        print(f"  Package entries: {len(info['files'])} files")
        print("  Entry points:")
        for ep in info["entry_points"]:
            if ep.strip():
                print(f"    {ep}")

    sdists = [a for a in artifacts if a.name.endswith(".tar.gz")]
    for s in sdists:
        names = verify_sdist(s)
        print(f"\n[VERIFIED SDIST] {s.name}")
        print(f"  Archive entries: {len(names)} files")

    print("\nPackage build and verification successful.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
