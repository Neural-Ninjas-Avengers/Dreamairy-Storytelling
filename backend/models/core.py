"""Core data models for the Adaptive Storytelling Agent."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EmotionalGoal(str, Enum):
    """Emotional goals for story adaptation."""
    CALM = "calm"
    ENTERTAIN = "entertain"
    STIMULATE_PLAY = "stimulate_play"


class EmotionType(str, Enum):
    """Types of emotions that can be detected."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    BOREDOM = "boredom"
    EXCITEMENT = "excitement"
    ANXIETY = "anxiety"
    CALM = "calm"


class EmotionSource(str, Enum):
    """Source of emotion detection."""
    AUDIO = "audio"
    VISUAL = "visual"
    COMBINED = "combined"


class ChildProfile(BaseModel):
    """Profile information for a child user."""
    age: int = Field(..., ge=3, le=12, description="Child's age in years")
    preferences: List[str] = Field(default_factory=list, description="Story themes and preferences")
    emotional_goal: EmotionalGoal = Field(default=EmotionalGoal.ENTERTAIN)
    voice_preference: Optional[str] = Field(default=None, description="Preferred voice for narration")
    anonymous_id: str = Field(default_factory=lambda: str(uuid4()), description="Anonymous identifier")


class EmotionState(BaseModel):
    """Current emotional state of the child."""
    primary_emotion: EmotionType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for emotion detection")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Intensity of the emotion")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: EmotionSource
    secondary_emotions: Optional[Dict[EmotionType, float]] = Field(default=None)


class Character(BaseModel):
    """Story character definition."""
    name: str
    description: str
    personality_traits: List[str] = Field(default_factory=list)
    voice_characteristics: Optional[Dict[str, Any]] = Field(default=None)


class StoryContext(BaseModel):
    """Context and state of the current story."""
    session_id: UUID
    current_segment: str = Field(default="", description="Current story text")
    characters: List[Character] = Field(default_factory=list)
    setting: str = Field(default="", description="Story setting description")
    plot_points: List[str] = Field(default_factory=list, description="Key plot points covered")
    emotional_arc: List[EmotionState] = Field(default_factory=list, description="Emotion history")
    theme: str = Field(default="adventure", description="Story theme")
    target_age: int = Field(..., ge=3, le=12)


class StorySegment(BaseModel):
    """A segment of the story with adaptation information."""
    text: str
    emotional_tone: str = Field(default="neutral")
    pacing: str = Field(default="normal", description="slow, normal, fast")
    characters_involved: List[str] = Field(default_factory=list)
    adaptation_reason: Optional[str] = Field(default=None, description="Why this adaptation was made")
    sequence_number: int = Field(default=0)
    illustration: Optional[Dict[str, Any]] = Field(default=None, description="Generated illustration data")


class VoiceConfig(BaseModel):
    """Configuration for voice synthesis."""
    voice_id: str = Field(default="Joanna")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=1.0, ge=0.1, le=1.0)
    emphasis: List[str] = Field(default_factory=list, description="Words to emphasize")
    emotional_tone: str = Field(default="neutral")


class SessionState(str, Enum):
    """States of a storytelling session."""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class Session(BaseModel):
    """Storytelling session information."""
    session_id: UUID = Field(default_factory=uuid4)
    child_profile: ChildProfile
    state: SessionState = Field(default=SessionState.CREATED)
    story_context: Optional[StoryContext] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    
    def update_state(self, new_state: SessionState) -> None:
        """Update session state with timestamp."""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        if new_state == SessionState.COMPLETED:
            self.ended_at = datetime.utcnow()


class EmotionResult(BaseModel):
    """Result from emotion detection analysis."""
    emotion_state: EmotionState
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw detection data")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")


class AdaptationAction(BaseModel):
    """Action to take based on emotion detection."""
    action_type: str = Field(..., description="Type of adaptation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(..., description="Reason for this adaptation")
    confidence: float = Field(..., ge=0.0, le=1.0)


class SessionSummary(BaseModel):
    """Summary of a completed storytelling session."""
    session_id: UUID
    duration_minutes: float
    total_segments: int
    emotions_detected: List[EmotionType]
    adaptations_made: int
    engagement_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)