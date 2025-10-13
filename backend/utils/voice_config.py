"""Voice configuration utilities for Polly integration."""

import logging
from typing import Dict, Any, List, Optional
from app.models.core import VoiceConfig, EmotionType, Character

logger = logging.getLogger(__name__)


class VoiceConfigManager:
    """Manages voice configurations for different scenarios and emotions."""
    
    def __init__(self):
        # Base voice configurations for different age groups
        self.age_voice_mapping = {
            (3, 5): {
                "primary": "Joanna",
                "alternative": "Salli",
                "male": "Joey",
                "characteristics": {"speed": 0.9, "pitch": 1.1, "volume": 0.9}
            },
            (6, 8): {
                "primary": "Joanna", 
                "alternative": "Kimberly",
                "male": "Matthew",
                "characteristics": {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
            },
            (9, 12): {
                "primary": "Kendra",
                "alternative": "Joanna", 
                "male": "Matthew",
                "characteristics": {"speed": 1.1, "pitch": 0.95, "volume": 1.0}
            }
        }
        
        # Emotion-based voice modifications
        self.emotion_modifiers = {
            EmotionType.JOY: {"speed": 1.2, "pitch": 1.1, "volume": 1.1},
            EmotionType.EXCITEMENT: {"speed": 1.3, "pitch": 1.2, "volume": 1.2},
            EmotionType.CALM: {"speed": 0.8, "pitch": 0.9, "volume": 0.8},
            EmotionType.SADNESS: {"speed": 0.7, "pitch": 0.8, "volume": 0.7},
            EmotionType.FEAR: {"speed": 1.1, "pitch": 1.0, "volume": 0.9},
            EmotionType.ANGER: {"speed": 1.2, "pitch": 0.9, "volume": 1.1},
            EmotionType.SURPRISE: {"speed": 1.1, "pitch": 1.1, "volume": 1.0},
            EmotionType.NEUTRAL: {"speed": 1.0, "pitch": 1.0, "volume": 1.0},
            EmotionType.BOREDOM: {"speed": 0.9, "pitch": 0.95, "volume": 0.9},
            EmotionType.ANXIETY: {"speed": 1.1, "pitch": 1.05, "volume": 0.95}
        }
        
        # Character voice profiles
        self.character_voices = {
            "narrator": {"voice_id": "Joanna", "speed": 1.0, "pitch": 1.0},
            "wise_owl": {"voice_id": "Matthew", "speed": 0.9, "pitch": 0.9},
            "playful_rabbit": {"voice_id": "Joey", "speed": 1.2, "pitch": 1.1},
            "gentle_bear": {"voice_id": "Matthew", "speed": 0.8, "pitch": 0.8},
            "curious_fox": {"voice_id": "Salli", "speed": 1.1, "pitch": 1.05},
            "brave_lion": {"voice_id": "Matthew", "speed": 1.0, "pitch": 0.9},
            "kind_fairy": {"voice_id": "Joanna", "speed": 0.9, "pitch": 1.2},
            "funny_monkey": {"voice_id": "Joey", "speed": 1.3, "pitch": 1.1}
        }
    
    def get_base_voice_for_age(self, age: int, gender_preference: Optional[str] = None) -> str:
        """Get the appropriate base voice for a child's age."""
        for age_range, config in self.age_voice_mapping.items():
            if age_range[0] <= age <= age_range[1]:
                if gender_preference == "male":
                    return config["male"]
                elif gender_preference == "female":
                    return config["primary"]
                else:
                    return config["primary"]
        
        # Default fallback
        return "Joanna"
    
    def create_base_config(self, age: int, voice_preference: Optional[str] = None) -> VoiceConfig:
        """Create a base voice configuration for a child."""
        # Determine voice ID
        if voice_preference:
            voice_id = voice_preference
        else:
            voice_id = self.get_base_voice_for_age(age)
        
        # Get age-appropriate characteristics
        characteristics = {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
        for age_range, config in self.age_voice_mapping.items():
            if age_range[0] <= age <= age_range[1]:
                characteristics = config["characteristics"]
                break
        
        return VoiceConfig(
            voice_id=voice_id,
            speed=characteristics["speed"],
            pitch=characteristics["pitch"],
            volume=characteristics["volume"],
            emotional_tone="neutral"
        )
    
    def adapt_for_emotion(self, base_config: VoiceConfig, emotion: EmotionType, intensity: float = 1.0) -> VoiceConfig:
        """Adapt voice configuration based on detected emotion."""
        if emotion not in self.emotion_modifiers:
            return base_config
        
        modifiers = self.emotion_modifiers[emotion]
        
        # Apply intensity scaling
        speed_mod = 1.0 + (modifiers["speed"] - 1.0) * intensity
        pitch_mod = 1.0 + (modifiers["pitch"] - 1.0) * intensity
        volume_mod = 1.0 + (modifiers["volume"] - 1.0) * intensity
        
        # Combine with base configuration
        new_speed = base_config.speed * speed_mod
        new_pitch = base_config.pitch * pitch_mod
        new_volume = base_config.volume * volume_mod
        
        # Clamp values to reasonable ranges
        new_speed = max(0.5, min(2.0, new_speed))
        new_pitch = max(0.5, min(2.0, new_pitch))
        new_volume = max(0.1, min(1.0, new_volume))
        
        return VoiceConfig(
            voice_id=base_config.voice_id,
            speed=new_speed,
            pitch=new_pitch,
            volume=new_volume,
            emphasis=base_config.emphasis,
            emotional_tone=emotion.value
        )
    
    def create_character_voice(self, character: Character, base_config: VoiceConfig) -> VoiceConfig:
        """Create a distinct voice configuration for a story character."""
        character_key = self._get_character_key(character.name.lower())
        
        if character_key in self.character_voices:
            char_config = self.character_voices[character_key]
            
            return VoiceConfig(
                voice_id=char_config["voice_id"],
                speed=char_config["speed"],
                pitch=char_config["pitch"],
                volume=base_config.volume,  # Keep base volume
                emotional_tone=base_config.emotional_tone
            )
        else:
            # Create variation of base voice for unknown characters
            return self._create_character_variation(character, base_config)
    
    def _get_character_key(self, character_name: str) -> str:
        """Map character names to predefined voice profiles."""
        name_mappings = {
            "owl": "wise_owl",
            "rabbit": "playful_rabbit", 
            "bunny": "playful_rabbit",
            "bear": "gentle_bear",
            "fox": "curious_fox",
            "lion": "brave_lion",
            "fairy": "kind_fairy",
            "monkey": "funny_monkey",
            "narrator": "narrator"
        }
        
        for key, profile in name_mappings.items():
            if key in character_name:
                return profile
        
        return "narrator"  # Default
    
    def _create_character_variation(self, character: Character, base_config: VoiceConfig) -> VoiceConfig:
        """Create a voice variation for characters not in predefined profiles."""
        # Analyze character traits to determine voice characteristics
        traits = [trait.lower() for trait in character.personality_traits]
        
        speed_mod = 1.0
        pitch_mod = 1.0
        
        # Adjust based on personality traits
        if "energetic" in traits or "playful" in traits:
            speed_mod = 1.2
            pitch_mod = 1.1
        elif "calm" in traits or "wise" in traits:
            speed_mod = 0.9
            pitch_mod = 0.9
        elif "brave" in traits or "strong" in traits:
            pitch_mod = 0.8
        elif "gentle" in traits or "kind" in traits:
            speed_mod = 0.9
            pitch_mod = 1.05
        
        return VoiceConfig(
            voice_id=base_config.voice_id,
            speed=base_config.speed * speed_mod,
            pitch=base_config.pitch * pitch_mod,
            volume=base_config.volume,
            emotional_tone=base_config.emotional_tone
        )
    
    def create_ssml_prosody(self, config: VoiceConfig, text: str) -> str:
        """Create SSML with prosody tags based on voice configuration."""
        # Map numeric values to SSML prosody values
        speed_map = {
            (0.0, 0.7): "slow",
            (0.7, 0.9): "medium", 
            (0.9, 1.1): "medium",
            (1.1, 1.3): "fast",
            (1.3, 2.0): "fast"
        }
        
        pitch_map = {
            (0.0, 0.8): "low",
            (0.8, 1.2): "medium",
            (1.2, 2.0): "high"
        }
        
        volume_map = {
            (0.0, 0.4): "soft",
            (0.4, 0.8): "medium",
            (0.8, 1.0): "loud"
        }
        
        # Get SSML values
        rate = self._get_ssml_value(config.speed, speed_map, "medium")
        pitch = self._get_ssml_value(config.pitch, pitch_map, "medium")
        volume = self._get_ssml_value(config.volume, volume_map, "medium")
        
        # Handle emphasis
        if config.emphasis:
            emphasized_text = text
            for word in config.emphasis:
                emphasized_text = emphasized_text.replace(
                    word, f'<emphasis level="strong">{word}</emphasis>'
                )
            text = emphasized_text
        
        # Create SSML
        ssml = f'''<speak>
            <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
                {text}
            </prosody>
        </speak>'''
        
        return ssml
    
    def _get_ssml_value(self, numeric_value: float, value_map: Dict, default: str) -> str:
        """Convert numeric value to SSML prosody value."""
        for (min_val, max_val), ssml_val in value_map.items():
            if min_val <= numeric_value < max_val:
                return ssml_val
        return default
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices with their characteristics."""
        voices = []
        
        # Extract unique voices from all configurations
        all_voices = set()
        for config in self.age_voice_mapping.values():
            all_voices.add(config["primary"])
            all_voices.add(config["alternative"])
            all_voices.add(config["male"])
        
        for voice_id in all_voices:
            voices.append({
                "voice_id": voice_id,
                "language": "en-US",
                "gender": self._get_voice_gender(voice_id),
                "description": f"Neural voice suitable for storytelling"
            })
        
        return voices
    
    def _get_voice_gender(self, voice_id: str) -> str:
        """Determine gender of voice based on voice ID."""
        male_voices = ["Matthew", "Joey", "Justin", "Kevin"]
        if voice_id in male_voices:
            return "male"
        return "female"
    
    def validate_voice_config(self, config: VoiceConfig) -> bool:
        """Validate that voice configuration values are within acceptable ranges."""
        if not (0.5 <= config.speed <= 2.0):
            return False
        if not (0.5 <= config.pitch <= 2.0):
            return False
        if not (0.1 <= config.volume <= 1.0):
            return False
        return True