"""Audio stream processing utilities for Transcribe integration."""

import io
import wave
import logging
from typing import Optional, Dict, Any, AsyncIterator
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Utilities for processing audio streams for emotion detection."""
    
    def __init__(self):
        self.sample_rate = 16000  # Standard sample rate for speech recognition
        self.chunk_size = 1024
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate that audio data is in a supported format."""
        try:
            # Try to read as WAV
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                # Check basic parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                
                # Validate parameters
                if channels not in [1, 2]:  # Mono or stereo
                    return False
                if sample_width not in [1, 2]:  # 8-bit or 16-bit
                    return False
                if framerate < 8000 or framerate > 48000:  # Reasonable range
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False
    
    def convert_to_mono(self, audio_data: bytes) -> bytes:
        """Convert stereo audio to mono."""
        try:
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                if wav_file.getnchannels() == 1:
                    return audio_data  # Already mono
                
                # Read stereo data
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                
                # Convert to numpy array
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                
                audio_array = np.frombuffer(frames, dtype=dtype)
                
                # Reshape to stereo (2 channels)
                stereo_array = audio_array.reshape(-1, 2)
                
                # Convert to mono by averaging channels
                mono_array = np.mean(stereo_array, axis=1).astype(dtype)
                
                # Create new WAV file
                output_io = io.BytesIO()
                with wave.open(output_io, 'wb') as output_wav:
                    output_wav.setnchannels(1)
                    output_wav.setsampwidth(sample_width)
                    output_wav.setframerate(framerate)
                    output_wav.writeframes(mono_array.tobytes())
                
                return output_io.getvalue()
                
        except Exception as e:
            logger.error(f"Mono conversion failed: {e}")
            return audio_data  # Return original on failure
    
    def resample_audio(self, audio_data: bytes, target_rate: int = 16000) -> bytes:
        """Resample audio to target sample rate."""
        try:
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                original_rate = wav_file.getframerate()
                
                if original_rate == target_rate:
                    return audio_data  # No resampling needed
                
                # For demo purposes, return original audio
                # In production, you'd use a library like librosa or scipy
                logger.info(f"Audio resampling from {original_rate}Hz to {target_rate}Hz (demo mode)")
                return audio_data
                
        except Exception as e:
            logger.error(f"Audio resampling failed: {e}")
            return audio_data
    
    def extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract basic audio features for emotion analysis."""
        try:
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                duration = wav_file.getnframes() / framerate
                
                # Convert to numpy array for analysis
                if sample_width == 1:
                    audio_array = np.frombuffer(frames, dtype=np.uint8)
                    audio_array = audio_array.astype(np.float32) / 128.0 - 1.0
                elif sample_width == 2:
                    audio_array = np.frombuffer(frames, dtype=np.int16)
                    audio_array = audio_array.astype(np.float32) / 32768.0
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                
                # Calculate basic features
                rms_energy = np.sqrt(np.mean(audio_array ** 2))
                zero_crossing_rate = np.mean(np.abs(np.diff(np.sign(audio_array)))) / 2
                
                # Estimate pitch (very basic)
                # In production, use more sophisticated pitch detection
                pitch_estimate = self._estimate_pitch(audio_array, framerate)
                
                return {
                    "duration": duration,
                    "rms_energy": float(rms_energy),
                    "zero_crossing_rate": float(zero_crossing_rate),
                    "pitch_estimate": pitch_estimate,
                    "sample_rate": framerate,
                    "channels": wav_file.getnchannels()
                }
                
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    def _estimate_pitch(self, audio_array: np.ndarray, sample_rate: int) -> float:
        """Basic pitch estimation using autocorrelation."""
        try:
            # Simple autocorrelation-based pitch detection
            correlation = np.correlate(audio_array, audio_array, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Find the first peak after the zero lag
            min_period = int(sample_rate / 800)  # 800 Hz max
            max_period = int(sample_rate / 80)   # 80 Hz min
            
            if len(correlation) > max_period:
                peak_idx = np.argmax(correlation[min_period:max_period]) + min_period
                if peak_idx > 0:
                    return sample_rate / peak_idx
            
            return 0.0  # No pitch detected
            
        except Exception:
            return 0.0
    
    async def chunk_audio_stream(self, audio_data: bytes, chunk_duration: float = 1.0) -> AsyncIterator[bytes]:
        """Split audio into chunks for streaming processing."""
        try:
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                framerate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                
                chunk_frames = int(framerate * chunk_duration)
                bytes_per_frame = sample_width * channels
                chunk_size = chunk_frames * bytes_per_frame
                
                # Read and yield chunks
                while True:
                    chunk_data = wav_file.readframes(chunk_frames)
                    if not chunk_data:
                        break
                    
                    # Create WAV chunk
                    chunk_io = io.BytesIO()
                    with wave.open(chunk_io, 'wb') as chunk_wav:
                        chunk_wav.setnchannels(channels)
                        chunk_wav.setsampwidth(sample_width)
                        chunk_wav.setframerate(framerate)
                        chunk_wav.writeframes(chunk_data)
                    
                    yield chunk_io.getvalue()
                    
        except Exception as e:
            logger.error(f"Audio chunking failed: {e}")
    
    def detect_speech_activity(self, audio_data: bytes, threshold: float = 0.01) -> bool:
        """Detect if audio contains speech activity."""
        try:
            features = self.extract_audio_features(audio_data)
            rms_energy = features.get("rms_energy", 0)
            
            # Simple energy-based voice activity detection
            return rms_energy > threshold
            
        except Exception as e:
            logger.error(f"Speech activity detection failed: {e}")
            return False