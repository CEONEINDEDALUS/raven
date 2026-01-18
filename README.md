# 🦅 R.A.V.E.N.

**Reclusive Artificial Vision Enhanced Navigator**

> *Just another temporary AI assistant in your life, but better.*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

A local, offline-first AI assistant operating with logical precision and analytical efficiency. Built somewhere between hell and heaven, for those who appreciate computational elegance.

---

## ✨ Features

- 🧠 **Local AI Chat** - Powered by Ollama (llama3.1:8b)
- 🎤 **Voice Input** - Local Whisper speech-to-text
- 🔊 **Voice Output** - Kokoro ONNX TTS (with intelligent fallback)
- 👁️ **Camera Vision** - Real-time visual analysis via qwen2.5vl:7b
- 🖥️ **PyQt6 Desktop UI** - Arc reactor visualization that actually works

## 📥 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/CEONEINDEDALUS/raven.git
cd raven
```

### Step 2: Run the Installer

After cloning, run the appropriate installer for your platform:

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```bat
install.bat
```

The installer will automatically:
- ✅ Check Python installation (installs if needed on Linux)
- ✅ Create virtual environment
- ✅ Install all Python requirements
- ✅ Download Whisper model
- ✅ Check Ollama installation (installs if needed)
- ✅ Start Ollama service
- ✅ Download required AI models (llama3.1:8b, qwen2.5vl:7b)
- ✅ Run automatic troubleshooting
- ✅ Create run scripts

### Step 3: Verify Installation

Check that everything is set up correctly:

```bash
# Verify Python virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Check installed packages
pip list

# Verify Ollama models
ollama list
```

## 🚀 Quick Start

### Running R.A.V.E.N.

After installation (see [Installation](#-installation) above), start the application:

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```bat
run.bat
```

## 💬 Usage

### Voice Commands

Once you click **"INITIATE PROTOCOL"**:

**Basic:**
- `"Hello"` or `"Hi R.A.V.E.N."` - Greet the assistant
- `"How are you"` - System status check
- `"Who are you"` - Identity information
- `"Goodbye"` or `"Shutdown"` - Exit gracefully

**Camera:**
- `"Open camera"` - Activate vision overlay
- `"Close camera"` - Deactivate camera
- `"What do you see"` - Analyze camera feed
- `"What are you seeing"` - Detailed visual analysis

**Conversation:**
- Ask anything naturally - R.A.V.E.N. maintains context and responds with logical precision

### Visual Indicators

**Arc Reactor:**
- 🔵 **Cyan** - Standing by
- 🟢 **Green** - Listening
- 🟠 **Orange** - Processing
- 🔵 **Blue** - Speaking

## 🔧 Requirements

- **Python 3.8+** (auto-checked/installed)
- **Microphone** (for voice input)
- **Speakers/Headphones** (for voice output)
- **Camera** (optional, for vision)
- **Ollama** (auto-installed if missing)
- **Internet** (for initial setup)

## 🛠️ Troubleshooting

### Common Issues

**"Error connecting to neural core"**
```bash
# Linux
sudo systemctl start ollama

# macOS
ollama serve

# Windows
# Start Ollama from Start Menu
```

**Microphone not working**
```bash
# Check devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Linux: Install dependencies
sudo apt-get install portaudio19-dev python3-dev
pip install PyAudio
```

**Camera not opening**
```bash
# Test camera
python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

**Models missing**
```bash
ollama pull llama3.1:8b
ollama pull qwen2.5vl:7b
ollama list  # Verify installation
```

## ⚙️ Configuration

Edit `raven.py` to customize:

```python
OLLAMA_MODEL = "llama3.1:8b"        # Main chat model
VISION_MODEL = "qwen2.5vl:7b"       # Vision model
WHISPER_SIZE = "medium"              # STT model size
MAX_MEMORY_TOKENS = 4000            # Conversation history limit
```

## 📁 Project Structure

```
raven/
├── raven.py              # Main application
├── camera_overlay.py      # Camera overlay & capture
├── kokoro_tts.py         # TTS integration
├── install.py            # Comprehensive installer
├── install.sh            # Linux/macOS wrapper
├── install.bat           # Windows wrapper
├── requirements.txt      # Python dependencies
└── models/               # Downloaded models
```

## 🧪 Advanced

**Debug mode:**
```bash
python -X faulthandler raven.py
```

**Test components:**
```bash
# Ollama
ollama list
ollama run llama3.1:8b

# Audio
python -c "import sounddevice as sd; print(sd.query_devices())"

# Camera
python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

## 📚 Documentation

- **[USAGE.md](USAGE.md)** - Detailed usage guide
- **[INSTALL.md](INSTALL.md)** - Additional installation notes

## 🤝 Contributing

Feel free to open issues or submit pull requests. I may be slow to respond, but I'll get there eventually.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 👤 Author

**CEONEINDEDALUS**

- GitHub: [@CEONEINDEDALUS](https://github.com/CEONEINDEDALUS)
- Location: Somewhere between hell and heaven
- Team: Team Dedalus

---

> *"Precision. Directness. Zero redundancy."* - R.A.V.E.N.
