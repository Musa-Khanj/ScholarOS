# First Launch & Initialization

This guide explains how to initialize your ScholarOS user environment, inspect configuration paths, and launch the application.

---

## 1. Initializing the User Environment (`scholaros init`)

Before running research pipelines or launching the desktop interface, bootstrap your local user environment:

```bash
scholaros init
```

### What `scholaros init` Does:
1. **Creates Standard OS Directories**:
   - **Windows**:
     - Config: `%APPDATA%\ScholarOS\config\`
     - Data: `%LOCALAPPDATA%\ScholarOS\data\`
     - Cache: `%LOCALAPPDATA%\ScholarOS\cache\`
     - Logs: `%LOCALAPPDATA%\ScholarOS\logs\`
   - **Linux / POSIX**:
     - Config: `~/.config/scholaros/`
     - Data: `~/.local/share/scholaros/data/`
     - Cache: `~/.cache/scholaros/`
     - Logs: `~/.local/state/scholaros/logs/` (or `~/.scholaros/logs/`)
   - **macOS**:
     - Config: `~/Library/Application Support/ScholarOS/config/`
     - Data: `~/Library/Application Support/ScholarOS/data/`
     - Cache: `~/Library/Caches/ScholarOS/`
     - Logs: `~/Library/Logs/ScholarOS/`

2. **Generates Default `config.toml`**:
   Writes a production-ready starter configuration file if one does not already exist.

3. **Safe Idempotency**:
   Running `scholaros init` multiple times will not overwrite your customized configuration. To force-reset the config to factory defaults:
   ```bash
   scholaros init --force
   ```

---

## 2. Inspecting Platform Configuration (`scholaros config`)

To view active platform directories and check the status of your configuration file:

```bash
scholaros config
```

Example Output:
```text
ScholarOS Platform & Configuration Paths
----------------------------------------
Platform         : Windows (win32)
Application Dir  : C:\Users\YourUser\AppData\Roaming\ScholarOS
Configuration Dir: C:\Users\YourUser\AppData\Roaming\ScholarOS\config
Data Dir         : C:\Users\YourUser\AppData\Local\ScholarOS\data
Cache Dir        : C:\Users\YourUser\AppData\Local\ScholarOS\cache
Log Dir          : C:\Users\YourUser\AppData\Local\ScholarOS\logs
Config File Path : C:\Users\YourUser\AppData\Roaming\ScholarOS\config\config.toml [found]
```

### Custom Environment Overrides (Sandboxing & Testing)
You can redirect ScholarOS paths anytime by setting environment variables:
- `SCHOLAROS_HOME`: Root directory override for all application files.
- `SCHOLAROS_CONFIG_DIR`: Override configuration directory.
- `SCHOLAROS_DATA_DIR`: Override persistent data directory.
- `SCHOLAROS_CACHE_DIR`: Override temporary cache storage.
- `SCHOLAROS_LOG_DIR`: Override log destination.

---

## 3. Launching the Desktop GUI

ScholarOS provides both console and windowed desktop launchers:

### Terminal Launcher
```bash
# Using CLI subcommand:
scholaros gui

# Or direct entry point:
scholaros-gui
```

### Windows Windowed Launcher (Zero Console Window)
```bash
scholaros-desktop
```
This launcher is registered under `[project.gui-scripts]` and invokes `pythonw.exe`, starting the ScholarOS desktop window cleanly without leaving a black terminal window open.

Next Step: Learn how to connect your preferred language models in the [LLM Configuration Guide](llm_configuration.md).
