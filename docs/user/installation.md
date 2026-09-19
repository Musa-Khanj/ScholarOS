# Installation Guide

This guide covers system prerequisites, installation methods, and verification steps for **ScholarOS** on Windows, Linux, and macOS.

---

## 1. System Requirements

### Hardware Prerequisites
- **CPU**: Modern x86_64 or ARM64 processor (Intel Core i5/AMD Ryzen 5 or Apple Silicon M1+ recommended).
- **RAM**:
  - Minimum: 4 GB RAM (with mock or cloud providers).
  - Recommended: 16 GB+ RAM (for running local LLMs via Ollama, such as `qwen2.5:1.5b` or `llama3.2:3b`).
- **Disk Space**: 500 MB for ScholarOS core package; 5 GB+ if storing local vector embeddings and cached documents.

### Operating Systems
- **Microsoft Windows**: Windows 10 or Windows 11 (64-bit).
- **Linux**: Ubuntu 22.04+, Debian 12+, Fedora 38+, Arch Linux.
- **macOS**: macOS 13 (Ventura) or later (Apple Silicon or Intel).

### Software Requirements
- **Python**: Version `3.12`, `3.13`, or `3.14+` with `pip` and `tkinter` support.
  - On Windows: Ensure "Add python.exe to PATH" is checked during installation.
  - On Ubuntu/Debian: Ensure `python3-tk` is installed:
    ```bash
    sudo apt-get update && sudo apt-get install -y python3-tk
    ```

---

## 2. Recommended Installation: Virtual Environment

We recommend installing ScholarOS into an isolated virtual environment:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Linux / macOS:
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip
```

---

## 3. Installation Options

### Option A: Install from PyPI (Recommended)
```bash
pip install scholaros
```

To install with development, GUI, and build dependencies:
```bash
pip install "scholaros[all]"
```

### Option B: Install from Built Wheel / Release Artifact
If you downloaded a release `.whl` from GitHub Releases:
```bash
pip install dist/scholaros-1.0.0-py3-none-any.whl
```

### Option C: Install from Source (Git Clone)
```bash
git clone https://github.com/Musa-Khanj/ScholarOS.git
cd ScholarOS
pip install -e .
```

---

## 4. Windows Desktop Batch Launcher

For Windows users who prefer launching directly without opening a terminal:
1. Navigate to `packaging\windows\run_scholaros.bat`.
2. Double-click `run_scholaros.bat` or create a desktop shortcut.
3. The launcher automatically detects the `.venv` Python runtime and launches the ScholarOS Desktop GUI (`scholaros-desktop` via `pythonw.exe`) without an intrusive command prompt window.

---

## 5. Verify Your Installation

Run the CLI health check to verify that ScholarOS is installed correctly:

```bash
scholaros info
scholaros status
```

Expected output:
```text
ScholarOS
Version: 1.0.0
Description: A modular multi-agent AI research operating system.

ScholarOS status: READY
Version: 1.0.0
```

Next Step: Proceed to [First Launch Guide](first_launch.md) to bootstrap your directories and configuration.
