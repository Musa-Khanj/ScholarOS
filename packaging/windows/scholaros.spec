# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification for ScholarOS Desktop Application on Windows.

Build with:
    pyinstaller packaging/windows/scholaros.spec
"""

import sys
from pathlib import Path

block_cipher = None

repo_root = Path.cwd().resolve()
scholaros_path = str(repo_root / "scholaros")

a = Analysis(
    [str(repo_root / "scholaros" / "gui" / "launcher.py")],
    pathex=[str(repo_root)],
    binaries=[],
    datas=[
        (str(repo_root / "pyproject.toml"), "."),
    ],
    hiddenimports=[
        "scholaros",
        "scholaros.gui",
        "scholaros.gui.launcher",
        "scholaros.gui.builder",
        "scholaros.gui.window",
        "scholaros.gui.views",
        "scholaros.gui.components",
        "scholaros.platform",
        "scholaros.platform.paths",
        "scholaros.ai",
        "scholaros.ai.factory",
        "scholaros.ai.providers",
        "scholaros.ai.providers.mock",
        "scholaros.ai.providers.ollama",
        "scholaros.ai.providers.openai",
        "scholaros.ai.providers.anthropic",
        "scholaros.ai.providers.google",
        "scholaros.ai.providers.openrouter",
        "scholaros.knowledge",
        "scholaros.retrieval",
        "scholaros.research",
        "scholaros.services",
        "scholaros.services.builtin",
        "scholaros.security",
        "scholaros.events",
        "scholaros.logging",
        "scholaros.config",
        "tkinter",
        "tkinter.ttk",
        "sqlite3",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "mypy",
        "ruff",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ScholarOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ScholarOS",
)
