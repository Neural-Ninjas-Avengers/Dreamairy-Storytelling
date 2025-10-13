"""FastAPI endpoints for the Adaptive Storytelling Agent."""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
import asyncio

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.models.core import (
    ChildProfile, EmotionalGoal, SessionState, EmotionType
)
from app.core.story_orchestrator import StoryOrchestrator
from app.utils.aws_validator import AWSValidator

logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = StoryOrchestrator()

# Create router
router = APIRouter()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request model for creating a new storytelling session."""
    age: int = Field(..., ge=3, le=12, description="Child's age in years")
    preferences: List[str] = Field(default=[], description="Story themes and preferences")
    emotional_goal: EmotionalGoal = Field(default=EmotionalGoal.ENTERTAIN)
    voice_preference: Optional[str] = Field(default=None, description="Preferred voice ID")


class SessionResponse(BaseModel):
    """Response model for session information."""
    session_id: str
    state: str
    child_age: int
    emotional_goal: str
    created_at: str
    message: str


class EmotionUpdateRequest(BaseModel):
    """Request model for emotion updates."""
    emotion_type: Optional[EmotionType] = Field(default=None)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    intensity: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class StorySegmentResponse(BaseModel):
    """Response model for story segments."""
    text: str
    emotional_tone: str
    pacing: str
    characters_involved: List[str]
    adaptation_reason: Optional[str]
    sequence_number: int
    illustration: Optional[Dict[str, Any]] = Field(default=None, description="Generated illustration data")


class SessionStatusResponse(BaseModel):
    """Response model for session status."""
    status: str
    session_info: Dict[str, Any]
    story_progress: Dict[str, Any]
    emotion_status: Dict[str, Any]
    audio_status: Dict[str, Any]


# Dependency for AWS validation
async def validate_aws_services():
    """Validate AWS services are available."""
    validator = AWSValidator()
    results = await validator.validate_all_services()
    
    if not any(results.values()):
        raise HTTPException(
            status_code=503,
            detail="AWS services are not available. Please check configuration."
        )
    
    return results


# Session Management Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    aws_status: Dict[str, bool] = Depends(validate_aws_services)
):
    """Create a new storytelling session."""
    
    try:
        # Create child profile
        child_profile = ChildProfile(
            age=request.age,
            preferences=request.preferences,
            emotional_goal=request.emotional_goal,
            voice_preference=request.voice_preference
        )
        
        # Start session through orchestrator
        session_id = await orchestrator.start_session(child_profile)
        
        # Get session details
        session = await orchestrator.session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=500, detail="Failed to retrieve created session")
        
        return SessionResponse(
            session_id=str(session_id),
            state=session.state.value,
            child_age=session.child_profile.age,
            emotional_goal=session.child_profile.emotional_goal.value,
            created_at=session.created_at.isoformat(),
            message="Session created successfully. Ready for storytelling!"
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """Get comprehensive status for a storytelling session."""
    
    try:
        session_uuid = UUID(session_id)
        status = await orchestrator.get_session_status(session_uuid)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Session not found")
        
        if status.get("status") == "error":
            raise HTTPException(status_code=500, detail=status.get("error", "Unknown error"))
        
        return SessionStatusResponse(**status)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End a storytelling session."""
    
    logger.info(f"Attempting to end session: {session_id}")
    
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
            logger.info(f"Session ID is valid UUID: {session_uuid}")
        except ValueError as uuid_error:
            logger.error(f"Invalid UUID format: {session_id} - {uuid_error}")
            raise HTTPException(status_code=400, detail=f"Invalid session ID format: {session_id}")
        
        # Try to end the session
        try:
            summary = await orchestrator.end_session(session_uuid)
            logger.info(f"Session ended successfully: {session_id}")
        except Exception as orchestrator_error:
            logger.error(f"Orchestrator error ending session {session_id}: {orchestrator_error}")
            # Return a simple success response even if orchestrator fails
            return {
                "message": "Session ended (with warnings)",
                "summary": {
                    "session_id": session_id,
                    "duration_minutes": 0.0,
                    "total_segments": 0,
                    "emotions_detected": [],
                    "adaptations_made": 0,
                    "engagement_score": None
                }
            }
        
        # Return successful summary
        return {
            "message": "Session ended successfully",
            "summary": {
                "session_id": str(summary.session_id),
                "duration_minutes": summary.duration_minutes,
                "total_segments": summary.total_segments,
                "emotions_detected": [emotion.value for emotion in summary.emotions_detected],
                "adaptations_made": summary.adaptations_made,
                "engagement_score": summary.engagement_score
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error ending session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


# Story Generation Endpoints
@router.post("/sessions/{session_id}/story/start")
async def start_story(session_id: str, theme: str = "adventure"):
    """Start story generation for a session."""
    
    try:
        session_uuid = UUID(session_id)
        
        # Get session
        session = await orchestrator.session_manager.get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create initial story context
        from app.models.core import StoryContext
        story_context = StoryContext(
            session_id=session_uuid,
            theme=theme,
            target_age=session.child_profile.age
        )
        
        # Generate initial story segment
        segment = await orchestrator.generate_story_segment(session_uuid, story_context)
        
        return {
            "message": "Story started successfully",
            "segment": StorySegmentResponse(
                text=segment.text,
                emotional_tone=segment.emotional_tone,
                pacing=segment.pacing,
                characters_involved=segment.characters_involved,
                adaptation_reason=segment.adaptation_reason,
                sequence_number=segment.sequence_number,
                illustration=segment.illustration
            )
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to start story: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start story: {str(e)}")


@router.get("/sessions/{session_id}/story/current")
async def get_current_story_segment(session_id: str):
    """Get the current story segment for a session."""
    
    try:
        session_uuid = UUID(session_id)
        
        # Get session
        session = await orchestrator.session_manager.get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.story_context:
            raise HTTPException(status_code=404, detail="No story context found")
        
        return {
            "current_segment": session.story_context.current_segment,
            "theme": session.story_context.theme,
            "characters": [
                {
                    "name": char.name,
                    "description": char.description,
                    "personality_traits": char.personality_traits
                }
                for char in session.story_context.characters
            ],
            "setting": session.story_context.setting,
            "plot_points": session.story_context.plot_points
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get current story: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current story: {str(e)}")


# Emotion Detection Endpoints
@router.post("/sessions/{session_id}/emotion/audio")
async def process_audio_emotion(
    session_id: str,
    audio_file: UploadFile = File(..., description="Audio file for emotion detection")
):
    """Process audio input for emotion detection."""
    
    try:
        session_uuid = UUID(session_id)
        
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process emotion through orchestrator
        adaptation_action = await orchestrator.process_multimodal_input(
            session_uuid, audio_data=audio_data
        )
        
        if adaptation_action:
            return {
                "message": "Audio emotion processed successfully",
                "adaptation": {
                    "action_type": adaptation_action.action_type,
                    "reason": adaptation_action.reason,
                    "confidence": adaptation_action.confidence,
                    "parameters": adaptation_action.parameters
                }
            }
        else:
            return {
                "message": "Audio processed but no adaptation needed",
                "adaptation": None
            }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to process audio emotion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio emotion: {str(e)}")


@router.post("/sessions/{session_id}/emotion/image")
async def process_image_emotion(
    session_id: str,
    image_file: UploadFile = File(..., description="Image file for emotion detection")
):
    """Process image input for emotion detection."""
    
    try:
        session_uuid = UUID(session_id)
        
        # Validate image file
        if not image_file.content_type or not image_file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid image file format")
        
        # Read image data
        image_data = await image_file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Process emotion through orchestrator
        adaptation_action = await orchestrator.process_multimodal_input(
            session_uuid, image_data=image_data
        )
        
        if adaptation_action:
            return {
                "message": "Image emotion processed successfully",
                "adaptation": {
                    "action_type": adaptation_action.action_type,
                    "reason": adaptation_action.reason,
                    "confidence": adaptation_action.confidence,
                    "parameters": adaptation_action.parameters
                }
            }
        else:
            return {
                "message": "Image processed but no adaptation needed",
                "adaptation": None
            }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to process image emotion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image emotion: {str(e)}")


@router.post("/sessions/{session_id}/emotion/multimodal")
async def process_multimodal_emotion(
    session_id: str,
    audio_file: Optional[UploadFile] = File(None, description="Audio file for emotion detection"),
    image_file: Optional[UploadFile] = File(None, description="Image file for emotion detection")
):
    """Process both audio and image input for multimodal emotion detection."""
    
    try:
        session_uuid = UUID(session_id)
        
        if not audio_file and not image_file:
            raise HTTPException(status_code=400, detail="At least one input (audio or image) is required")
        
        audio_data = None
        image_data = None
        
        # Process audio if provided
        if audio_file:
            if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
                raise HTTPException(status_code=400, detail="Invalid audio file format")
            audio_data = await audio_file.read()
        
        # Process image if provided
        if image_file:
            if not image_file.content_type or not image_file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Invalid image file format")
            image_data = await image_file.read()
        
        # Process multimodal emotion through orchestrator
        adaptation_action = await orchestrator.process_multimodal_input(
            session_uuid, audio_data=audio_data, image_data=image_data
        )
        
        if adaptation_action:
            return {
                "message": "Multimodal emotion processed successfully",
                "adaptation": {
                    "action_type": adaptation_action.action_type,
                    "reason": adaptation_action.reason,
                    "confidence": adaptation_action.confidence,
                    "parameters": adaptation_action.parameters
                }
            }
        else:
            return {
                "message": "Multimodal input processed but no adaptation needed",
                "adaptation": None
            }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to process multimodal emotion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process multimodal emotion: {str(e)}")


# Audio Streaming Endpoints
@router.get("/sessions/{session_id}/audio/stream")
async def stream_audio(session_id: str):
    """Stream audio for a storytelling session."""
    
    try:
        session_uuid = UUID(session_id)
        
        # Verify session exists
        session = await orchestrator.session_manager.get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        async def audio_generator():
            try:
                async for chunk in orchestrator.get_audio_stream(session_uuid):
                    yield chunk
            except Exception as e:
                logger.error(f"Audio streaming error: {e}")
        
        return StreamingResponse(
            audio_generator(),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to stream audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stream audio: {str(e)}")


# System Information Endpoints
@router.get("/system/status")
async def get_system_status():
    """Get system status and health information."""
    
    try:
        # Get AWS service status
        validator = AWSValidator()
        aws_status = await validator.validate_all_services()
        
        # Get session statistics
        session_stats = await orchestrator.session_manager.get_session_statistics()
        
        return {
            "status": "healthy",
            "aws_services": aws_status,
            "session_statistics": session_stats,
            "components": {
                "emotion_analyzer": "active",
                "story_generator": "active", 
                "voice_narrator": "active",
                "session_manager": "active"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/system/voices")
async def get_available_voices():
    """Get list of available voices for narration."""
    
    try:
        voices = orchestrator.voice_narrator.get_available_voices()
        
        return {
            "voices": voices,
            "total_count": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get available voices: {str(e)}")


@router.get("/system/themes")
async def get_available_themes():
    """Get list of available story themes."""
    
    themes = [
        {
            "id": "animals",
            "name": "Animal Adventures",
            "description": "Stories featuring friendly animals and nature",
            "age_groups": ["3-5", "6-8", "9-12"]
        },
        {
            "id": "friendship",
            "name": "Friendship Tales",
            "description": "Stories about making friends and caring for others",
            "age_groups": ["3-5", "6-8", "9-12"]
        },
        {
            "id": "adventure",
            "name": "Adventure Quests",
            "description": "Exciting journeys and discoveries",
            "age_groups": ["6-8", "9-12"]
        },
        {
            "id": "magic",
            "name": "Magical Worlds",
            "description": "Enchanted places with magic and wonder",
            "age_groups": ["6-8", "9-12"]
        },
        {
            "id": "family",
            "name": "Family Stories",
            "description": "Heartwarming tales about family love",
            "age_groups": ["3-5", "6-8"]
        }
    ]
    
    return {
        "themes": themes,
        "total_count": len(themes)
    }


# Health Check Endpoint
@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    
    return {
        "status": "healthy",
        "service": "Adaptive Storytelling Agent",
        "version": "1.0.0"
    }