# Plugin Development Guide

ScholarOS includes a sandboxed, capability-permissioned plugin subsystem. This guide walks you through authoring a complete custom plugin from scratch.

---

## 1. Plugin Structure

A ScholarOS plugin consists of:
1. **Manifest (`PluginManifest`)**: Declares metadata and requested capability permissions.
2. **Implementation (`BasePlugin` subclass)**: Implements lifecycle callbacks (`initialize`, `start`, `stop`).
3. **Tools / Endpoints**: Exposes computational tools or adapters to the AI and Research agents.

---

## 2. Example: Creating an ArXiv Search Plugin

Here is a complete implementation of a custom ArXiv search plugin:

```python
from typing import Any
from scholaros.plugins.base import BasePlugin
from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.permissions import PermissionSet, Permission


class ArxivSearchPlugin(BasePlugin):
    """Searches ArXiv for academic research preprints."""

    def __init__(self) -> None:
        manifest = PluginManifest(
            name="ArxivSearchPlugin",
            version="1.0.0",
            author="ScholarOS Contributor",
            description="Searches ArXiv for relevant scientific preprints.",
            permissions=PermissionSet(
                permissions=[Permission.NETWORK],  # Requests outbound HTTP access
            ),
        )
        super().__init__(manifest=manifest)

    def on_initialize(self) -> None:
        """Called when plugin is loaded into the registry."""
        pass

    def on_start(self) -> None:
        """Called when plugin is activated."""
        pass

    def on_stop(self) -> None:
        """Called when plugin is disabled or application shuts down."""
        pass

    def search_preprints(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """
        Execute search against ArXiv API.
        Protected by sandbox; requires NETWORK permission.
        """
        self.enforce_permission(Permission.NETWORK)
        
        # Example dummy results for illustration
        return [
            {
                "title": f"Preprint matching: {query}",
                "arxiv_id": "2401.00001",
                "abstract": "A novel approach to scientific literature synthesis...",
            }
        ]
```

---

## 3. Registering Your Plugin

Register the plugin into the `PluginManager`:

```python
from scholaros.plugins.manager import PluginManager

plugin_manager = PluginManager()
plugin = ArxivSearchPlugin()

# Register and activate
plugin_manager.register(plugin)
plugin_manager.start(plugin.name)
```

---

## 4. Security & Sandbox Constraints

The ScholarOS Security subsystem enforces permission validation before allowing sensitive operations:
- If a plugin attempts to access the filesystem without `Permission.FILESYSTEM_READ` or `FILESYSTEM_WRITE`, `PermissionDeniedError` is raised.
- Plugins cannot execute arbitrary sub-processes without `Permission.EXECUTION`.
- Sandboxed plugins cannot inspect host environment secrets (such as API keys) belonging to other services.

Next Step: Learn how to add a custom LLM backend in the [Provider Development Guide](provider_development.md).
