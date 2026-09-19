@echo off
rem ============================================================================
rem ScholarOS Windows Desktop Launcher
rem ============================================================================

setlocal enabledelayedexpansion

rem Determine repository root or installation directory
set "APP_DIR=%~dp0..\.."
cd /d "%APP_DIR%"

rem Locate Python executable
set "PYTHON_EXE="

if exist "%APP_DIR%\.venv\Scripts\pythonw.exe" (
    set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\pythonw.exe"
) else if exist "%APP_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
) else (
    rem Fallback to system python
    for %%P in (pythonw.exe python.exe) do (
        for /f "tokens=*" %%I in ('where %%P 2^>nul') do (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%I"
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python 3.14+ runtime was not found.
    echo Please install Python and make sure it is added to your PATH or create a .venv.
    pause
    exit /b 1
)

rem Launch ScholarOS Desktop GUI
start "" "%PYTHON_EXE%" -m scholaros.gui.launcher %*
exit /b 0
