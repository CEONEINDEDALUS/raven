# Raven AI Assistant - Installation Guide

## Quick Start

### Option 1: Automated Installation (Recommended)

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama:**
   - Download from [ollama.com](https://ollama.com)
   - Or run: `curl -fsSL https://ollama.com/install.sh | sh`

3. **Pull the AI model:**
   ```bash
   ollama pull mistral:7b
   ```

4. **Run Raven:**
   ```bash
   python raven.py
   ```

## What the Installer Does

The `install.py` script automatically:

1. **Checks Python version** (requires 3.8+)
2. **Installs Python packages** from requirements.txt
3. **Installs Ollama** (if not present)
4. **Downloads AI models** (Mistral 7B and Whisper medium)
5. **Sets up TTS voices** (Kokoro)
6. **Verifies installation** with comprehensive tests
7. **Creates desktop shortcut** (optional)

## Requirements

- **Python 3.8+** 
- **Internet connection** (for downloading models)
- **Administrator privileges** (for system-wide installations)
- **Audio system** (for voice input/output)

## Installed Components

### Core Dependencies
- PyQt6 - GUI framework
- Ollama - Local AI model runner
- OpenAI Whisper - Speech recognition
- NumPy - Numerical computing
- SpeechRecognition - Audio processing
- ONNX Runtime - Model inference
- Kokoro - Text-to-speech
- SoundDevice - Audio I/O

### AI Models
- **Mistral 7B** - Large language model (~4GB)
- **Whisper Medium** - Speech recognition model (~1.5GB)

## Troubleshooting

### Common Issues

1. **Ollama installation fails:**
   - Manually download from [ollama.com](https://ollama.com)
   - Ensure Ollama service is running: `ollama serve`

2. **Audio issues:**
   - Check microphone permissions
   - Test audio devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`

3. **Model download fails:**
   - Check internet connection
   - Ensure sufficient disk space (6GB+ recommended)
   - Try manual download: `ollama pull mistral:7b`

4. **Python package conflicts:**
   - Use virtual environment: `python -m venv venv`
   - Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)

### Manual Verification

Test individual components:
```bash
# Test Python packages
python install.py --test

# Test Ollama
ollama list

# Test Whisper
python -c "import whisper; print('Whisper OK')"

# Test audio
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## Support

If installation issues persist:
1. Check the installation log for specific errors
2. Verify all requirements are met
3. Try manual installation steps
4. Ensure sufficient disk space and memory

## Post-Installation

After successful installation:
1. Run Raven: `python raven.py`
2. The AI assistant will start with voice and text interface
3. Use desktop shortcut for easy access (if created)

Enjoy your local AI assistant! 🚀