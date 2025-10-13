"""Abstract interfaces for core components."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from uuid import UUID

from app.models.core import (
    ChildProfile, EmotionResult, EmotionState, StoryContext, 
    StorySegment, VoiceConfig, Session, SessionSummary,
    AdaptationAction, EmotionalGoal
)


class EmotionAnalyzerInterface(ABC):
    """Interface for emotion analysis components."""
    
    @abstractmethod
    async def analyze_audio(self, audio_stream: bytes) -> EmotionResult:
        """Analyze audio stream for emotional content."""
        pass
    
    @abstractmethod
    async def analyze_image(self, image_data: bytes) -> EmotionResult:
        """Analyze image for facial expressions and emotions."""
        pass
    
    @abstractmethod
    async def get_current_emotion(self, session_id: UUID) -> Optional[EmotionState]:
        """Get the current emotional state for a session."""
        pass
    
    @abstractmethod
    def validate_emotion_confidence(self, emotion: EmotionResult) -> bool:
        """Validate if emotion detection confidence is sufficient."""
        pass


class StoryGeneratorInterface(ABC):
    """Interface for story generation components."""
    
    @abstractmethod
    async def generate_initial_story(self, profile: ChildProfile, theme: str) -> StorySegment:
        """Generate the initial story segment."""
        pass
    
    @abstractmethod
    async def adapt_story_segment(
        self, 
        current_context: StoryContext, 
        emotion: EmotionState, 
        goal: EmotionalGoal
    ) -> StorySegment:
        """Adapt story based on current emotion and goal."""
        pass
    
    @abstractmethod
    async def generate_story_conclusion(self, story_context: StoryContext) -> StorySegment:
        """Generate an appropriate story conclusion."""
        pass
    
    @abstractmethod
    def validate_content_appropriateness(self, content: str, age: int) -> bool:
        """Validate that content is appropriate for the target age."""
        pass


class VoiceNarratorInterface(ABC):
    """Interface for voice narration components."""
    
    @abstractmethod
    async def narrate_segment(self, text: str, voice_config: VoiceConfig) -> bytes:
        """Convert text to speech with specified voice configuration."""
        pass
    
    @abstractmethod
    async def adjust_voice_for_emotion(
        self, 
        base_config: VoiceConfig, 
        emotion: EmotionState
    ) -> VoiceConfig:
        """Adjust voice configuration based on detected emotion."""
        pass
    
    @abstractmethod
    def create_character_voice(self, character_name: str, base_voice: str) -> VoiceConfig:
        """Create a distinct voice configuration for a character."""
        pass
    
    @abstractmethod
    async def stream_audio(self, audio_data: bytes) -> AsyncIterator[bytes]:
        """Stream audio data for real-time playback."""
        pass


class SessionManagerInterface(ABC):
    """Interface for session management components."""
    
    @abstractmethod
    async def create_session(self, child_profile: ChildProfile) -> Session:
        """Create a new storytelling session."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieve a session by ID."""
        pass
    
    @abstractmethod
    async def update_session_state(self, session_id: UUID, session: Session) -> None:
        """Update session state and context."""
        pass
    
    @abstractmethod
    async def cleanup_session_data(self, session_id: UUID) -> None:
        """Clean up session data for privacy compliance."""
        pass
    
    @abstractmethod
    async def get_user_preferences(self, anonymous_id: str) -> dict:
        """Get user preferences by anonymous ID."""
        pass
    
    @abstractmethod
    async def update_user_preferences(self, anonymous_id: str, preferences: dict) -> None:
        """Update user preferences."""
        pass


class StoryOrchestratorInterface(ABC):
    """Interface for the main story orchestration component."""
    
    @abstractmethod
    async def start_session(self, child_profile: ChildProfile) -> UUID:
        """Start a new storytelling session."""
        pass
    
    @abstractmethod
    async def process_emotion_update(
        self, 
        session_id: UUID, 
        emotion_data: EmotionResult
    ) -> AdaptationAction:
        """Process emotion update and determine adaptation action."""
        pass
    
    @abstractmethod
    async def generate_story_segment(
        self, 
        session_id: UUID, 
        context: StoryContext
    ) -> StorySegment:
        """Generate the next story segment."""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: UUID) -> SessionSummary:
        """End a storytelling session and return summary."""
        pass