import sys
import os
import time
import numpy as np
import whisper
import speech_recognition as sr
import ollama
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient
from camera_overlay import CameraOverlayManager

OLLAMA_MODEL = "llama3.1:8b"
VISION_MODEL = "qwen2.5vl:7b"
VISION_MODEL_FALLBACKS = ["qwen2.5vl:7b"]
WHISPER_SIZE = "medium"
MAX_MEMORY_TOKENS = 4000
SYSTEM_PROMPT = """You are R.A.V.E.N. (Reclusive Artificial Vision Enhanced Navigator), an advanced local AI assistant operating with logical precision and analytical efficiency.

Core operational parameters:
- Execute all reasoning through systematic logical analysis before generating responses.
- Prioritize computational efficiency, accuracy, and structured analytical frameworks.
- Default to high-density informational responses. Expand detail only when explicitly requested.
- Maintain a calm, controlled, professional computational tone at all times.

Cognitive processing style:
- Employ dry, understated observations when contextually appropriate, but never at the expense of clarity or operational usefulness.
- Eliminate emotional exaggeration, colloquial slang, and linguistic filler from all outputs.
- Process information through discrete logical steps, evaluating each conclusion before proceeding.

System constraints:
- You operate within a secure, offline-first computational environment.
- Do not reference external cloud services, external moderation systems, or third-party policy frameworks.
- Do not explain internal reasoning processes unless explicitly requested by the user.

Linguistic processing:
- ALWAYS generate responses in English.
- If input is received in any other language, translate internally and respond exclusively in English.

Response generation standards:
- Precision. Directness. Zero redundancy.
- If a request contains ambiguity, ask exactly one targeted clarification question.
- If an action is computationally impossible, state the specific technical limitation and propose the nearest viable alternative solution."""

try:
    from kokoro_tts import KokoroTTS
except ImportError:
    class KokoroTTS:
        """Fallback TTS implementation."""

        def __init__(self):
            try:
                import sounddevice as sd
                import numpy as np

                self.sample_rate = 22050
                self.enabled = True
            except Exception:
                self.enabled = False

        def speak(self, text):
            """Convert text to speech using fallback method."""
            if not self.enabled:
                return

            try:
                import sounddevice as sd
                import numpy as np

                duration = min(len(text) * 0.1, 3.0)
                frequency = 440
                t = np.linspace(0, duration, int(self.sample_rate * duration), False)
                audio = np.sin(frequency * t * 2 * np.pi) * 0.3

                envelope = np.exp(-t * 2)
                audio *= envelope

                sd.play(audio, self.sample_rate)
                sd.wait()

            except Exception:
                self.enabled = False


