"""
ScholarOS Plugin Installer.

Responsible for installing, uninstalling, and updating plugin packages
and files in the plugins directory.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import zipfile

from scholaros.plugins.exceptions import InstallationError
from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.metadata import PluginMetadata


class PluginInstaller:
    """
    Manages filesystem-level plugin installation, removal, and updates.
    """

    def __init__(self, target_dir: Path | str | None = None) -> None:
        self.target_dir = (
            Path(target_dir).resolve()
            if target_dir is not None
            else Path.cwd() / "plugins"
        )
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def is_installed(self, plugin_id: str) -> bool:
        """Check if a plugin exists in target directory."""
        dest_dir = self.target_dir / plugin_id
        dest_file = self.target_dir / f"{plugin_id}.py"
        return dest_dir.exists() or dest_file.exists()

    def install(self, source: str | Path) -> PluginMetadata:
        """
        Install a plugin from a directory, a single .py file, or a .zip archive.
        """
        src = Path(source).resolve()
        if not src.exists():
            raise InstallationError(f"Plugin source does not exist: {src}")

        try:
            if src.is_file() and src.suffix == ".zip":
                return self._install_from_zip(src)
            elif src.is_dir():
                return self._install_from_dir(src)
            elif src.is_file() and src.suffix == ".py":
                return self._install_from_single_file(src)
            else:
                raise InstallationError(f"Unsupported plugin source type: {src}")
        except Exception as exc:
            if isinstance(exc, InstallationError):
                raise
            raise InstallationError(f"Failed to install plugin from {src}: {exc}") from exc

    def _install_from_dir(self, src: Path) -> PluginMetadata:
        """Install a plugin folder."""
        # Find manifest
        manifest_file = None
        for name in ("manifest.json", "manifest.toml", "plugin.json"):
            candidate = src / name
            if candidate.is_file():
                manifest_file = candidate
                break

        if manifest_file:
            manifest = PluginManifest.from_file(manifest_file)
        else:
            manifest = PluginManifest(name=src.name.replace("_", " ").title(), id=src.name.lower())

        dest = self.target_dir / manifest.id
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(src, dest)
        return PluginMetadata.from_manifest(manifest)

    def _install_from_single_file(self, src: Path) -> PluginMetadata:
        """Install a single .py plugin file."""
        plugin_id = src.stem.lower()
        manifest = PluginManifest(name=src.stem.replace("_", " ").title(), id=plugin_id)
        dest = self.target_dir / f"{plugin_id}.py"
        shutil.copy2(src, dest)
        return PluginMetadata.from_manifest(manifest)

    def _install_from_zip(self, src: Path) -> PluginMetadata:
        """Install a plugin from a zip archive."""
        temp_dir = self.target_dir / f".temp_{src.stem}"
        try:
            with zipfile.ZipFile(src, "r") as z:
                z.extractall(temp_dir)

            # Check if zip contains a single root folder or direct files
            subdirs = [p for p in temp_dir.iterdir() if p.is_dir()]
            root = subdirs[0] if len(subdirs) == 1 else temp_dir
            metadata = self._install_from_dir(root)
            return metadata
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def uninstall(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin by removing its directory or file.
        """
        dest_dir = self.target_dir / plugin_id
        dest_file = self.target_dir / f"{plugin_id}.py"

        removed = False
        try:
            if dest_dir.exists() and dest_dir.is_dir():
                shutil.rmtree(dest_dir)
                removed = True
            elif dest_file.exists() and dest_file.is_file():
                dest_file.unlink()
                removed = True
        except Exception as exc:
            raise InstallationError(f"Failed to uninstall plugin {plugin_id!r}: {exc}") from exc

        return removed

    def update(self, plugin_id: str, source: str | Path) -> PluginMetadata:
        """
        Update an existing plugin by replacing it with a new version.
        """
        if not self.is_installed(plugin_id):
            raise InstallationError(f"Cannot update non-existent plugin: {plugin_id!r}")

        # Install new source (will overwrite destination)
        return self.install(source)


__all__ = [
    "PluginInstaller",
]
