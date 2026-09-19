# Troubleshooting & Diagnostics

This guide provides practical solutions for common operational issues encountered when installing, configuring, or running ScholarOS.

---

## 1. Diagnostics Quick Check

Run the CLI diagnostics command to verify system health and configuration resolution:

```bash
scholaros status
scholaros config
```

If any errors are reported, check the sections below.

---

## 2. Common Issues & Solutions

### Issue A: "Connection refused: http://localhost:11434" (Ollama Offline)
- **Symptom**: CLI or GUI throws `ProviderConnectionError` or says Ollama is unavailable.
- **Cause**: The local Ollama daemon is not running.
- **Solution**:
  1. Open a terminal and start Ollama:
     ```bash
     ollama serve
     ```
  2. Verify it is listening:
     ```bash
     curl http://localhost:11434/api/tags
     ```
  3. Ensure you pulled your model:
     ```bash
     ollama pull qwen2.5:1.5b
     ```
  4. Alternatively, switch to mock mode for testing without a model:
     ```bash
     scholaros run "test query" --provider mock
     ```

### Issue B: "no display name and no $DISPLAY environment variable" (Linux Headless)
- **Symptom**: Launching `scholaros gui` on a remote Linux server or SSH session fails because Tkinter cannot open a window.
- **Solution**:
  - For headless servers, use the CLI directly:
    ```bash
    scholaros run "Your research query"
    ```
  - If running via SSH with X11 forwarding enabled:
    ```bash
    ssh -X user@host
    ```
  - Or use a virtual framebuffer (Xvfb):
    ```bash
    xvfb-run scholaros gui
    ```

### Issue C: Corrupted or Outdated Configuration File
- **Symptom**: Application fails during configuration loading or validation with `ConfigurationError`.
- **Solution**:
  Force reset your configuration file to the canonical factory starter config:
  ```bash
  scholaros init --force
  ```

### Issue D: Missing `python3-tk` on Linux
- **Symptom**: `ImportError: No module named '_tkinter'` when running `scholaros-gui`.
- **Solution**:
  Install the Python Tkinter system package:
  ```bash
  # Debian / Ubuntu:
  sudo apt-get update && sudo apt-get install -y python3-tk

  # Fedora:
  sudo dnf install -y python3-tkinter

  # Arch Linux:
  sudo pacman -S tk
  ```

---

## 3. Application Logs & Telemetry

ScholarOS writes structured diagnostic logs to the platform logs directory:
- **Windows**: `%LOCALAPPDATA%\ScholarOS\logs\scholaros.log`
- **Linux**: `~/.local/state/scholaros/logs/scholaros.log`
- **macOS**: `~/Library/Logs/ScholarOS/scholaros.log`

To inspect the latest log entries on Windows (PowerShell):
```powershell
Get-Content "$env:LOCALAPPDATA\ScholarOS\logs\scholaros.log" -Tail 50
```
On Linux / macOS:
```bash
tail -n 50 ~/.local/state/scholaros/logs/scholaros.log
```

Next Step: If you are interested in extending or contributing to ScholarOS, explore the [Developer Getting Started Guide](../developer/getting_started.md).
