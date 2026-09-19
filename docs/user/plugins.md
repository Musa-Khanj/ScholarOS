# Managing Plugins & Capability Permissions

ScholarOS provides an isolated, permission-gated plugin architecture that allows external tools, calculators, scrapers, and data adapters to extend system capabilities safely.

---

## 1. Plugin Architecture Overview

Every ScholarOS plugin is isolated and declares explicit capability permissions:
- **Manifest**: Defines plugin name, version, author, description, and required permissions.
- **Capabilities & Permissions**: Granular rights required by the plugin:
  - `network`: Permission to make outbound HTTP requests.
  - `filesystem:read`: Permission to read files from approved paths.
  - `filesystem:write`: Permission to write outputs or cache files.
  - `execution`: Permission to execute sub-processes or computational tools.
- **Sandbox**: Plugins execute within a sandboxed environment; unauthorized system calls are blocked by the Security subsystem.

---

## 2. Built-in Plugins

ScholarOS ships with production built-in plugins:
- **System Metrics Plugin** (`scholaros.plugins.builtin.system_metrics`):
  - Monitors system memory, CPU utilization, and vector store footprint.
  - Helps evaluate whether local LLMs fit comfortably in system RAM without causing swap thrashing.

---

## 3. Configuring Plugins in `config.toml`

Enable or disable plugins via the configuration file:

```toml
[plugins]
# Automatically discover plugins placed in the plugins directory
auto_discovery = true

# List of enabled plugin names
enabled = [
    "SystemMetricsPlugin"
]

# Strict capability checking
enforce_permissions = true
```

Next Step: If you encounter any problems, see the [Troubleshooting Guide](troubleshooting.md).
