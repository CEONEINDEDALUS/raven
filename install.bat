@echo off
title R.A.V.E.N. Installation

echo.
echo ==============================================================
echo   R.A.V.E.N. (Reclusive Artificial Vision Enhanced Navigator)
echo ==============================================================
echo.
echo This script will install R.A.V.E.N. and all dependencies.
echo.
echo The installer will:
echo   - Check and install Python if needed
echo   - Create virtual environment
echo   - Install all Python requirements
echo   - Check and install Ollama if needed
echo   - Download required AI models
echo   - Run automatic troubleshooting
echo.

choice /C YN /M "Do you want to continue"
if errorlevel 2 exit /b 1

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python install.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installation completed successfully!
    echo.
    echo To run R.A.V.E.N.:
    echo   run.bat
    echo   or
    echo   venv\Scripts\python.exe raven.py
) else (
    echo.
    echo ❌ Installation failed. Please check the error messages above.
    echo For troubleshooting, see README.md
)

echo.
pause