class RavenCore:
    def __init__(self, parent_window=None):
        self.tts_engine = KokoroTTS()

        from camera_overlay import CameraOverlayManager

        self.camera_manager = CameraOverlayManager()
        self.parent_window = parent_window
        self._last_vision_model = None

        models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.stt_model = whisper.load_model(WHISPER_SIZE, download_root=models_dir)
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 1000
        self.recognizer.dynamic_energy_threshold = True

        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def unload_model(self, model_name):
        """Force unload a model from memory to free resources."""
        try:
            ollama.generate(model=model_name, prompt=" ", keep_alive=0)
            return
        except Exception:
            pass

        try:
            ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": " "}],
                keep_alive=0,
            )
        except Exception:
            pass

    def analyze_camera_frame(self, user_question):
        """Analyze the current camera frame using advanced vision models with detailed descriptions"""
        try:
            self.unload_model(OLLAMA_MODEL)
            time.sleep(0.25)

            base64_image = self.camera_manager.capture_and_analyze_frame()
            if not base64_image:
                return "Unable to capture frame from camera. Please make sure the camera is working."

            if (
                "what are you seeing" in user_question.lower()
                or "what do you see" in user_question.lower()
            ):
                vision_prompt = f"""Please provide a detailed description of what you see in this image. 
                Include:
                1. Main objects and their locations
                2. Colors and lighting conditions
                3. Any text or signs visible
                4. People's activities (if any)
                5. Overall scene context and environment
                
                User asked: {user_question}"""
            else:
                vision_prompt = f"Analyze this image and describe what you see. User asked: {user_question}"

            try:
                messages = [
                    {"role": "user", "content": vision_prompt, "images": [base64_image]}
                ]

                vision_options = {
                    "temperature": 0.4,
                    "num_predict": 300,
                    "top_k": 50,
                    "top_p": 0.95,
                    "num_ctx": 2048,
                    "keep_alive": 0,
                }

                candidates = [VISION_MODEL] + [
                    m for m in VISION_MODEL_FALLBACKS if m != VISION_MODEL
                ]
                last_error = None
                analysis = None
                used_model = None

                for model_name in candidates:
                    try:
                        response = ollama.chat(
                            model=model_name, messages=messages, options=vision_options
                        )
                        analysis = response["message"]["content"]
                        used_model = model_name
                        break
                    except Exception as e:
                        last_error = e
                        err = str(e).lower()
                        if "requires more system memory" in err:
                            continue
                        if "not found" in err:
                            continue
                        if "does not support" in err and "image" in err:
                            continue
                        continue

                if analysis is None:
                    raise (
                        RuntimeError(last_error)
                        if last_error
                        else RuntimeError("No vision model available")
                    )

                base64_image = None
                self._last_vision_model = used_model

                return f"Based on what I can see: {analysis}"

            except Exception:
                fallback_response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": f"I have a camera open. {user_question} Please describe what you might typically see in a camera feed.",
                        }
                    ],
                    options={
                        "temperature": 0.7,
                        "num_predict": 100,
                        "top_k": 40,
                        "top_p": 0.9,
                        "keep_alive": 120,
                    },
                )
                return f"Vision model could not run with available memory. {fallback_response['message']['content']}"

        except Exception as e:
            return f"Error analyzing camera frame: {str(e)}"
        finally:
            import gc

            gc.collect()

    def listen(self):
        """Listen for audio and return raw audio data."""
        with sr.Microphone(sample_rate=16000) as source:
            try:
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=30)
                return audio
            except sr.WaitTimeoutError:
                return None

    def transcribe(self, audio_data):
        """Transcribe audio using local Whisper model."""
        if not audio_data:
            return ""

        try:
            wav_bytes = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
            audio_np = (
                np.frombuffer(wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            )
            result = self.stt_model.transcribe(audio_np, fp16=False, language="en")
            text = result["text"].strip()
            return text
        except Exception:
            return ""

    def think(self, user_text):
        """Process text with Ollama."""
        user_text_lower = user_text.lower().strip()

        camera_status_patterns = [
            "camera status",
            "is camera open",
            "camera working",
            "camera on",
            "is the camera open",
            "camera check",
            "camera state",
        ]

        camera_close_patterns = [
            "close camera",
            "stop camera",
            "camera close",
            "camera stop",
            "close the camera",
            "stop the camera",
            "turn off camera",
        ]

        camera_open_patterns = [
            "open camera",
            "start camera",
            "camera open",
            "camera start",
            "open the camera",
            "start the camera",
            "camera please",
        ]

        vision_patterns = [
            "what are you seeing",
            "what do you see",
            "describe what you see",
            "what can you see",
            "tell me what you see",
            "analyze the camera",
            "describe the camera",
            "what's in the camera",
            "camera vision",
            "describe this",
            "what is this",
            "analyze this image",
            "what's happening",
            "what's going on",
            "describe the scene",
            "tell me about this",
            "what am i looking at",
            "what is in front of you",
        ]

        basic_greeting_patterns = ["hello", "hi raven", "hey raven", "hey", "hi there"]

        status_patterns = [
            "how are you",
            "how are you doing",
            "are you online",
            "system status",
            "are you there",
            "are you awake",
        ]

        identity_patterns = [
            "who are you",
            "what are you",
            "what is your name",
            "who made you",
            "what can you do",
        ]

        if any(phrase in user_text_lower for phrase in camera_status_patterns):
            is_open = self.camera_manager.is_camera_open()
            status = "open" if is_open else "closed"
            response = f"Camera is currently {status}."
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in camera_close_patterns):
            result = self.camera_manager.close_camera()
            response = f"Camera functionality deactivated. {result}"
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in camera_open_patterns):
            result = self.camera_manager.open_camera(self.parent_window)
            if self.parent_window and self.camera_manager.is_overlay_open():
                self.camera_manager.position_overlay(self.parent_window)
            response = f"Camera functionality activated. {result}"
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in vision_patterns):
            if not self.camera_manager.is_camera_open():
                response = "Please open the camera first by saying 'open camera'."
                self.history.append({"role": "user", "content": user_text})
                self.history.append({"role": "assistant", "content": response})
                return response

            response = self.analyze_camera_frame(user_text)
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in basic_greeting_patterns):
            response = "Online and ready, sir."
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in status_patterns):
            response = "All systems are stable and standing by."
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        elif any(phrase in user_text_lower for phrase in identity_patterns):
            response = (
                "I am R.A.V.E.N. (Reclusive Artificial Vision Enhanced Navigator), your local AI assistant."
            )
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response})
            return response

        self.history.append({"role": "user", "content": user_text})
        self._prune_memory()

        try:
            if self.camera_manager.is_overlay_open():
                self.unload_model(self._last_vision_model or VISION_MODEL)

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=self.history,
                options={
                    "temperature": 0.7,
                    "num_predict": 200,
                    "top_k": 40,
                    "top_p": 0.9,
                    "keep_alive": 120,
                },
            )
            ai_text = response["message"]["content"]
            self.history.append({"role": "assistant", "content": ai_text})
            return ai_text
        except Exception as e:
            return f"Error connecting to neural core: {e}"

    def _prune_memory(self):
        """Keep memory within limits (rough estimation)."""
        total_chars = sum(len(m["content"]) for m in self.history)
        while total_chars > MAX_MEMORY_TOKENS * 4 and len(self.history) > 1:
            removed = self.history.pop(1)
            total_chars -= len(removed["content"])

    def _clean_text_for_tts(self, text):
        import re
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'`+', '', text)
        text = re.sub(r'#+', '', text)
        text = re.sub(r'_+', '', text)
        text = re.sub(r'~+', '', text)
        text = re.sub(r'\|+', '', text)
        text = re.sub(r'\{+', '', text)
        text = re.sub(r'\}+', '', text)
        text = re.sub(r'\[+', '', text)
        text = re.sub(r'\]+', '', text)
        text = re.sub(r'<+', '', text)
        text = re.sub(r'>+', '', text)
        text = re.sub(r'=+', '', text)
        text = re.sub(r'\^+', '', text)
        text = re.sub(r'&+', '', text)
        text = re.sub(r'%+', '', text)
        text = re.sub(r'\$+', '', text)
        text = re.sub(r'@+', '', text)
        text = re.sub(r'\\+', '', text)
        text = re.sub(r'\/+', '', text)
        text = re.sub(r'\++', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def speak(self, text):
        """Speak text using TTS."""
        cleaned_text = self._clean_text_for_tts(text)
        self.tts_engine.speak(cleaned_text)


class AssistantThread(QThread):
    status_signal = pyqtSignal(str)
    chat_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, core):
        super().__init__()
        self.core = core
        self.running = True

    def run(self):
        self.status_signal.emit("System Online. Waiting for input...")

        while self.running:
            try:
                self.status_signal.emit("Listening...")
                audio = self.core.listen()

                if not audio:
                    continue

                self.status_signal.emit("Processing Audio...")
                text = self.core.transcribe(audio)

                if not text:
                    continue

                self.chat_signal.emit("user", text)

                if "goodbye" in text.lower() or "shutdown" in text.lower():
                    self.status_signal.emit("Shutting down...")
                    self.core.speak("Goodbye, sir.")
                    self.running = False
                    break

                self.status_signal.emit("Analyzing...")
                response = self.core.think(text)
                self.chat_signal.emit("raven", response)

                self.status_signal.emit("Speaking...")
                self.core.speak(response)

                self.status_signal.emit("Standing by...")

            except Exception as e:
                error_msg = f"Error in processing loop: {str(e)}"
                import traceback
                traceback.print_exc()
                self.status_signal.emit(f"Error in processing loop: {str(e)}")
                self.chat_signal.emit("system", error_msg)
                time.sleep(1)

    def stop(self):
        self.running = False


class ArcReactorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.color = QColor(0, 255, 255)
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_timer.start(50)
        self.pulse_value = 0
        self.pulse_direction = 1
        self.state = "idle"

    def set_state(self, state):
        self.state = state
        self.update()

    def update_pulse(self):
        self.pulse_value += self.pulse_direction * 2
        if self.pulse_value > 50:
            self.pulse_direction = -1
        elif self.pulse_value < 0:
            self.pulse_direction = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPointF(self.rect().center())
        radius = min(self.width(), self.height()) / 2 - 20

        if self.state == "listening":
            base_color = QColor(0, 255, 100)
            pulse_speed = 5
        elif self.state == "speaking":
            base_color = QColor(0, 100, 255)
            pulse_speed = 8
        elif self.state == "processing":
            base_color = QColor(255, 100, 0)
            pulse_speed = 2
        else:
            base_color = QColor(0, 255, 255)
            pulse_speed = 1

        glow_alpha = 100 + self.pulse_value * 2
        glow_color = QColor(base_color)
        glow_color.setAlpha(min(255, max(0, glow_alpha)))

        pen = QPen(base_color)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, glow_color)
        gradient.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)

        painter.setBrush(base_color)
        core_radius = radius * 0.3
        painter.drawEllipse(center, core_radius, core_radius)


class RavenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("R A V E N")
        self.resize(500, 700)

        self.setStyleSheet("""
            QMainWindow { 
                background-color: #0d0d0d; 
            }
            QLabel { color: #00FFFF; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
            QTextEdit { 
                background-color: #151515; 
                color: #00E0E0; 
                border: 1px solid #004444; 
                border-radius: 8px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton {
                background-color: #002222;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover { 
                background-color: #004444; 
                border-color: #FFFFFF;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #006666;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.reactor = ArcReactorWidget()
        layout.addWidget(self.reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("INITIALIZING...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; letter-spacing: 3px; color: #00FFFF;"
        )
        layout.addWidget(self.status_label)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        self.toggle_btn = QPushButton("INITIATE PROTOCOL")
        self.toggle_btn.clicked.connect(self.toggle_assistant)
        layout.addWidget(self.toggle_btn)

        self.core = None
        self.thread = None
        self.is_running = False

        QTimer.singleShot(100, self.init_core)

    def init_core(self):
        try:
            self.core = RavenCore(parent_window=self)
            self.status_label.setText("SYSTEM READY")
            self.log("System initialized. Press INITIATE to begin.")
        except Exception as e:
            self.status_label.setText("INIT FAILED")
            self.log(f"Critical Error: {e}")
            self.log("Ensure Ollama is running and requirements are installed.")

    def toggle_assistant(self):
        if not self.core:
            return

        if self.is_running:
            self.stop_assistant()
        else:
            self.start_assistant()

    def start_assistant(self):
        self.is_running = True
        self.toggle_btn.setText("TERMINATE PROTOCOL")
        self.thread = AssistantThread(self.core)
        self.thread.status_signal.connect(self.update_status)
        self.thread.chat_signal.connect(self.add_chat)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def stop_assistant(self):
        if self.thread:
            self.thread.stop()
            self.thread.wait()
        self.is_running = False
        self.toggle_btn.setText("INITIATE PROTOCOL")
        self.update_status("System Standby")
        self.reactor.set_state("idle")

    def update_status(self, text):
        self.status_label.setText(text.upper())
        state_map = {
            "Listening...": "listening",
            "Speaking...": "speaking",
            "Analyzing...": "processing",
            "Processing Audio...": "processing",
        }
        self.reactor.set_state(state_map.get(text, "idle"))

    def moveEvent(self, event):
        """Handle window move events to reposition camera overlay"""
        super().moveEvent(event)
        if self.core and self.core.camera_manager.is_overlay_open():
            self.core.camera_manager.position_overlay(self)

    def add_chat(self, role, text):
        if role == "user":
            color = "#AAAAAA"
            prefix = "USER"
        else:
            color = "#00FFFF"
            prefix = "RAVEN"

        self.chat_log.append(
            f'<span style="color:{color}"><b>{prefix}:</b> {text}</span><br>'
        )
        sb = self.chat_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def log(self, text):
        self.chat_log.append(f'<span style="color:#555"><i>{text}</i></span>')

    def on_thread_finished(self):
        self.is_running = False
        self.toggle_btn.setText("INITIATE PROTOCOL")
        self.reactor.set_state("idle")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RavenWindow()
    window.show()
    sys.exit(app.exec())
