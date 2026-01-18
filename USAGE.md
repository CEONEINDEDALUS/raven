# R.A.V.E.N. Usage Guide

## Installation

### Quick Start

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```bat
install.bat
```

The installer handles everything automatically:
- ✅ Python check and installation (Linux)
- ✅ Virtual environment creation
- ✅ Python package installation
- ✅ Whisper model download
- ✅ Ollama installation (if needed)
- ✅ Ollama service startup
- ✅ AI model downloads (llama3.1:8b, qwen2.5vl:7b)
- ✅ Automatic troubleshooting
- ✅ Run script creation

## Running R.A.V.E.N.

### Method 1: Using Run Scripts (Easiest)

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```bat
run.bat
```

### Method 2: Manual Activation

**Linux/macOS:**
```bash
source venv/bin/activate
python raven.py
```

**Windows:**
```bat
venv\Scripts\activate
python raven.py
```

## Using R.A.V.E.N.

### Initial Setup

1. **Start the application** using one of the methods above
2. Wait for "SYSTEM READY" status
3. Click **"INITIATE PROTOCOL"** button
4. The system will start listening for voice commands

### Voice Commands

#### Basic Commands
- **"Hello"** or **"Hi R.A.V.E.N."** - Greet the assistant
- **"How are you"** - Check system status
- **"Who are you"** - Get identity information
- **"Goodbye"** or **"Shutdown"** - Exit the application

#### Camera Commands
- **"Open camera"** - Activate camera vision overlay
- **"Close camera"** - Deactivate camera
- **"Camera status"** - Check if camera is active
- **"What do you see"** - Analyze current camera feed
- **"What are you seeing"** - Get detailed visual analysis
- **"Describe what you see"** - Visual description

#### Conversation
- Ask any question naturally
- R.A.V.E.N. will respond with logical, precise answers
- The system maintains conversation context

### Visual Indicators

**Arc Reactor Colors:**
- 🔵 **Cyan** - System idle/standing by
- 🟢 **Green** - Listening for voice input
- 🟠 **Orange** - Processing/analyzing
- 🔵 **Blue** - Speaking/generating output

**Status Messages:**
- "SYSTEM READY" - Ready to start
- "Listening..." - Waiting for voice input
- "Processing Audio..." - Transcribing speech
- "Analyzing..." - Processing with AI
- "Speaking..." - Generating voice output
- "Standing by..." - Ready for next command

## Troubleshooting

### If Installation Fails

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8+
   ```

2. **Manual Python installation:**
   - Linux: `sudo apt-get install python3 python3-pip python3-venv`
   - macOS: `brew install python3`
   - Windows: Download from https://www.python.org/downloads/

3. **Re-run installer:**
   ```bash
   python3 install.py
   ```

### If Ollama Issues Occur

1. **Check Ollama installation:**
   ```bash
   ollama --version
   ```

2. **Start Ollama service:**
   - Linux: `sudo systemctl start ollama`
   - macOS: `ollama serve` (run in background)
   - Windows: Start from Start Menu

3. **Check installed models:**
   ```bash
   ollama list
   ```

4. **Install missing models:**
   ```bash
   ollama pull llama3.1:8b
   ollama pull qwen2.5vl:7b
   ```

### If Microphone Doesn't Work

1. **Check system permissions:**
   - Linux: Check PulseAudio/PipeWire settings
   - macOS: System Preferences > Security & Privacy > Microphone
   - Windows: Settings > Privacy > Microphone

2. **Test microphone:**
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

3. **Install PyAudio dependencies (Linux):**
   ```bash
   sudo apt-get install portaudio19-dev python3-dev
   pip install PyAudio
   ```

### If Camera Doesn't Work

1. **Check camera permissions:**
   - Linux: Check v4l2 permissions
   - macOS: System Preferences > Security & Privacy > Camera
   - Windows: Settings > Privacy > Camera

2. **Test camera:**
   ```bash
   python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
   ```

3. **Try different camera index:**
   - The system automatically tries indices 0-9
   - If automatic detection fails, check camera device list

### Common Error Messages

**"Error connecting to neural core"**
- Solution: Ensure Ollama is running and models are installed

**"Could not find PyAudio"**
- Solution: Install system dependencies and reinstall PyAudio

**"Camera error"**
- Solution: Check camera permissions and ensure no other app is using it

**"Vision model could not run"**
- Solution: Ensure qwen2.5vl:7b is installed and Ollama has enough memory

## Advanced Configuration

### Changing AI Models

Edit `raven.py`:

```python
OLLAMA_MODEL = "llama3.1:8b"  # Change to your preferred model
VISION_MODEL = "qwen2.5vl:7b"  # Change vision model
```

Then pull the new model:
```bash
ollama pull <model-name>
```

### Adjusting Memory

Edit `raven.py`:
```python
MAX_MEMORY_TOKENS = 4000  # Increase for longer conversations
```

### Changing Whisper Model Size

Edit `raven.py`:
```python
WHISPER_SIZE = "medium"  # Options: tiny, base, small, medium, large
```

## Tips for Best Experience

1. **Speak clearly** - Better recognition with clear pronunciation
2. **Wait for listening indicator** - Green light means it's ready
3. **Use camera in good lighting** - Better vision analysis
4. **Keep Ollama running** - Required for AI responses
5. **Check system resources** - Vision models can be memory-intensive

## Getting Help

1. Check the troubleshooting section above
2. Review terminal output for error messages
3. Verify all requirements are installed
4. Check README.md for detailed documentation
