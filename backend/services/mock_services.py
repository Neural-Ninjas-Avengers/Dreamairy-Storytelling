"""Mock AWS services for local testing without incurring costs."""

import logging
import asyncio
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class MockBedrockClient:
    """Mock Bedrock client that generates stories locally without AWS costs."""
    
    def __init__(self):
        self.story_templates = {
            "animals": [
                "Once upon a time, in a magical forest, there lived a friendly little rabbit named Luna. Luna had the softest white fur and the brightest blue eyes you've ever seen. Every morning, she would hop through the forest looking for new friends to play with.",
                "In a cozy meadow surrounded by tall oak trees, there lived a wise old owl named Oliver. Oliver wore tiny round glasses and always had the best stories to tell. One sunny day, a curious little fox came to visit him.",
                "Deep in the enchanted woods, a gentle bear named Bruno was preparing for a very special day. Bruno loved to help other animals and today he was planning the biggest picnic the forest had ever seen!"
            ],
            "adventure": [
                "On a bright and sunny morning, Maya discovered a mysterious map hidden in her grandmother's attic. The map showed a path to a secret treasure island filled with wonderful surprises!",
                "Captain Leo and his crew of friendly pirates were sailing across the sparkling blue ocean when they spotted something amazing - a rainbow bridge leading to a floating castle in the clouds!",
                "In the heart of the Amazon jungle, young explorer Sam found an ancient temple covered in colorful vines. Inside, magical crystals glowed with warm, friendly light."
            ],
            "friendship": [
                "In the small town of Willowbrook, two best friends named Emma and Jake were planning the most amazing adventure. They had been friends since they were tiny, and they did everything together.",
                "At Sunshine Elementary School, a new student named Maria was feeling nervous on her first day. But soon she met kind-hearted Sophie, who showed her that making friends could be the best adventure of all.",
                "In the neighborhood park, a group of children from different countries discovered that even though they spoke different languages, they could still be the very best of friends."
            ]
        }
        
        self.continuation_templates = [
            "And then, something wonderful happened! {character} discovered that {discovery}, which made everyone smile with joy.",
            "Suddenly, a new friend appeared! It was {new_character}, who had been looking for someone just like {character} to share an amazing adventure.",
            "As they continued their journey, {character} learned an important lesson about {lesson}, and felt proud and happy.",
            "The magical moment arrived when {character} realized that {realization}, and everything became clear and beautiful."
        ]
        
        self.adaptation_responses = {
            "boredom": [
                "But wait! Suddenly, a colorful butterfly with sparkling wings appeared and whispered, 'Follow me to the most amazing secret I know!'",
                "Just then, {character} heard a mysterious sound coming from behind the old oak tree. What could it be? Let's find out together!",
                "Suddenly, the ground began to shimmer and glow, revealing a hidden door that led to the most wonderful place imaginable!"
            ],
            "fear": [
                "Don't worry, {character}! Just then, a gentle and wise {protector} appeared with a warm smile and said, 'I'm here to help you, and everything will be perfectly safe.'",
                "The scary thing turned out to be something wonderful! It was actually a friendly {friendly_character} who just wanted to play and be friends.",
                "A soft, golden light surrounded {character}, making them feel safe and protected. The wise old {guardian} was watching over them with love."
            ],
            "excitement": [
                "The adventure continued with even more amazing discoveries! {character} found {discovery} and felt so happy and excited!",
                "What an incredible moment! {character} and their friends celebrated by {celebration}, laughing and having the most wonderful time together!"
            ]
        }
    
    async def generate_story(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate a story using local templates."""
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Detect story type from prompt
        story_type = "animals"  # default
        if "adventure" in prompt.lower():
            story_type = "adventure"
        elif "friend" in prompt.lower():
            story_type = "friendship"
        
        # Detect if this is an adaptation
        adaptation_type = None
        if "bored" in prompt.lower() or "boring" in prompt.lower():
            adaptation_type = "boredom"
        elif "scared" in prompt.lower() or "afraid" in prompt.lower():
            adaptation_type = "fear"
        elif "excited" in prompt.lower() or "happy" in prompt.lower():
            adaptation_type = "excitement"
        
        # Generate appropriate response
        if adaptation_type and adaptation_type in self.adaptation_responses:
            templates = self.adaptation_responses[adaptation_type]
            story = random.choice(templates)
            
            # Replace placeholders
            story = story.replace("{character}", "our brave friend")
            story = story.replace("{protector}", "guardian angel")
            story = story.replace("{friendly_character}", "magical unicorn")
            story = story.replace("{guardian}", "fairy godmother")
            story = story.replace("{discovery}", "a treasure chest full of golden stars")
            story = story.replace("{celebration}", "dancing under the rainbow")
            
        elif "continue" in prompt.lower() or "next" in prompt.lower():
            # Generate continuation
            template = random.choice(self.continuation_templates)
            story = template.replace("{character}", "our hero")
            story = story.replace("{discovery}", "friendship is the greatest treasure")
            story = story.replace("{new_character}", "a wise talking owl")
            story = story.replace("{lesson}", "kindness and courage")
            story = story.replace("{realization}", "they had the power to help others all along")
        else:
            # Generate initial story
            story = random.choice(self.story_templates[story_type])
        
        logger.info(f"Generated mock story: {story[:50]}...")
        return story

    def __init__(self):
        self.mock_transcripts = [
            "I'm having so much fun with this story!",
            "This is really exciting, what happens next?",
            "I love the characters in this story.",
            "Can we hear more about the adventure?",
            "That was a little scary, but I'm okay now.",
            "I'm getting a bit tired of this part.",
            "Wow, that's amazing! Tell me more!",
            "I want to know what the character does next."
        ]
    
    async def start_streaming_transcription(self, audio_stream: bytes, language_code: str = "en-US") -> Dict[str, Any]:
        """Mock transcription that returns realistic results."""
        
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Return mock transcription
        transcript = random.choice(self.mock_transcripts)
        confidence = random.uniform(0.7, 0.95)
        
        return {
            "TranscriptEvent": {
                "Transcript": {
                    "Results": [
                        {
                            "Alternatives": [
                                {
                                    "Transcript": transcript,
                                    "Confidence": confidence
                                }
                            ],
                            "IsPartial": False
                        }
                    ]
                }
            }
        }
    
    async def analyze_audio_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Mock sentiment analysis based on keywords."""
        
        # Simple keyword-based sentiment
        positive_words = ["fun", "exciting", "love", "amazing", "wow", "great"]
        negative_words = ["scary", "tired", "boring", "sad", "afraid"]
        
        transcript_lower = transcript.lower()
        
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            confidence = min(0.9, 0.6 + positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            confidence = min(0.9, 0.6 + negative_count * 0.1)
        else:
            sentiment = "NEUTRAL"
            confidence = 0.7
        
        return {
            "Sentiment": sentiment,
            "SentimentScore": {
                "Positive": positive_count / max(1, positive_count + negative_count + 1),
                "Negative": negative_count / max(1, positive_count + negative_count + 1),
                "Neutral": 1 / max(1, positive_count + negative_count + 1)
            },
            "Confidence": confidence
        }

class MockRekognitionClient:
    """Mock Rekognition client for local image emotion detection."""
    
    def __init__(self):
        self.emotion_responses = [
            {"Type": "HAPPY", "Confidence": 85.5},
            {"Type": "CALM", "Confidence": 78.2},
            {"Type": "SURPRISED", "Confidence": 72.8},
            {"Type": "SAD", "Confidence": 68.9},
            {"Type": "CONFUSED", "Confidence": 65.4},
            {"Type": "ANGRY", "Confidence": 45.2}
        ]
    
    async def detect_faces_and_emotions(self, image_bytes: bytes) -> Dict[str, Any]:
        """Mock face and emotion detection."""
        
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.5, 1.2))
        
        # Generate realistic mock response
        primary_emotion = random.choice(self.emotion_responses)
        
        # Create a realistic distribution of emotions
        emotions = [primary_emotion]
        for emotion in self.emotion_responses:
            if emotion != primary_emotion:
                # Add other emotions with lower confidence
                confidence = random.uniform(10, 40)
                emotions.append({"Type": emotion["Type"], "Confidence": confidence})
        
        return {
            "FaceDetails": [
                {
                    "BoundingBox": {
                        "Width": 0.3,
                        "Height": 0.4,
                        "Left": 0.35,
                        "Top": 0.2
                    },
                    "Confidence": 99.5,
                    "Emotions": emotions,
                    "Smile": {
                        "Value": primary_emotion["Type"] == "HAPPY",
                        "Confidence": 85.0 if primary_emotion["Type"] == "HAPPY" else 25.0
                    },
                    "EyesOpen": {
                        "Value": True,
                        "Confidence": 95.0
                    },
                    "MouthOpen": {
                        "Value": primary_emotion["Type"] in ["SURPRISED", "HAPPY"],
                        "Confidence": 80.0
                    },
                    "Pose": {
                        "Roll": random.uniform(-5, 5),
                        "Yaw": random.uniform(-10, 10),
                        "Pitch": random.uniform(-5, 5)
                    }
                }
            ]
        }

