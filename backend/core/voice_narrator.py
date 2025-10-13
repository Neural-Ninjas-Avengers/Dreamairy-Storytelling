"""Voice narration system using Amazon Polly with emotional adaptation."""

import logging
import asyncio
import io
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime

from app.core.interfaces import VoiceNarratorInterface
from app.models.core import VoiceConfig, EmotionState, Character, StorySegment
from app.services.aws_clients import polly_client
from app.utils.voice_config import VoiceConfigManager

logger = logging.getLogger(__name__)


class TextToSpeechEngine:
    """Core text-to-speech engine using Amazon Polly."""
    
    def __init__(self):
        self.voice_config_manager = VoiceConfigManager()
        self.cache = {}  # Simple audio cache for repeated phrases
        self.max_cache_size = 100
        
        # Common phrases that can be cached
        self.cacheable_phrases = [
            "Once upon a time",
            "The end",
            "What do you think happens next?",
            "And they lived happily ever after"
        ]
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_config: VoiceConfig,
        use_ssml: bool = True
    ) -> bytes:
        """Convert text to speech with specified voice configuration."""
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(text, voice_config)
            if cache_key in self.cache:
                logger.debug(f"Using cached audio for: {text[:50]}...")
                return self.cache[cache_key]
            
            # Prepare text for synthesis
            if use_ssml:
                ssml_text = self.voice_config_manager.create_ssml_prosody(voice_config, text)
                synthesis_text = ssml_text
                text_type = "ssml"
            else:
                synthesis_text = text
                text_type = "text"
            
            # Synthesize speech
            audio_data = await polly_client.synthesize_speech(
                text=synthesis_text,
                voice_id=voice_config.voice_id,
                output_format="mp3",
                sample_rate="22050"
            )
            
            # Cache if appropriate
            if self._should_cache(text):
                self._add_to_cache(cache_key, audio_data)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            # Return empty audio data on failure
            return b""
    
    async def synthesize_with_emotion(
        self,
        text: str,
        base_config: VoiceConfig,
        emotion: EmotionState
    ) -> bytes:
        """Synthesize speech adapted for specific emotion."""
        
        # Adapt voice configuration for emotion
        adapted_config = self.voice_config_manager.adapt_for_emotion(
            base_config, emotion.primary_emotion, emotion.intensity
        )
        
        return await self.synthesize_speech(text, adapted_config)
    
    async def synthesize_character_voice(
        self,
        text: str,
        character: Character,
        base_config: VoiceConfig
    ) -> bytes:
        """Synthesize speech with character-specific voice."""
        
        # Create character-specific voice configuration
        character_config = self.voice_config_manager.create_character_voice(
            character, base_config
        )
        
        return await self.synthesize_speech(text, character_config)
    
    def _generate_cache_key(self, text: str, config: VoiceConfig) -> str:
        """Generate cache key for audio data."""
        # Simple hash-like key based on text and key config parameters
        key_elements = [
            text.lower().strip(),
            config.voice_id,
            f"{config.speed:.1f}",
            f"{config.pitch:.1f}",
            config.emotional_tone
        ]
        return "|".join(key_elements)
    
    def _should_cache(self, text: str) -> bool:
        """Determine if text should be cached."""
        # Cache short, common phrases
        if len(text) < 100 and any(phrase in text for phrase in self.cacheable_phrases):
            return True
        return False
    
    def _add_to_cache(self, key: str, audio_data: bytes) -> None:
        """Add audio data to cache."""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = audio_data
    
    def clear_cache(self) -> None:
        """Clear the audio cache."""
        self.cache.clear()


