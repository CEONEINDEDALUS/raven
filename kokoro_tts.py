"""
Kokoro ONNX TTS implementation for Raven.

This module provides text-to-speech functionality using Kokoro ONNX models.
Models should be downloaded from the official Kokoro ONNX repository.
"""

import os
import numpy as np
import sounddevice as sd

try:
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("Kokoro ONNX not available. TTS will use fallback.")

class KokoroTTS:
    """
    Kokoro ONNX TTS implementation.
    
    This class provides TTS functionality using Kokoro ONNX models.
    Models should be downloaded from the official Kokoro ONNX repository.
    """
    
    def __init__(self, model_path=None, voices_path=None):
        """
        Initialize Kokoro TTS.
        
        Args:
            model_path: Path to the ONNX model file
            voices_path: Path to the voices file
        """
        self.model_path = model_path
        self.voices_path = voices_path
        self.sample_rate = 24000
        self.kokoro = None
        self.enabled = False
        
        if not KOKORO_AVAILABLE:
            print("Kokoro ONNX not available. TTS will use fallback.")
            return
            
        # Set default paths if not provided
        if not model_path:
            models_dir = os.path.join(os.path.dirname(__file__), "models")
            self.model_path = os.path.join(models_dir, "kokoro-v1.0.onnx")
            self.voices_path = os.path.join(models_dir, "voices-v1.0.bin")
        
        # Check if models exist
        if not os.path.exists(self.model_path):
            print(f"Model file not found: {self.model_path}")
            print("TTS will use fallback.")
            return
            
        if not os.path.exists(self.voices_path):
            print(f"Voices file not found: {self.voices_path}")
            print("TTS will use fallback.")
            return
            
        try:
            # Initialize Kokoro with the downloaded models
            self.kokoro = Kokoro(self.model_path, self.voices_path)
            self.enabled = True
            print(f"Kokoro TTS initialized with model: {self.model_path}")
            
        except Exception as e:
            print(f"Failed to initialize Kokoro TTS: {e}")
            print("TTS will use fallback.")
    
    def synthesize(self, text, voice="af_sky", speed=1.0, lang="en-us"):
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice to use (default: "af_sky")
            speed: Speech speed (default: 1.0)
            lang: Language (default: "en-us")
            
        Returns:
            numpy array of audio samples
        """
        if not self.enabled or not self.kokoro:
            return self._fallback_synthesis(text)
        
        try:
            # Generate speech using Kokoro
            samples, sample_rate = self.kokoro.create(text, voice=voice, speed=speed, lang=lang)
            return samples
            
        except Exception as e:
            print(f"Synthesis error: {e}")
            return self._fallback_synthesis(text)
    
    def _fallback_synthesis(self, text):
        """
        Fallback synthesis using simple tones.
        
        Args:
            text: Text to synthesize
            
        Returns:
            numpy array of audio samples
        """
        # Simple tone generation as fallback
        duration = min(len(text) * 0.1, 3.0)  # Max 3 seconds
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        audio = np.sin(frequency * t * 2 * np.pi) * 0.3
        
        # Apply envelope for more natural sound
        envelope = np.exp(-t * 2)
        audio *= envelope
        
        return audio
    
    def speak(self, text, voice="af_sky", speed=1.0):
        """
        Synthesize and play speech.
        
        Args:
            text: Text to speak
            voice: Voice to use (default: "af_sky")
            speed: Speech speed (default: 1.0)
        """
        try:
            audio = self.synthesize(text, voice=voice, speed=speed)
            sd.play(audio, self.sample_rate)
            sd.wait()
            print(f"RAVEN: {text}")
        except Exception as e:
            print(f"TTS playback error: {e}")
            print(f"RAVEN: {text}")

# Test function
def test_tts():
    """Test the TTS system."""
    tts = KokoroTTS()
    test_text = "Hello! This is Raven speaking with Kokoro TTS."
    tts.speak(test_text)

if __name__ == "__main__":
    test_tts()