class MockPollyClient:
    """Mock Polly client for local text-to-speech simulation."""
    
    def __init__(self):
        # Generate a small silent audio file as placeholder
        self.silent_audio = self._generate_silent_audio()
    
    def _generate_silent_audio(self) -> bytes:
        """Generate a small silent MP3-like audio file."""
        # This is a minimal MP3 header + silence
        # In a real implementation, you could use a TTS library like pyttsx3
        return b'\xff\xfb\x90\x00' + b'\x00' * 1000  # Minimal MP3-like structure
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        output_format: str = "mp3",
        sample_rate: str = "22050"
    ) -> bytes:
        """Mock speech synthesis."""
        
        # Simulate processing time based on text length
        processing_time = len(text) * 0.01  # 10ms per character
        await asyncio.sleep(min(processing_time, 2.0))  # Max 2 seconds
        
        logger.info(f"Mock TTS: '{text[:50]}...' with voice {voice_id}")
        
        # Return silent audio (in production, could use local TTS)
        return self.silent_audio
    
    async def list_available_voices(self, language_code: str = "en-US") -> List[Dict[str, Any]]:
        """Mock voice listing."""
        
        return [
            {"Id": "Joanna", "Name": "Joanna", "Gender": "Female", "LanguageCode": "en-US"},
            {"Id": "Matthew", "Name": "Matthew", "Gender": "Male", "LanguageCode": "en-US"},
            {"Id": "Salli", "Name": "Salli", "Gender": "Female", "LanguageCode": "en-US"},
            {"Id": "Joey", "Name": "Joey", "Gender": "Male", "LanguageCode": "en-US"},
            {"Id": "Kendra", "Name": "Kendra", "Gender": "Female", "LanguageCode": "en-US"}
        ]

