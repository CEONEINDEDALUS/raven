#!/bin/bash

echo "🦅 R.A.V.E.N. (Reclusive Artificial Vision Enhanced Navigator)"
echo "=============================================================="
echo
echo "This script will install R.A.V.E.N. and all dependencies."
echo
echo "The installer will:"
echo "  - Check and install Python if needed"
echo "  - Create virtual environment"
echo "  - Install all Python requirements"
echo "  - Check and install Ollama if needed"
echo "  - Download required AI models"
echo "  - Run automatic troubleshooting"
echo

read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    echo "Installation guide:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

python3 install.py

if [ $? -eq 0 ]; then
    echo
    echo "✅ Installation completed successfully!"
    echo
    echo "To run R.A.V.E.N.:"
    echo "  ./run.sh"
    echo "  or"
    echo "  source venv/bin/activate && python raven.py"
else
    echo
    echo "❌ Installation failed. Please check the error messages above."
    echo "For troubleshooting, see README.md"
    exit 1
fi
