#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import urllib.request
import shutil
import json
from pathlib import Path


class RavenInstaller:
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent.absolute()
        self.models_dir = self.project_root / "models"
        self.venv_dir = self.project_root / "venv"
        self.required_models = ["llama3.1:8b", "qwen2.5vl:7b"]

    def print_step(self, message):
        print(f"\n{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}")

    def print_success(self, message):
        print(f"✓ {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def print_warning(self, message):
        print(f"⚠ {message}")

    def check_python(self):
        self.print_step("Checking Python Installation")
        if self.python_version < (3, 8):
            self.print_error(f"Python 3.8+ required. Found: {self.python_version.major}.{self.python_version.minor}")
            print("\nPlease install Python 3.8+ from:")
            if self.system == "Windows":
                print("  https://www.python.org/downloads/")
            elif self.system == "Darwin":
                print("  brew install python3")
                print("  or download from: https://www.python.org/downloads/")
            else:
                print("  sudo apt-get install python3 python3-pip")
                print("  or: sudo yum install python3 python3-pip")
            return False
        self.print_success(f"Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} detected")
        return True

    def install_python_dependencies(self):
        self.print_step("Installing System Python Dependencies")
        if self.system == "Linux":
            self.print_warning("System dependencies may be needed for PyAudio")
            print("If PyAudio installation fails, install manually:")
            print("  Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-dev")
            print("  Fedora: sudo dnf install portaudio-devel python3-devel")
            print("  Arch: sudo pacman -S portaudio python")
            try:
                result = subprocess.run(
                    ["which", "apt-get"],
                    capture_output=True
                )
                if result.returncode == 0:
                    print("\nAttempting to install dependencies via apt-get...")
                    try:
                        subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True, timeout=60)
                        subprocess.run(
                            ["sudo", "apt-get", "install", "-y", "python3-venv", "python3-pip", "portaudio19-dev", "python3-dev"],
                            check=True,
                            capture_output=True,
                            timeout=300
                        )
                        self.print_success("System dependencies installed")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        self.print_warning("Could not install system dependencies automatically")
            except:
                pass
        return True

    def create_virtual_environment(self):
        self.print_step("Setting Up Virtual Environment")
        if self.venv_dir.exists():
            self.print_success("Virtual environment already exists")
            return True

        print("Creating virtual environment...")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_dir)],
                check=True,
                capture_output=True,
            )
            self.print_success("Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False

    def get_pip_command(self):
        if self.system == "Windows":
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")

    def get_python_command(self):
        if self.system == "Windows":
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")

    def install_requirements(self):
        self.print_step("Installing Python Requirements")
        pip_cmd = self.get_pip_command()

        print("Upgrading pip...")
        try:
            subprocess.run(
                [pip_cmd, "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
            )
            self.print_success("Pip upgraded")
        except subprocess.CalledProcessError:
            self.print_warning("Could not upgrade pip (continuing anyway)")

        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print("Installing from requirements.txt...")
            try:
                result = subprocess.run(
                    [pip_cmd, "install", "-r", str(requirements_file)],
                    check=True,
                    capture_output=False,
                )
                self.print_success("Requirements installed")
                return True
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install requirements: {e}")
                print("\nTroubleshooting:")
                print("1. Check internet connection")
                print("2. Try: pip install --upgrade pip setuptools wheel")
                print("3. For PyAudio on Linux: sudo apt-get install portaudio19-dev")
                print("4. For PyAudio on macOS: brew install portaudio")
                return False
        else:
            self.print_error("requirements.txt not found")
            return False

    def download_whisper_model(self):
        self.print_step("Downloading Whisper Model")
        self.models_dir.mkdir(exist_ok=True)
        python_cmd = self.get_python_command()

        download_script = """
import whisper
import os
import sys

models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

print("Downloading Whisper medium model...")
try:
    model = whisper.load_model("medium", download_root=models_dir)
    print("✓ Whisper model downloaded successfully")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [python_cmd, "-c", download_script],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.print_success("Whisper model downloaded")
                return True
            else:
                self.print_error(f"Whisper model download failed: {result.stderr}")
                return False
        except Exception as e:
            self.print_error(f"Error downloading Whisper model: {e}")
            return False

    def check_ollama_installed(self):
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_success(f"Ollama found: {version}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return False

    def install_ollama(self):
        self.print_step("Installing Ollama")
        if self.check_ollama_installed():
            self.print_success("Ollama already installed")
            return True

        print("Ollama not found. Installing...")
        if self.system == "Linux":
            print("Installing Ollama for Linux...")
            try:
                install_script = "curl -fsSL https://ollama.ai/install.sh | sh"
                result = subprocess.run(
                    install_script,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.print_success("Ollama installed")
                    subprocess.run(["sudo", "systemctl", "enable", "ollama"], capture_output=True)
                    subprocess.run(["sudo", "systemctl", "start", "ollama"], capture_output=True)
                    return True
                else:
                    self.print_error(f"Failed to install Ollama: {result.stderr}")
                    print("\nManual installation:")
                    print("  curl -fsSL https://ollama.ai/install.sh | sh")
                    return False
            except Exception as e:
                self.print_error(f"Error installing Ollama: {e}")
                print("\nManual installation:")
                print("  curl -fsSL https://ollama.ai/install.sh | sh")
                return False
        elif self.system == "Darwin":
            print("Installing Ollama for macOS...")
            try:
                if shutil.which("brew"):
                    result = subprocess.run(
                        ["brew", "install", "ollama"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.print_success("Ollama installed via Homebrew")
                        return True
                print("\nManual installation:")
                print("  brew install ollama")
                print("  or download from: https://ollama.ai/download")
                return False
            except Exception as e:
                self.print_error(f"Error installing Ollama: {e}")
                print("\nManual installation:")
                print("  brew install ollama")
                print("  or download from: https://ollama.ai/download")
                return False
        else:
            print("\nPlease install Ollama manually:")
            print("  Download from: https://ollama.ai/download")
            print("  After installation, restart this script")
            return False

    def check_ollama_running(self):
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def start_ollama_service(self):
        if self.system == "Linux":
            try:
                subprocess.run(["sudo", "systemctl", "start", "ollama"], check=True, capture_output=True)
                import time
                time.sleep(2)
                return True
            except:
                pass
        elif self.system == "Darwin":
            try:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time
                time.sleep(2)
                return True
            except:
                pass
        return False

    def check_ollama_models(self):
        available_models = []
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                output_lines = result.stdout.strip().split("\n")
                for line in output_lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            available_models.append(model_name)
        except:
            pass
        return available_models

    def install_ollama_models(self):
        self.print_step("Checking Ollama Models")
        if not self.check_ollama_running():
            self.print_warning("Ollama service not running. Attempting to start...")
            if not self.start_ollama_service():
                self.print_error("Could not start Ollama service")
                print("\nPlease start Ollama manually:")
                print("  Linux: sudo systemctl start ollama")
                print("  macOS: ollama serve")
                print("  Windows: Start Ollama from Start Menu")
                return False

        available_models = self.check_ollama_models()
        missing_models = [m for m in self.required_models if m not in available_models]

        if not missing_models:
            self.print_success("All required models are available")
            return True

        print(f"Missing models: {', '.join(missing_models)}")
        print("Installing missing models...")
        print("This may take a while depending on your internet connection.")

        for model in missing_models:
            print(f"\nPulling {model}...")
            try:
                result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=False,
                    timeout=3600
                )
                if result.returncode == 0:
                    self.print_success(f"{model} installed")
                else:
                    self.print_error(f"Failed to pull {model}")
                    print(f"Try manually: ollama pull {model}")
            except subprocess.TimeoutExpired:
                self.print_error(f"Timeout while pulling {model}")
                print(f"Try manually: ollama pull {model}")
            except Exception as e:
                self.print_error(f"Error pulling {model}: {e}")
                print(f"Try manually: ollama pull {model}")

        return True

    def troubleshoot(self):
        self.print_step("Running Troubleshooting")
        issues_found = []

        if not self.venv_dir.exists():
            issues_found.append("Virtual environment not created")

        pip_cmd = self.get_pip_command()
        try:
            subprocess.run([pip_cmd, "--version"], check=True, capture_output=True)
        except:
            issues_found.append("pip not working in virtual environment")

        if not self.check_ollama_installed():
            issues_found.append("Ollama not installed")

        if not self.check_ollama_running():
            issues_found.append("Ollama service not running")

        available_models = self.check_ollama_models()
        missing_models = [m for m in self.required_models if m not in available_models]
        if missing_models:
            issues_found.append(f"Missing models: {', '.join(missing_models)}")

        if issues_found:
            self.print_warning("Issues found:")
            for issue in issues_found:
                print(f"  - {issue}")
            return False
        else:
            self.print_success("No issues found")
            return True

    def create_run_script(self):
        python_cmd = self.get_python_command()

        if self.system == "Windows":
            script_content = f"@echo off\ncd /d {self.project_root}\n{python_cmd} raven.py\npause"
            script_path = self.project_root / "run.bat"
        else:
            script_content = f"#!/bin/bash\ncd {self.project_root}\nsource venv/bin/activate\n{python_cmd} raven.py"
            script_path = self.project_root / "run.sh"

        try:
            with open(script_path, "w") as f:
                f.write(script_content)

            if self.system != "Windows":
                os.chmod(script_path, 0o755)

            self.print_success(f"Created {script_path.name}")
            return True
        except Exception as e:
            self.print_error(f"Failed to create run script: {e}")
            return False

    def print_usage_instructions(self):
        self.print_step("Installation Complete - Usage Instructions")
        python_cmd = self.get_python_command()

        print("\n📖 HOW TO USE R.A.V.E.N.:")
        print("\n1. START THE APPLICATION:")
        if self.system == "Windows":
            print("   Option A: Double-click run.bat")
            print(f"   Option B: {python_cmd} raven.py")
        else:
            print("   Option A: ./run.sh")
            print(f"   Option B: source venv/bin/activate && {python_cmd} raven.py")

        print("\n2. VOICE COMMANDS:")
        print("   - Say 'open camera' to activate camera vision")
        print("   - Say 'close camera' to deactivate camera")
        print("   - Say 'what do you see' to analyze camera feed")
        print("   - Say 'goodbye' or 'shutdown' to exit")

        print("\n3. TROUBLESHOOTING:")
        print("   - If microphone doesn't work: Check system permissions")
        print("   - If camera doesn't work: Check camera permissions")
        print("   - If Ollama errors: Ensure Ollama service is running")
        print("   - If models missing: Run 'ollama pull llama3.1:8b' and 'ollama pull qwen2.5vl:7b'")

        print("\n4. REQUIRED MODELS:")
        for model in self.required_models:
            print(f"   - {model}")

        print("\n5. FOR MORE HELP:")
        print("   Check README.md for detailed documentation")

    def run(self):
        print("\n" + "="*60)
        print("  🦅 R.A.V.E.N. (Reclusive Artificial Vision Enhanced Navigator)")
        print("  Installation Script")
        print("="*60)

        if not self.check_python():
            return False

        if self.system == "Linux":
            self.install_python_dependencies()

        if not self.create_virtual_environment():
            return False

        if not self.install_requirements():
            return False

        if not self.download_whisper_model():
            self.print_warning("Whisper model download failed, but continuing...")

        if not self.check_ollama_installed():
            if not self.install_ollama():
                self.print_warning("Ollama installation failed. Please install manually.")
                print("Visit: https://ollama.ai/download")
        else:
            if not self.check_ollama_running():
                self.start_ollama_service()

        self.install_ollama_models()

        self.troubleshoot()

        self.create_run_script()

        self.print_usage_instructions()

        return True


if __name__ == "__main__":
    installer = RavenInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)