class MockS3Client:
    """Mock S3 client for local preference storage."""
    
    def __init__(self):
        self.local_storage: Dict[str, Any] = {}
    
    async def store_user_preferences(self, anonymous_id: str, preferences: Dict[str, Any]) -> bool:
        """Store preferences in local memory."""
        
        self.local_storage[f"preferences/{anonymous_id}"] = preferences
        logger.info(f"Stored preferences for user {anonymous_id}")
        return True
    
    async def get_user_preferences(self, anonymous_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve preferences from local memory."""
        
        key = f"preferences/{anonymous_id}"
        preferences = self.local_storage.get(key)
        
        if preferences:
            logger.info(f"Retrieved preferences for user {anonymous_id}")
        
        return preferences
    
    async def store_story_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Store story template locally."""
        
        self.local_storage[f"templates/{template_id}"] = template_data
        return True
    
    async def get_story_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve story template locally."""
        
        return self.local_storage.get(f"templates/{template_id}")
    
    async def delete_user_data(self, anonymous_id: str) -> bool:
        """Delete user data locally."""
        
        keys_to_delete = [key for key in self.local_storage.keys() if anonymous_id in key]
        for key in keys_to_delete:
            del self.local_storage[key]
        
        logger.info(f"Deleted data for user {anonymous_id}")
        return True

# Mock client instances - NO AWS COSTS!
mock_bedrock_client = MockBedrockClient()
mock_rekognition_client = MockRekognitionClient()
mock_polly_client = MockPollyClient()
mock_s3_client = MockS3Client()

def get_bedrock_client():
    """Get Bedrock client (mock or real based on config)."""
    from app.config import get_settings
    settings = get_settings()
    
    if settings.use_mock_services or settings.offline_mode:
        return mock_bedrock_client
    else:
        from app.services.aws_clients import bedrock_client
        return bedrock_client

    from app.config import get_settings
    settings = get_settings()
    
    if settings.use_mock_services or settings.offline_mode:
    else:

def get_rekognition_client():
    """Get Rekognition client (mock or real based on config)."""
    from app.config import get_settings
    settings = get_settings()
    
    if settings.use_mock_services or settings.offline_mode:
        return mock_rekognition_client
    else:
        from app.services.aws_clients import rekognition_client
        return rekognition_client

def get_polly_client():
    """Get Polly client (mock or real based on config)."""
    from app.config import get_settings
    settings = get_settings()
    
    if settings.use_mock_services or settings.offline_mode:
        return mock_polly_client
    else:
        from app.services.aws_clients import polly_client
        return polly_client

def get_s3_client():
    """Get S3 client (mock or real based on config)."""
    from app.config import get_settings
    settings = get_settings()
    
    if settings.use_mock_services or settings.offline_mode:
        return mock_s3_client
    else:
        from app.services.aws_clients import s3_client
        return s3_client