class DialogueProcessor:
    """Processes story text to handle dialogue and character voices."""
    
    def __init__(self):
        self.dialogue_patterns = [
            r'"([^"]*)",?\s*said\s+([A-Z][a-z]+)',  # "Hello," said Alice
            r'([A-Z][a-z]+)\s+said,?\s*"([^"]*)"',  # Alice said, "Hello"
            r'"([^"]*)",?\s*([A-Z][a-z]+)\s+replied', # "Hello," Alice replied
            r'"([^"]*)",?\s*whispered\s+([A-Z][a-z]+)', # "Hello," whispered Alice
        ]
    
    def extract_dialogue_segments(self, text: str) -> List[Dict[str, Any]]:
        """Extract dialogue segments from story text."""
        import re
        
        segments = []
        current_pos = 0
        
        # Find all dialogue matches
        all_matches = []
        for pattern in self.dialogue_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'dialogue': match.group(1) if '"' in match.group(0)[:5] else match.group(2),
                    'speaker': match.group(2) if '"' in match.group(0)[:5] else match.group(1),
                    'full_match': match.group(0)
                })
        
        # Sort matches by position
        all_matches.sort(key=lambda x: x['start'])
        
        # Create segments
        for match in all_matches:
            # Add narrative before dialogue
            if current_pos < match['start']:
                narrative_text = text[current_pos:match['start']].strip()
                if narrative_text:
                    segments.append({
                        'type': 'narrative',
                        'text': narrative_text,
                        'speaker': 'narrator'
                    })
            
            # Add dialogue segment
            segments.append({
                'type': 'dialogue',
                'text': match['dialogue'],
                'speaker': match['speaker'],
                'full_text': match['full_match']
            })
            
            current_pos = match['end']
        
        # Add remaining narrative
        if current_pos < len(text):
            remaining_text = text[current_pos:].strip()
            if remaining_text:
                segments.append({
                    'type': 'narrative',
                    'text': remaining_text,
                    'speaker': 'narrator'
                })
        
        # If no dialogue found, treat entire text as narrative
        if not segments:
            segments.append({
                'type': 'narrative',
                'text': text,
                'speaker': 'narrator'
            })
        
        return segments
    
    def prepare_text_for_speech(self, text: str) -> str:
        """Prepare text for optimal speech synthesis."""
        
        # Add pauses for better pacing
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        
        # Handle ellipsis for dramatic pauses
        text = text.replace('...', '<break time="1s"/>')
        
        # Clean up extra spaces
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class AudioStreamManager:
    """Manages audio streaming and playback coordination."""
    
    def __init__(self):
        self.chunk_size = 4096  # Audio chunk size for streaming
        self.buffer_size = 8192  # Buffer size for smooth playback
    
    async def stream_audio_data(self, audio_data: bytes) -> AsyncIterator[bytes]:
        """Stream audio data in chunks for real-time playback."""
        
        try:
            audio_stream = io.BytesIO(audio_data)
            
            while True:
                chunk = audio_stream.read(self.chunk_size)
                if not chunk:
                    break
                
                yield chunk
                
                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Audio streaming failed: {e}")
    
    async def combine_audio_segments(self, audio_segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into a single stream."""
        
        try:
            combined_audio = io.BytesIO()
            
            for segment in audio_segments:
                if segment:  # Skip empty segments
                    combined_audio.write(segment)
            
            return combined_audio.getvalue()
            
        except Exception as e:
            logger.error(f"Audio combination failed: {e}")
            return b""
    
    def add_pause_between_segments(self, duration_ms: int = 500) -> bytes:
        """Generate silence for pauses between segments."""
        
        # Simple silence generation (in production, would generate proper audio silence)
        # For now, return empty bytes as placeholder
        return b""


class VoiceNarrator(VoiceNarratorInterface):
    """Main voice narrator that orchestrates text-to-speech with emotional adaptation."""
    
    def __init__(self):
        self.tts_engine = TextToSpeechEngine()
        self.dialogue_processor = DialogueProcessor()
        self.stream_manager = AudioStreamManager()
        self.voice_config_manager = VoiceConfigManager()
        
        # Session-specific configurations
        self.session_configs: Dict[str, VoiceConfig] = {}
        
    async def narrate_segment(
        self, 
        text: str, 
        voice_config: VoiceConfig,
        characters: Optional[List[Character]] = None
    ) -> bytes:
        """Convert story segment to speech with character voices."""
        
        try:
            # Process dialogue and narrative segments
            segments = self.dialogue_processor.extract_dialogue_segments(text)
            
            audio_segments = []
            
            for segment in segments:
                # Prepare text for speech
                prepared_text = self.dialogue_processor.prepare_text_for_speech(segment['text'])
                
                if segment['type'] == 'dialogue' and characters:
                    # Use character voice for dialogue
                    character = self._find_character(segment['speaker'], characters)
                    if character:
                        audio_data = await self.tts_engine.synthesize_character_voice(
                            prepared_text, character, voice_config
                        )
                    else:
                        # Fallback to narrator voice
                        audio_data = await self.tts_engine.synthesize_speech(
                            prepared_text, voice_config
                        )
                else:
                    # Use narrator voice for narrative
                    audio_data = await self.tts_engine.synthesize_speech(
                        prepared_text, voice_config
                    )
                
                if audio_data:
                    audio_segments.append(audio_data)
                    
                    # Add small pause between segments
                    if len(audio_segments) > 1:
                        pause = self.stream_manager.add_pause_between_segments(300)
                        if pause:
                            audio_segments.append(pause)
            
            # Combine all audio segments
            return await self.stream_manager.combine_audio_segments(audio_segments)
            
        except Exception as e:
            logger.error(f"Segment narration failed: {e}")
            return b""
    
    async def adjust_voice_for_emotion(
        self, 
        base_config: VoiceConfig, 
        emotion: EmotionState
    ) -> VoiceConfig:
        """Adjust voice configuration based on detected emotion."""
        
        return self.voice_config_manager.adapt_for_emotion(
            base_config, emotion.primary_emotion, emotion.intensity
        )
    
    def create_character_voice(
        self, 
        character_name: str, 
        base_voice: str
    ) -> VoiceConfig:
        """Create a distinct voice configuration for a character."""
        
        # Create a character object for voice generation
        character = Character(
            name=character_name,
            description=f"Story character: {character_name}",
            personality_traits=[]
        )
        
        base_config = VoiceConfig(voice_id=base_voice)
        
        return self.voice_config_manager.create_character_voice(character, base_config)
    
    async def stream_audio(self, audio_data: bytes) -> AsyncIterator[bytes]:
        """Stream audio data for real-time playback."""
        
        async for chunk in self.stream_manager.stream_audio_data(audio_data):
            yield chunk
    
    async def narrate_with_emotion_adaptation(
        self,
        story_segment: StorySegment,
        base_config: VoiceConfig,
        current_emotion: Optional[EmotionState] = None,
        characters: Optional[List[Character]] = None
    ) -> bytes:
        """Narrate a story segment with emotion-based voice adaptation."""
        
        try:
            # Adapt voice configuration if emotion is provided
            if current_emotion:
                adapted_config = await self.adjust_voice_for_emotion(base_config, current_emotion)
            else:
                adapted_config = base_config
            
            # Apply segment-specific voice characteristics
            segment_config = self._adapt_config_for_segment(adapted_config, story_segment)
            
            # Narrate the segment
            return await self.narrate_segment(
                story_segment.text, 
                segment_config, 
                characters
            )
            
        except Exception as e:
            logger.error(f"Emotion-adaptive narration failed: {e}")
            return b""
    
    def _find_character(self, speaker_name: str, characters: List[Character]) -> Optional[Character]:
        """Find character by name in the character list."""
        
        speaker_lower = speaker_name.lower()
        for character in characters:
            if character.name.lower() == speaker_lower:
                return character
        
        return None
    
    def _adapt_config_for_segment(
        self, 
        base_config: VoiceConfig, 
        segment: StorySegment
    ) -> VoiceConfig:
        """Adapt voice configuration based on segment characteristics."""
        
        # Create a copy of the base configuration
        adapted_config = VoiceConfig(
            voice_id=base_config.voice_id,
            speed=base_config.speed,
            pitch=base_config.pitch,
            volume=base_config.volume,
            emphasis=base_config.emphasis.copy() if base_config.emphasis else [],
            emotional_tone=segment.emotional_tone
        )
        
        # Adjust based on pacing
        if segment.pacing == "fast":
            adapted_config.speed = min(2.0, base_config.speed * 1.2)
        elif segment.pacing == "slow":
            adapted_config.speed = max(0.5, base_config.speed * 0.8)
        elif segment.pacing == "gentle":
            adapted_config.speed = max(0.5, base_config.speed * 0.9)
            adapted_config.volume = max(0.1, base_config.volume * 0.9)
        
        # Adjust based on emotional tone
        tone_adjustments = {
            "exciting": {"speed": 1.1, "pitch": 1.05, "volume": 1.0},
            "calming": {"speed": 0.9, "pitch": 0.95, "volume": 0.8},
            "mysterious": {"speed": 0.8, "pitch": 0.9, "volume": 0.7},
            "joyful": {"speed": 1.1, "pitch": 1.1, "volume": 1.0},
            "gentle": {"speed": 0.9, "pitch": 1.0, "volume": 0.8}
        }
        
        if segment.emotional_tone in tone_adjustments:
            adjustments = tone_adjustments[segment.emotional_tone]
            adapted_config.speed = max(0.5, min(2.0, base_config.speed * adjustments["speed"]))
            adapted_config.pitch = max(0.5, min(2.0, base_config.pitch * adjustments["pitch"]))
            adapted_config.volume = max(0.1, min(1.0, base_config.volume * adjustments["volume"]))
        
        return adapted_config
    
    def set_session_voice_config(self, session_id: str, config: VoiceConfig) -> None:
        """Set voice configuration for a specific session."""
        self.session_configs[session_id] = config
    
    def get_session_voice_config(self, session_id: str) -> Optional[VoiceConfig]:
        """Get voice configuration for a specific session."""
        return self.session_configs.get(session_id)
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session-specific voice data."""
        self.session_configs.pop(session_id, None)
    
    async def test_voice_configuration(self, config: VoiceConfig) -> bool:
        """Test if a voice configuration works properly."""
        
        try:
            test_text = "This is a test of the voice configuration."
            audio_data = await self.tts_engine.synthesize_speech(test_text, config)
            return len(audio_data) > 0
            
        except Exception as e:
            logger.error(f"Voice configuration test failed: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices with their characteristics."""
        return self.voice_config_manager.get_available_voices()


class AudioBuffer:
    """Manages audio buffering for smooth playback."""
    
    def __init__(self, buffer_size: int = 16384):
        self.buffer_size = buffer_size
        self.buffer = io.BytesIO()
        self.is_playing = False
        self.playback_position = 0
        
    def add_audio_data(self, audio_data: bytes) -> None:
        """Add audio data to the buffer."""
        current_pos = self.buffer.tell()
        self.buffer.seek(0, io.SEEK_END)
        self.buffer.write(audio_data)
        self.buffer.seek(current_pos)
    
    def get_next_chunk(self, chunk_size: int = 4096) -> Optional[bytes]:
        """Get the next chunk of audio data."""
        chunk = self.buffer.read(chunk_size)
        if chunk:
            self.playback_position += len(chunk)
            return chunk
        return None
    
    def has_data(self) -> bool:
        """Check if buffer has more data."""
        current_pos = self.buffer.tell()
        self.buffer.seek(0, io.SEEK_END)
        end_pos = self.buffer.tell()
        self.buffer.seek(current_pos)
        return current_pos < end_pos
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer = io.BytesIO()
        self.playback_position = 0


class RealTimeAudioStreamer:
    """Handles real-time audio streaming with buffering and pace control."""
    
    def __init__(self):
        self.session_buffers: Dict[str, AudioBuffer] = {}
        self.streaming_sessions: Dict[str, bool] = {}
        self.pace_controllers: Dict[str, 'PaceController'] = {}
    
    async def start_streaming_session(self, session_id: str) -> None:
        """Start a new streaming session."""
        self.session_buffers[session_id] = AudioBuffer()
        self.streaming_sessions[session_id] = True
        self.pace_controllers[session_id] = PaceController()
        
        logger.info(f"Started audio streaming session: {session_id}")
    
    async def add_audio_to_stream(self, session_id: str, audio_data: bytes) -> None:
        """Add audio data to the streaming session."""
        if session_id in self.session_buffers:
            self.session_buffers[session_id].add_audio_data(audio_data)
    
    async def stream_audio_chunks(
        self, 
        session_id: str, 
        chunk_size: int = 4096
    ) -> AsyncIterator[bytes]:
        """Stream audio chunks for real-time playback."""
        
        if session_id not in self.session_buffers:
            logger.warning(f"No streaming session found: {session_id}")
            return
        
        buffer = self.session_buffers[session_id]
        pace_controller = self.pace_controllers[session_id]
        
        try:
            while self.streaming_sessions.get(session_id, False):
                # Get next chunk from buffer
                chunk = buffer.get_next_chunk(chunk_size)
                
                if chunk:
                    # Apply pace control
                    delay = pace_controller.calculate_chunk_delay(len(chunk))
                    
                    yield chunk
                    
                    # Wait for appropriate playback timing
                    if delay > 0:
                        await asyncio.sleep(delay)
                else:
                    # No data available, wait briefly
                    await asyncio.sleep(0.01)
                    
                    # Check if we should stop streaming
                    if not buffer.has_data() and not self.streaming_sessions.get(session_id, False):
                        break
        
        except Exception as e:
            logger.error(f"Audio streaming error for session {session_id}: {e}")
        
        finally:
            logger.info(f"Audio streaming ended for session: {session_id}")
    
    async def adjust_streaming_pace(
        self, 
        session_id: str, 
        pace_multiplier: float
    ) -> None:
        """Adjust the streaming pace for dramatic effect."""
        
        if session_id in self.pace_controllers:
            self.pace_controllers[session_id].set_pace_multiplier(pace_multiplier)
            logger.debug(f"Adjusted pace for session {session_id}: {pace_multiplier}x")
    
    async def add_dramatic_pause(self, session_id: str, duration_seconds: float) -> None:
        """Add a dramatic pause to the audio stream."""
        
        if session_id in self.pace_controllers:
            pause_audio = self._generate_silence(duration_seconds)
            await self.add_audio_to_stream(session_id, pause_audio)
    
    def _generate_silence(self, duration_seconds: float) -> bytes:
        """Generate silence audio data."""
        # Placeholder for silence generation
        # In production, would generate proper audio silence
        silence_length = int(duration_seconds * 1000)  # Rough estimate
        return b'\x00' * silence_length
    
    async def stop_streaming_session(self, session_id: str) -> None:
        """Stop and clean up a streaming session."""
        
        self.streaming_sessions[session_id] = False
        
        # Clean up resources
        self.session_buffers.pop(session_id, None)
        self.pace_controllers.pop(session_id, None)
        
        logger.info(f"Stopped audio streaming session: {session_id}")
    
    def get_streaming_status(self, session_id: str) -> Dict[str, Any]:
        """Get status information for a streaming session."""
        
        if session_id not in self.session_buffers:
            return {"status": "not_found"}
        
        buffer = self.session_buffers[session_id]
        is_active = self.streaming_sessions.get(session_id, False)
        
        return {
            "status": "active" if is_active else "inactive",
            "buffer_position": buffer.playback_position,
            "has_buffered_data": buffer.has_data(),
            "is_playing": buffer.is_playing
        }


class PaceController:
    """Controls audio playback pace for dramatic effect."""
    
    def __init__(self):
        self.base_pace = 1.0  # Normal pace
        self.current_pace_multiplier = 1.0
        self.chunk_duration_ms = 100  # Base chunk duration in milliseconds
    
    def set_pace_multiplier(self, multiplier: float) -> None:
        """Set pace multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)."""
        self.current_pace_multiplier = max(0.1, min(3.0, multiplier))
    
    def calculate_chunk_delay(self, chunk_size_bytes: int) -> float:
        """Calculate delay between chunks based on pace settings."""
        
        # Estimate chunk duration based on size (rough approximation)
        estimated_duration_ms = (chunk_size_bytes / 1000) * self.chunk_duration_ms
        
        # Apply pace multiplier (slower pace = longer delay)
        adjusted_duration_ms = estimated_duration_ms / self.current_pace_multiplier
        
        # Convert to seconds
        return adjusted_duration_ms / 1000.0
    
    def get_pause_duration(self, pause_type: str) -> float:
        """Get duration for different types of pauses."""
        
        pause_durations = {
            "comma": 0.2,
            "period": 0.5,
            "paragraph": 1.0,
            "dramatic": 1.5,
            "chapter": 2.0
        }
        
        base_duration = pause_durations.get(pause_type, 0.5)
        
        # Adjust for current pace
        return base_duration / self.current_pace_multiplier


class AudioEffectsProcessor:
    """Processes audio for enhanced storytelling effects."""
    
    def __init__(self):
        self.effect_cache = {}
    
    async def add_echo_effect(self, audio_data: bytes, intensity: float = 0.3) -> bytes:
        """Add echo effect for magical or mysterious moments."""
        
        # Placeholder for echo effect
        # In production, would use audio processing library
        logger.debug(f"Adding echo effect with intensity {intensity}")
        return audio_data
    
    async def add_whisper_effect(self, audio_data: bytes) -> bytes:
        """Add whisper effect for secretive moments."""
        
        # Placeholder for whisper effect
        logger.debug("Adding whisper effect")
        return audio_data
    
    async def add_excitement_boost(self, audio_data: bytes, boost_level: float = 1.2) -> bytes:
        """Boost audio for exciting moments."""
        
        # Placeholder for excitement boost
        logger.debug(f"Adding excitement boost: {boost_level}x")
        return audio_data
    
    async def normalize_volume(self, audio_data: bytes, target_level: float = 0.8) -> bytes:
        """Normalize audio volume for consistent playback."""
        
        # Placeholder for volume normalization
        logger.debug(f"Normalizing volume to {target_level}")
        return audio_data


class AdaptiveAudioManager:
    """Manages adaptive audio features based on story context and emotions."""
    
    def __init__(self):
        self.streamer = RealTimeAudioStreamer()
        self.effects_processor = AudioEffectsProcessor()
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
    
    async def start_adaptive_session(
        self, 
        session_id: str, 
        base_voice_config: VoiceConfig
    ) -> None:
        """Start an adaptive audio session."""
        
        await self.streamer.start_streaming_session(session_id)
        
        self.session_contexts[session_id] = {
            "base_voice_config": base_voice_config,
            "current_pace": 1.0,
            "last_emotion": None,
            "story_intensity": 0.5
        }
    
    async def process_story_segment_audio(
        self,
        session_id: str,
        audio_data: bytes,
        segment: StorySegment,
        current_emotion: Optional[EmotionState] = None
    ) -> None:
        """Process and stream story segment audio with adaptive features."""
        
        try:
            # Apply emotion-based audio effects
            processed_audio = await self._apply_emotion_effects(
                audio_data, segment, current_emotion
            )
            
            # Apply story context effects
            processed_audio = await self._apply_story_context_effects(
                processed_audio, segment, session_id
            )
            
            # Add to stream
            await self.streamer.add_audio_to_stream(session_id, processed_audio)
            
            # Update session context
            self._update_session_context(session_id, segment, current_emotion)
            
        except Exception as e:
            logger.error(f"Audio processing failed for session {session_id}: {e}")
    
    async def _apply_emotion_effects(
        self,
        audio_data: bytes,
        segment: StorySegment,
        emotion: Optional[EmotionState]
    ) -> bytes:
        """Apply audio effects based on detected emotion."""
        
        if not emotion:
            return audio_data
        
        processed_audio = audio_data
        
        # Apply emotion-specific effects
        if emotion.primary_emotion.value == "excitement" and emotion.intensity > 0.7:
            processed_audio = await self.effects_processor.add_excitement_boost(
                processed_audio, 1.0 + emotion.intensity * 0.3
            )
        
        elif emotion.primary_emotion.value == "fear" and segment.emotional_tone == "mysterious":
            processed_audio = await self.effects_processor.add_echo_effect(
                processed_audio, emotion.intensity * 0.5
            )
        
        elif emotion.primary_emotion.value == "calm":
            processed_audio = await self.effects_processor.normalize_volume(
                processed_audio, 0.6
            )
        
        return processed_audio
    
    async def _apply_story_context_effects(
        self,
        audio_data: bytes,
        segment: StorySegment,
        session_id: str
    ) -> bytes:
        """Apply effects based on story context."""
        
        processed_audio = audio_data
        
        # Apply pacing effects
        if segment.pacing == "slow":
            await self.streamer.adjust_streaming_pace(session_id, 0.8)
        elif segment.pacing == "fast":
            await self.streamer.adjust_streaming_pace(session_id, 1.2)
        else:
            await self.streamer.adjust_streaming_pace(session_id, 1.0)
        
        # Add dramatic pauses for certain content
        if "..." in segment.text or segment.emotional_tone == "mysterious":
            await self.streamer.add_dramatic_pause(session_id, 0.8)
        
        return processed_audio
    
    def _update_session_context(
        self,
        session_id: str,
        segment: StorySegment,
        emotion: Optional[EmotionState]
    ) -> None:
        """Update session context with new information."""
        
        if session_id in self.session_contexts:
            context = self.session_contexts[session_id]
            
            # Update emotion tracking
            if emotion:
                context["last_emotion"] = emotion
            
            # Update story intensity based on segment
            if segment.emotional_tone in ["exciting", "dramatic"]:
                context["story_intensity"] = min(1.0, context["story_intensity"] + 0.1)
            elif segment.emotional_tone in ["calm", "gentle"]:
                context["story_intensity"] = max(0.0, context["story_intensity"] - 0.1)
    
    async def get_streaming_chunks(
        self, 
        session_id: str
    ) -> AsyncIterator[bytes]:
        """Get streaming audio chunks for a session."""
        
        async for chunk in self.streamer.stream_audio_chunks(session_id):
            yield chunk
    
    async def stop_adaptive_session(self, session_id: str) -> None:
        """Stop and clean up an adaptive audio session."""
        
        await self.streamer.stop_streaming_session(session_id)
        self.session_contexts.pop(session_id, None)
    
    def get_session_audio_status(self, session_id: str) -> Dict[str, Any]:
        """Get audio status for a session."""
        
        streaming_status = self.streamer.get_streaming_status(session_id)
        context = self.session_contexts.get(session_id, {})
        
        return {
            "streaming": streaming_status,
            "context": {
                "current_pace": context.get("current_pace", 1.0),
                "story_intensity": context.get("story_intensity", 0.5),
                "last_emotion": context.get("last_emotion")
            }
        }