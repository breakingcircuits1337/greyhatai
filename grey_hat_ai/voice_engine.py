"""
Voice Engine for Grey Hat AI

This module provides speech-to-text and text-to-speech capabilities using:
- faster-whisper for local STT (privacy and speed)
- Eleven Labs API for high-quality TTS
- Voice Activity Detection for continuous listening
"""

import os
import io
import logging
import threading
import queue
import time
import wave
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import tempfile

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    import webrtcvad
except ImportError:
    webrtcvad = None

try:
    from elevenlabs import generate, set_api_key, voices, Voice
    from elevenlabs.api import History
except ImportError:
    generate = None
    set_api_key = None
    voices = None
    Voice = None
    History = None

logger = logging.getLogger(__name__)


@dataclass
class VoiceConfig:
    """Configuration for voice engine."""
    # STT Configuration
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    sample_rate: int = 16000
    chunk_duration: float = 0.5  # seconds
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive
    silence_threshold: float = 2.0  # seconds of silence before stopping
    
    # TTS Configuration
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
    elevenlabs_stability: float = 0.75
    elevenlabs_clarity: float = 0.75
    elevenlabs_style: float = 0.0
    
    # Audio settings
    audio_device: Optional[int] = None  # None = default device


class VoiceEngine:
    """
    Voice engine providing STT and TTS capabilities.
    
    Features:
    - Local STT using faster-whisper for privacy
    - High-quality TTS using Eleven Labs
    - Voice Activity Detection for continuous listening
    - Thread-safe operation for Streamlit integration
    """
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.whisper_model = None
        self.vad = None
        self.elevenlabs_configured = False
        
        # Audio recording state
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        
        # Callbacks
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_listening_start: Optional[Callable[[], None]] = None
        self.on_listening_stop: Optional[Callable[[], None]] = None
        
        # Audio cache for TTS
        self.tts_cache: Dict[str, bytes] = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize STT and VAD components."""
        try:
            # Initialize Whisper model
            if WhisperModel:
                logger.info(f"Loading Whisper model: {self.config.whisper_model_size}")
                self.whisper_model = WhisperModel(
                    self.config.whisper_model_size,
                    device="cpu",  # Use CPU for compatibility
                    compute_type="int8"  # Optimize for speed
                )
                logger.info("Whisper model loaded successfully")
            else:
                logger.warning("faster-whisper not available, STT disabled")
            
            # Initialize VAD
            if webrtcvad:
                self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)
                logger.info("Voice Activity Detection initialized")
            else:
                logger.warning("webrtcvad not available, VAD disabled")
                
        except Exception as e:
            logger.error(f"Error initializing voice components: {e}")
    
    def set_elevenlabs_api_key(self, api_key: str) -> bool:
        """
        Configure Eleven Labs API for TTS.
        
        Args:
            api_key: Eleven Labs API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not set_api_key:
            logger.error("elevenlabs package not available")
            return False
            
        try:
            set_api_key(api_key)
            self.elevenlabs_configured = True
            logger.info("Eleven Labs API configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to configure Eleven Labs API: {e}")
            return False
    
    def get_available_voices(self) -> Dict[str, str]:
        """
        Get available Eleven Labs voices.
        
        Returns:
            Dictionary mapping voice IDs to voice names
        """
        if not self.elevenlabs_configured or not voices:
            return {}
            
        try:
            voice_list = voices()
            return {voice.voice_id: voice.name for voice in voice_list}
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return {}
    
    def start_listening(self, callback: Callable[[str], None] = None):
        """
        Start continuous speech recognition.
        
        Args:
            callback: Function to call when speech is detected
        """
        if self.is_listening:
            logger.warning("Already listening")
            return
            
        if not self.whisper_model:
            logger.error("Whisper model not available")
            return
            
        if not sd or not np:
            logger.error("sounddevice or numpy not available")
            return
        
        if callback:
            self.on_speech_detected = callback
            
        self.is_listening = True
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        
        if self.on_listening_start:
            self.on_listening_start()
            
        logger.info("Started listening for speech")
    
    def stop_listening(self):
        """Stop continuous speech recognition."""
        if not self.is_listening:
            return
            
        self.is_listening = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
            
        if self.on_listening_stop:
            self.on_listening_stop()
            
        logger.info("Stopped listening for speech")
    
    def _recording_loop(self):
        """Main recording loop running in separate thread."""
        chunk_size = int(self.config.sample_rate * self.config.chunk_duration)
        audio_buffer = []
        silence_chunks = 0
        max_silence_chunks = int(self.config.silence_threshold / self.config.chunk_duration)
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            self.audio_queue.put(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=chunk_size,
                device=self.config.audio_device,
                callback=audio_callback
            ):
                while self.is_listening:
                    try:
                        # Get audio chunk
                        chunk = self.audio_queue.get(timeout=0.1)
                        
                        # Convert to int16 for VAD
                        chunk_int16 = (chunk * 32767).astype(np.int16)
                        
                        # Check for voice activity
                        is_speech = self._is_speech(chunk_int16.tobytes())
                        
                        if is_speech:
                            audio_buffer.append(chunk)
                            silence_chunks = 0
                        else:
                            silence_chunks += 1
                            if audio_buffer:  # Only add silence if we have speech
                                audio_buffer.append(chunk)
                        
                        # Process accumulated audio if we have enough silence
                        if audio_buffer and silence_chunks >= max_silence_chunks:
                            self._process_audio_buffer(audio_buffer)
                            audio_buffer = []
                            silence_chunks = 0
                            
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Error in recording loop: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
    
    def _is_speech(self, audio_bytes: bytes) -> bool:
        """Check if audio contains speech using VAD."""
        if not self.vad:
            return True  # Assume speech if VAD not available
            
        try:
            # VAD expects 10, 20, or 30ms frames at 8, 16, or 48 kHz
            frame_duration = 30  # ms
            frame_size = int(self.config.sample_rate * frame_duration / 1000)
            
            if len(audio_bytes) < frame_size * 2:  # 2 bytes per sample (int16)
                return False
                
            # Take first complete frame
            frame = audio_bytes[:frame_size * 2]
            return self.vad.is_speech(frame, self.config.sample_rate)
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return True  # Assume speech on error
    
    def _process_audio_buffer(self, audio_buffer):
        """Process accumulated audio buffer for speech recognition."""
        if not audio_buffer:
            return
            
        try:
            # Concatenate audio chunks
            audio_data = np.concatenate(audio_buffer)
            
            # Transcribe using Whisper
            text = self._transcribe_audio(audio_data)
            
            if text and text.strip() and self.on_speech_detected:
                self.on_speech_detected(text.strip())
                
        except Exception as e:
            logger.error(f"Error processing audio buffer: {e}")
    
    def _transcribe_audio(self, audio_data) -> str:
        """Transcribe audio data using Whisper."""
        if not self.whisper_model:
            return ""
            
        try:
            # Whisper expects float32 audio
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Transcribe
            segments, info = self.whisper_model.transcribe(
                audio_data,
                language="en",  # Can be made configurable
                task="transcribe",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_file(self, audio_file_path: str) -> str:
        """
        Transcribe an audio file.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self.whisper_model:
            logger.error("Whisper model not available")
            return ""
            
        try:
            segments, info = self.whisper_model.transcribe(
                audio_file_path,
                language="en",
                task="transcribe"
            )
            
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return ""
    
    def text_to_speech(self, text: str, voice_id: str = None) -> Optional[bytes]:
        """
        Convert text to speech using Eleven Labs.
        
        Args:
            text: Text to convert
            voice_id: Voice ID to use (optional, uses config default)
            
        Returns:
            Audio data as bytes, or None if failed
        """
        if not self.elevenlabs_configured or not generate:
            logger.error("Eleven Labs not configured or available")
            return None
            
        voice_id = voice_id or self.config.elevenlabs_voice_id
        
        # Check cache first
        cache_key = f"{voice_id}:{hash(text)}"
        if cache_key in self.tts_cache:
            return self.tts_cache[cache_key]
        
        try:
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings={
                        "stability": self.config.elevenlabs_stability,
                        "similarity_boost": self.config.elevenlabs_clarity,
                        "style": self.config.elevenlabs_style
                    }
                )
            )
            
            # Cache the result
            self.tts_cache[cache_key] = audio
            
            # Limit cache size
            if len(self.tts_cache) > 50:
                # Remove oldest entries
                oldest_keys = list(self.tts_cache.keys())[:10]
                for key in oldest_keys:
                    del self.tts_cache[key]
            
            return audio
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def play_audio(self, audio_data: bytes):
        """
        Play audio data.
        
        Args:
            audio_data: Audio data to play
        """
        if not sd or not np:
            logger.error("sounddevice or numpy not available")
            return
            
        try:
            # Save to temporary file and load with sounddevice
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                # Load and play
                data, fs = sd.read(tmp_file.name)
                sd.play(data, fs)
                sd.wait()  # Wait until playback is finished
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the voice engine."""
        return {
            "whisper_available": self.whisper_model is not None,
            "vad_available": self.vad is not None,
            "elevenlabs_configured": self.elevenlabs_configured,
            "is_listening": self.is_listening,
            "audio_available": sd is not None and np is not None,
            "config": {
                "whisper_model_size": self.config.whisper_model_size,
                "sample_rate": self.config.sample_rate,
                "voice_id": self.config.elevenlabs_voice_id
            }
        }

