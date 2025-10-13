"""Demo-specific endpoints for showcasing the Adaptive Storytelling Agent."""

import logging
import asyncio
import base64
import io
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from PIL import Image

from app.services.ai_image_service import ai_image_service

from app.models.core import ChildProfile, EmotionalGoal, EmotionType
from app.core.story_orchestrator import StoryOrchestrator

logger = logging.getLogger(__name__)

# Demo router
demo_router = APIRouter()

# Global orchestrator instance
orchestrator = StoryOrchestrator()


class DemoScenario(BaseModel):
    """Demo scenario configuration."""
    name: str
    description: str
    child_profile: Dict[str, Any]
    emotion_sequence: List[Dict[str, Any]]
    expected_adaptations: List[str]
    duration_minutes: int


class DemoMetrics(BaseModel):
    """Demo session metrics."""
    session_id: str
    scenario_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    total_segments: int
    emotions_processed: int
    adaptations_triggered: int
    engagement_score: float
    adaptation_accuracy: float
    response_times: List[float]


class ImageGenerationRequest(BaseModel):
    """Request for AI image generation."""
    story_context: str
    character_description: str
    scene_description: str
    style: str = "children_book"
    has_user_photo: bool = False


class ImageGenerationResponse(BaseModel):
    """Response for AI image generation."""
    image_url: str
    generation_time: float
    prompt_used: str
    style_applied: str


class AvatarGenerationRequest(BaseModel):
    """Request for avatar generation from user photo."""
    style: str = "children_book_avatar"


class AvatarGenerationResponse(BaseModel):
    """Response for avatar generation."""
    avatar_url: str
    generation_time: float
    style_applied: str


class AIImageGenerator:
    """Handles AI image generation with user photos."""
    
    def __init__(self):
        self.generated_images: Dict[str, str] = {}  # Cache for generated images
        self.user_photos: Dict[str, str] = {}  # Store user photos by session
    
    def store_user_photo(self, session_id: str, photo_data: str) -> bool:
        """Store user photo for character generation."""
        try:
            # Validate base64 image data
            image_data = base64.b64decode(photo_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Basic validation
            if image.size[0] < 100 or image.size[1] < 100:
                return False
            
            # Store the photo
            self.user_photos[session_id] = photo_data
            logger.info(f"Stored user photo for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing user photo: {e}")
            return False
    
    async def generate_story_image(self, session_id: str, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate AI image for story with optional user photo integration."""
        
        start_time = datetime.utcnow()
        
        try:
            # Build the prompt
            prompt = self._build_image_prompt(request, session_id)
            
            # Use real AI service
            image_url = await ai_image_service.generate_image(prompt, request.style)
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            if image_url:
                response = ImageGenerationResponse(
                    image_url=image_url,
                    generation_time=generation_time,
                    prompt_used=prompt,
                    style_applied=request.style
                )
                
                # Cache the generated image
                cache_key = f"{session_id}_{hash(prompt)}"
                self.generated_images[cache_key] = image_url
                
                return response
            else:
                raise Exception("AI service returned no image")
            
        except Exception as e:
            logger.error(f"Error generating story image: {e}")
            # Return fallback image
            return ImageGenerationResponse(
                image_url="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBmaWxsPSIjNjM2NkYxIi8+Cjx0ZXh0IHg9IjI1NiIgeT0iMjU2IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+8J+OqCBJbWFnZW4gZGUgQ3VlbnRvIPCfjonwn5qA8J+MnzwvdGV4dD4KPC9zdmc+",
                generation_time=0.1,
                prompt_used=request.story_context,
                style_applied="fallback"
            )
    
    def _build_image_prompt(self, request: ImageGenerationRequest, session_id: str) -> str:
        """Build AI image generation prompt."""
        
        base_prompt = f"{request.scene_description}"
        
        # Add character description
        if request.character_description:
            if request.has_user_photo and session_id in self.user_photos:
                base_prompt += f" featuring a child character that looks like the provided photo, {request.character_description}"
            else:
                base_prompt += f" featuring {request.character_description}"
        
        # Add style specifications
        style_prompts = {
            "children_book": "in a colorful children's book illustration style, warm and friendly, soft lighting",
            "watercolor": "in watercolor painting style, soft edges, gentle colors",
            "cartoon": "in cartoon animation style, bright colors, expressive characters",
            "realistic": "in realistic style with magical elements, detailed and immersive",
            "fantasy": "in fantasy art style, magical atmosphere, enchanting details"
        }
        
        style_addition = style_prompts.get(request.style, style_prompts["children_book"])
        base_prompt += f", {style_addition}"
        
        # Add safety and appropriateness filters
        base_prompt += ", safe for children, appropriate content, positive atmosphere"
        
        return base_prompt
    
    async def generate_avatar_from_photo(self, session_id: str, style: str = "children_book_avatar") -> AvatarGenerationResponse:
        """Generate avatar from user photo."""
        
        start_time = datetime.utcnow()
        
        try:
            # Build avatar prompt (we'll use a generic prompt since we can't process the actual photo yet)
            avatar_prompt = self._build_avatar_prompt(style)
            
            # Use real AI service
            avatar_url = await ai_image_service.generate_avatar(avatar_prompt, style)
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            if avatar_url:
                return AvatarGenerationResponse(
                    avatar_url=avatar_url,
                    generation_time=generation_time,
                    style_applied=style
                )
            else:
                raise Exception("AI service returned no avatar")
            
        except Exception as e:
            logger.error(f"Error generating avatar: {e}")
            # Return fallback avatar SVG
            fallback_avatar = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTI4IiBoZWlnaHQ9IjEyOCIgdmlld0JveD0iMCAwIDEyOCAxMjgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjY0IiBjeT0iNjQiIHI9IjY0IiBmaWxsPSIjRkY2QkI1Ii8+CjxjaXJjbGUgY3g9IjY0IiBjeT0iNTAiIHI9IjIwIiBmaWxsPSIjRkZGIi8+CjxjaXJjbGUgY3g9IjU2IiBjeT0iNDYiIHI9IjMiIGZpbGw9IiMzMzMiLz4KPGNpcmNsZSBjeD0iNzIiIGN5PSI0NiIgcj0iMyIgZmlsbD0iIzMzMyIvPgo8cGF0aCBkPSJNNTYgNTZRNjQgNjAgNzIgNTYiIHN0cm9rZT0iIzMzMyIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+Cjwvc3ZnPg=="
            
            return AvatarGenerationResponse(
                avatar_url=fallback_avatar,
                generation_time=0.1,
                style_applied="fallback"
            )
    
    def _build_avatar_prompt(self, style: str) -> str:
        """Build avatar generation prompt."""
        
        style_prompts = {
            "children_book_avatar": "cute child character avatar in children's book illustration style, friendly face, big eyes, colorful, cartoon-like, portrait view, magical and whimsical",
            "cartoon_avatar": "cartoon child avatar, animated style, bright colors, happy expression, portrait",
            "fantasy_avatar": "fantasy child character avatar, magical elements, sparkles, dreamy style, portrait",
            "watercolor_avatar": "watercolor child avatar, soft colors, artistic style, gentle expression, portrait"
        }
        
        base_prompt = style_prompts.get(style, style_prompts["children_book_avatar"])
        base_prompt += ", safe for children, appropriate content, positive expression, circular frame"
        
        return base_prompt
    
    async def _simulate_avatar_generation(self, style: str, session_id: str) -> str:
        """Simulate avatar generation (replace with actual AI service in production)."""
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.5, 3.0))
        
        # For demo, return different avatar styles
        avatar_styles = {
            "children_book_avatar": "/static/images/avatar_children_book.jpg",
            "cartoon_avatar": "/static/images/avatar_cartoon.jpg", 
            "fantasy_avatar": "/static/images/avatar_fantasy.jpg",
            "watercolor_avatar": "/static/images/avatar_watercolor.jpg"
        }
        
        return avatar_styles.get(style, "/static/images/avatar_children_book.jpg")

    async def _simulate_image_generation(self, prompt: str, style: str, session_id: str) -> str:
        """Simulate AI image generation (replace with actual AI service in production)."""
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(2.0, 4.0))
        
        # For demo, return different placeholder images based on content
        if "forest" in prompt.lower() or "tree" in prompt.lower():
            return "/static/images/demo_forest_scene.jpg"
        elif "ocean" in prompt.lower() or "sea" in prompt.lower():
            return "/static/images/demo_ocean_scene.jpg"
        elif "castle" in prompt.lower() or "palace" in prompt.lower():
            return "/static/images/demo_castle_scene.jpg"
        elif "animal" in prompt.lower():
            return "/static/images/demo_animals_scene.jpg"
        else:
            return "/static/images/demo_magical_scene.jpg"
    
    def get_user_photo(self, session_id: str) -> Optional[str]:
        """Get stored user photo for a session."""
        return self.user_photos.get(session_id)
    
    def clear_session_data(self, session_id: str):
        """Clear stored data for a session."""
        self.user_photos.pop(session_id, None)
        # Clear cached images for this session
        keys_to_remove = [key for key in self.generated_images.keys() if key.startswith(session_id)]
        for key in keys_to_remove:
            self.generated_images.pop(key, None)


class DemoManager:
    """Manages demo scenarios and metrics collection."""
    
    def __init__(self):
        self.demo_scenarios = self._initialize_demo_scenarios()
        self.active_demos: Dict[str, Dict[str, Any]] = {}
        self.demo_metrics: Dict[str, DemoMetrics] = {}
    
    def _initialize_demo_scenarios(self) -> Dict[str, DemoScenario]:
        """Initialize predefined demo scenarios."""
        
        scenarios = {
            "boredom_to_engagement": DemoScenario(
                name="Boredom to Engagement",
                description="Demonstrates how the system detects boredom and adapts to re-engage the child",
                child_profile={
                    "age": 6,
                    "preferences": ["animals", "adventure"],
                    "emotional_goal": "entertain"
                },
                emotion_sequence=[
                    {"emotion": "neutral", "confidence": 0.7, "delay": 5},
                    {"emotion": "boredom", "confidence": 0.8, "delay": 10},
                    {"emotion": "boredom", "confidence": 0.9, "delay": 5},
                    {"emotion": "surprise", "confidence": 0.8, "delay": 8},
                    {"emotion": "joy", "confidence": 0.9, "delay": 10}
                ],
                expected_adaptations=[
                    "introduce_surprise_character",
                    "add_interactive_element",
                    "create_mystery"
                ],
                duration_minutes=5
            ),
            
            "fear_to_comfort": DemoScenario(
                name="Fear to Comfort",
                description="Shows how the system detects fear and adapts to provide comfort and reassurance",
                child_profile={
                    "age": 4,
                    "preferences": ["friendship", "family"],
                    "emotional_goal": "calm"
                },
                emotion_sequence=[
                    {"emotion": "neutral", "confidence": 0.6, "delay": 3},
                    {"emotion": "fear", "confidence": 0.7, "delay": 8},
                    {"emotion": "anxiety", "confidence": 0.8, "delay": 5},
                    {"emotion": "calm", "confidence": 0.8, "delay": 10},
                    {"emotion": "joy", "confidence": 0.7, "delay": 8}
                ],
                expected_adaptations=[
                    "introduce_protective_character",
                    "transform_scary_to_friendly",
                    "add_comforting_dialogue"
                ],
                duration_minutes=4
            ),
            
            "excitement_management": DemoScenario(
                name="Excitement Management",
                description="Demonstrates managing high excitement levels when the goal is to calm down",
                child_profile={
                    "age": 8,
                    "preferences": ["magic", "adventure"],
                    "emotional_goal": "calm"
                },
                emotion_sequence=[
                    {"emotion": "excitement", "confidence": 0.9, "delay": 5},
                    {"emotion": "excitement", "confidence": 0.95, "delay": 5},
                    {"emotion": "joy", "confidence": 0.8, "delay": 8},
                    {"emotion": "calm", "confidence": 0.8, "delay": 10},
                    {"emotion": "calm", "confidence": 0.9, "delay": 7}
                ],
                expected_adaptations=[
                    "gradually_slow_pace",
                    "introduce_calming_activity",
                    "shift_to_peaceful_setting"
                ],
                duration_minutes=6
            ),
            
            "multi_emotion_journey": DemoScenario(
                name="Multi-Emotion Journey",
                description="Complex scenario showing adaptation to multiple changing emotions",
                child_profile={
                    "age": 7,
                    "preferences": ["animals", "friendship", "adventure"],
                    "emotional_goal": "entertain"
                },
                emotion_sequence=[
                    {"emotion": "neutral", "confidence": 0.6, "delay": 3},
                    {"emotion": "curiosity", "confidence": 0.7, "delay": 5},
                    {"emotion": "excitement", "confidence": 0.8, "delay": 6},
                    {"emotion": "surprise", "confidence": 0.9, "delay": 4},
                    {"emotion": "joy", "confidence": 0.9, "delay": 8},
                    {"emotion": "boredom", "confidence": 0.7, "delay": 6},
                    {"emotion": "engagement", "confidence": 0.8, "delay": 10}
                ],
                expected_adaptations=[
                    "amplify_adventure",
                    "add_celebration_moments",
                    "introduce_surprise_character",
                    "create_mystery"
                ],
                duration_minutes=8
            )
        }
        
        return scenarios
    
    async def start_demo_scenario(self, scenario_name: str) -> str:
        """Start a demo scenario and return session ID."""
        
        if scenario_name not in self.demo_scenarios:
            raise ValueError(f"Unknown demo scenario: {scenario_name}")
        
        scenario = self.demo_scenarios[scenario_name]
        
        # Create child profile
        profile_data = scenario.child_profile
        child_profile = ChildProfile(
            age=profile_data["age"],
            preferences=profile_data["preferences"],
            emotional_goal=EmotionalGoal(profile_data["emotional_goal"])
        )
        
        # Start session
        session_id = await orchestrator.start_session(child_profile)
        session_id_str = str(session_id)
        
        # Initialize demo tracking
        self.active_demos[session_id_str] = {
            "scenario": scenario,
            "start_time": datetime.utcnow(),
            "emotion_index": 0,
            "adaptations_triggered": [],
            "response_times": []
        }
        
        # Initialize metrics
        self.demo_metrics[session_id_str] = DemoMetrics(
            session_id=session_id_str,
            scenario_name=scenario_name,
            start_time=datetime.utcnow(),
            end_time=None,
            total_segments=0,
            emotions_processed=0,
            adaptations_triggered=0,
            engagement_score=0.0,
            adaptation_accuracy=0.0,
            response_times=[]
        )
        
        # Start emotion sequence
        asyncio.create_task(self._run_emotion_sequence(session_id_str))
        
        logger.info(f"Started demo scenario '{scenario_name}' with session {session_id_str}")
        
        return session_id_str
    
    async def _run_emotion_sequence(self, session_id: str):
        """Run the emotion sequence for a demo scenario."""
        
        demo_data = self.active_demos.get(session_id)
        if not demo_data:
            return
        
        scenario = demo_data["scenario"]
        
        try:
            for i, emotion_data in enumerate(scenario.emotion_sequence):
                # Wait for the specified delay
                await asyncio.sleep(emotion_data["delay"])
                
                # Check if demo is still active
                if session_id not in self.active_demos:
                    break
                
                # Create emotion result
                from app.models.core import EmotionResult, EmotionState, EmotionSource
                
                emotion_state = EmotionState(
                    primary_emotion=EmotionType(emotion_data["emotion"]),
                    confidence=emotion_data["confidence"],
                    intensity=emotion_data.get("intensity", 0.7),
                    timestamp=datetime.utcnow(),
                    source=EmotionSource.COMBINED
                )
                
                emotion_result = EmotionResult(
                    emotion_state=emotion_state,
                    raw_data={"source": "demo_scenario"},
                    processing_time=0.1
                )
                
                # Process emotion and measure response time
                start_time = datetime.utcnow()
                
                try:
                    from uuid import UUID
                    adaptation_action = await orchestrator.process_emotion_update(
                        UUID(session_id), emotion_result
                    )
                    
                    response_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    # Update metrics
                    self._update_demo_metrics(session_id, emotion_data, adaptation_action, response_time)
                    
                    logger.info(f"Demo emotion processed: {emotion_data['emotion']} -> {adaptation_action.action_type}")
                    
                except Exception as e:
                    logger.error(f"Error processing demo emotion: {e}")
        
        except Exception as e:
            logger.error(f"Error in emotion sequence for demo {session_id}: {e}")
    
    def _update_demo_metrics(self, session_id: str, emotion_data: Dict, adaptation_action, response_time: float):
        """Update demo metrics with new data."""
        
        if session_id not in self.demo_metrics:
            return
        
        metrics = self.demo_metrics[session_id]
        demo_data = self.active_demos[session_id]
        
        # Update basic metrics
        metrics.emotions_processed += 1
        metrics.response_times.append(response_time)
        
        # Check if adaptation was triggered
        if adaptation_action and adaptation_action.action_type != "no_action":
            metrics.adaptations_triggered += 1
            demo_data["adaptations_triggered"].append(adaptation_action.action_type)
        
        # Calculate engagement score (based on confidence and response time)
        confidence = emotion_data["confidence"]
        engagement_factor = confidence * (1.0 if response_time < 2.0 else 0.5)
        
        # Running average of engagement
        current_score = metrics.engagement_score
        new_score = (current_score * (metrics.emotions_processed - 1) + engagement_factor) / metrics.emotions_processed
        metrics.engagement_score = new_score
        
        # Calculate adaptation accuracy
        scenario = demo_data["scenario"]
        expected_adaptations = set(scenario.expected_adaptations)
        triggered_adaptations = set(demo_data["adaptations_triggered"])
        
        if expected_adaptations:
            accuracy = len(expected_adaptations.intersection(triggered_adaptations)) / len(expected_adaptations)
            metrics.adaptation_accuracy = accuracy
    
    async def end_demo_scenario(self, session_id: str) -> DemoMetrics:
        """End a demo scenario and return final metrics."""
        
        if session_id in self.demo_metrics:
            metrics = self.demo_metrics[session_id]
            metrics.end_time = datetime.utcnow()
            
            # Get final session status
            try:
                from uuid import UUID
                session_status = await orchestrator.get_session_status(UUID(session_id))
                if session_status.get("story_progress"):
                    metrics.total_segments = session_status["story_progress"].get("segments_generated", 0)
            except Exception as e:
                logger.error(f"Error getting final session status: {e}")
        
        # Clean up
        self.active_demos.pop(session_id, None)
        
        return self.demo_metrics.get(session_id)
    
    def get_demo_metrics(self, session_id: str) -> Optional[DemoMetrics]:
        """Get current metrics for a demo session."""
        return self.demo_metrics.get(session_id)
    
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of available demo scenarios."""
        
        scenarios = []
        for name, scenario in self.demo_scenarios.items():
            scenarios.append({
                "name": name,
                "display_name": scenario.name,
                "description": scenario.description,
                "duration_minutes": scenario.duration_minutes,
                "child_age": scenario.child_profile["age"],
                "emotional_goal": scenario.child_profile["emotional_goal"],
                "emotion_count": len(scenario.emotion_sequence)
            })
        
        return scenarios


# Global instances
demo_manager = DemoManager()
ai_image_generator = AIImageGenerator()


# Demo Endpoints
@demo_router.get("/demo/scenarios")
async def get_demo_scenarios():
    """Get available demo scenarios."""
    
    scenarios = demo_manager.get_available_scenarios()
    
    return {
        "scenarios": scenarios,
        "total_count": len(scenarios)
    }


@demo_router.post("/demo/scenarios/{scenario_name}/start")
async def start_demo_scenario(scenario_name: str):
    """Start a demo scenario."""
    
    try:
        session_id = await demo_manager.start_demo_scenario(scenario_name)
        
        return {
            "message": f"Demo scenario '{scenario_name}' started successfully",
            "session_id": session_id,
            "scenario_name": scenario_name
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start demo scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start demo scenario: {str(e)}")


@demo_router.get("/demo/sessions/{session_id}/metrics")
async def get_demo_metrics(session_id: str):
    """Get metrics for a demo session."""
    
    metrics = demo_manager.get_demo_metrics(session_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Demo session not found")
    
    # Calculate additional statistics
    avg_response_time = sum(metrics.response_times) / len(metrics.response_times) if metrics.response_times else 0
    
    return {
        "session_id": metrics.session_id,
        "scenario_name": metrics.scenario_name,
        "duration_seconds": (
            (metrics.end_time or datetime.utcnow()) - metrics.start_time
        ).total_seconds(),
        "total_segments": metrics.total_segments,
        "emotions_processed": metrics.emotions_processed,
        "adaptations_triggered": metrics.adaptations_triggered,
        "engagement_score": round(metrics.engagement_score, 3),
        "adaptation_accuracy": round(metrics.adaptation_accuracy, 3),
        "average_response_time": round(avg_response_time, 3),
        "response_times": metrics.response_times,
        "is_completed": metrics.end_time is not None
    }


@demo_router.post("/demo/sessions/{session_id}/end")
async def end_demo_session(session_id: str):
    """End a demo session and get final metrics."""
    
    try:
        final_metrics = await demo_manager.end_demo_scenario(session_id)
        
        if not final_metrics:
            raise HTTPException(status_code=404, detail="Demo session not found")
        
        # End the actual storytelling session
        from uuid import UUID
        session_summary = await orchestrator.end_session(UUID(session_id))
        
        return {
            "message": "Demo session ended successfully",
            "demo_metrics": {
                "scenario_name": final_metrics.scenario_name,
                "duration_seconds": (final_metrics.end_time - final_metrics.start_time).total_seconds(),
                "emotions_processed": final_metrics.emotions_processed,
                "adaptations_triggered": final_metrics.adaptations_triggered,
                "engagement_score": round(final_metrics.engagement_score, 3),
                "adaptation_accuracy": round(final_metrics.adaptation_accuracy, 3),
                "average_response_time": round(
                    sum(final_metrics.response_times) / len(final_metrics.response_times)
                    if final_metrics.response_times else 0, 3
                )
            },
            "session_summary": {
                "session_id": str(session_summary.session_id),
                "duration_minutes": session_summary.duration_minutes,
                "total_segments": session_summary.total_segments,
                "emotions_detected": [emotion.value for emotion in session_summary.emotions_detected],
                "adaptations_made": session_summary.adaptations_made,
                "engagement_score": session_summary.engagement_score
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to end demo session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end demo session: {str(e)}")


@demo_router.post("/demo/sessions")
async def create_demo_session(request: dict):
    """Create a demo session with simplified API."""
    
    try:
        # Create child profile from request
        child_profile = ChildProfile(
            age=request.get("age", 6),
            preferences=request.get("preferences", ["animals"]),
            emotional_goal=EmotionalGoal(request.get("emotional_goal", "entertain")),
            voice_preference=request.get("voice_preference"),
            anonymous_id=request.get("anonymous_id", f"demo_{datetime.utcnow().timestamp()}")
        )
        
        # Start session through orchestrator
        session_id = await orchestrator.start_session(child_profile)
        
        return {
            "session_id": str(session_id),
            "message": "Demo session created successfully",
            "child_profile": {
                "age": child_profile.age,
                "emotional_goal": child_profile.emotional_goal.value,
                "preferences": child_profile.preferences
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create demo session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create demo session: {str(e)}")


@demo_router.post("/demo/sessions/{session_id}/story/generate")
async def generate_demo_story(session_id: str, request: dict = None):
    """Generate story segment for demo session."""
    
    try:
        from uuid import UUID
        session_uuid = UUID(session_id)
        
        # Get session
        session = await orchestrator.session_manager.get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create story context
        from app.models.core import StoryContext
        context_data = request or {}
        
        story_context = StoryContext(
            session_id=session_uuid,
            theme=context_data.get("theme", session.child_profile.preferences[0] if session.child_profile.preferences else "animals"),
            target_age=session.child_profile.age,
            current_segment="",
            characters=[],
            setting="",
            plot_points=[],
            emotional_arc=[]
        )
        
        # Generate story segment
        segment = await orchestrator.generate_story_segment(session_uuid, story_context)
        
        return {
            "text": segment.text,
            "emotional_tone": segment.emotional_tone,
            "pacing": segment.pacing,
            "characters_involved": segment.characters_involved,
            "sequence_number": getattr(segment, 'sequence_number', 1),
            "message": "Story segment generated successfully"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to generate demo story: {e}")
        
        # Return fallback story for demo
        fallback_stories = [
            "Había una vez, en un bosque mágico muy lejano, un pequeño conejo llamado Luna que tenía la habilidad especial de hacer brillar las estrellas con su cola esponjosa.",
            "Luna descubrió que cada vez que movía su cola, las estrellas del cielo parpadeaban con diferentes colores. Azul cuando estaba tranquila, dorado cuando estaba feliz, y plateado cuando tenía curiosidad.",
            "Un día, Luna se encontró con un búho sabio que le dijo: 'Tu don es muy especial, pequeña Luna. Las estrellas te están esperando para una gran aventura.'",
            "¿Qué crees que pasará en la aventura de Luna? La historia continúa adaptándose a cómo te sientes..."
        ]
        
        import random
        return {
            "text": random.choice(fallback_stories),
            "emotional_tone": "cheerful",
            "pacing": "moderate",
            "characters_involved": ["Luna", "Búho Sabio"],
            "sequence_number": 1,
            "message": "Demo story generated (fallback mode)"
        }


@demo_router.post("/demo/sessions/{session_id}/emotion")
async def send_demo_emotion(session_id: str, request: dict):
    """Send emotion feedback for demo session."""
    
    try:
        from uuid import UUID
        from app.models.core import EmotionResult, EmotionState, EmotionType, EmotionSource
        
        session_uuid = UUID(session_id)
        
        # Create emotion state
        emotion_state = EmotionState(
            primary_emotion=EmotionType(request.get("emotion", "joy")),
            confidence=request.get("confidence", 0.8),
            intensity=request.get("intensity", 0.7),
            timestamp=datetime.utcnow(),
            source=EmotionSource.USER_FEEDBACK
        )
        
        emotion_result = EmotionResult(
            emotion_state=emotion_state,
            raw_data={"source": "demo_feedback"},
            processing_time=0.1
        )
        
        # Process emotion
        adaptation_action = await orchestrator.process_emotion_update(session_uuid, emotion_result)
        
        return {
            "message": "Emotion processed successfully",
            "emotion": emotion_state.primary_emotion.value,
            "confidence": emotion_state.confidence,
            "adaptation": {
                "action_type": adaptation_action.action_type if adaptation_action else "no_action",
                "reason": adaptation_action.reason if adaptation_action else "No adaptation needed",
                "confidence": adaptation_action.confidence if adaptation_action else 0.0
            }
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to process demo emotion: {e}")
        return {
            "message": "Emotion processed (demo mode)",
            "emotion": request.get("emotion", "joy"),
            "confidence": request.get("confidence", 0.8),
            "adaptation": {
                "action_type": "continue",
                "reason": "Demo mode active",
                "confidence": 0.8
            }
        }


@demo_router.post("/demo/sessions/{session_id}/end")
async def end_demo_session_simple(session_id: str):
    """End demo session with simplified response."""
    
    try:
        from uuid import UUID
        session_uuid = UUID(session_id)
        
        # Try to end session properly
        try:
            summary = await orchestrator.end_session(session_uuid)
            return {
                "message": "Demo session ended successfully",
                "session_id": session_id,
                "duration_minutes": summary.duration_minutes,
                "total_segments": summary.total_segments
            }
        except Exception as e:
            logger.warning(f"Error ending session properly: {e}")
            return {
                "message": "Demo session ended (with warnings)",
                "session_id": session_id,
                "duration_minutes": 0.0,
                "total_segments": 0
            }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to end demo session: {e}")
        return {
            "message": "Demo session ended (demo mode)",
            "session_id": session_id,
            "duration_minutes": 0.0,
            "total_segments": 0
        }


@demo_router.get("/demo/analytics")
async def get_demo_analytics():
    """Get aggregated analytics from all demo sessions."""
    
    all_metrics = list(demo_manager.demo_metrics.values())
    
    if not all_metrics:
        return {
            "total_sessions": 0,
            "message": "No demo sessions found"
        }
    
    # Calculate aggregated statistics
    total_sessions = len(all_metrics)
    completed_sessions = len([m for m in all_metrics if m.end_time])
    
    avg_engagement = sum(m.engagement_score for m in all_metrics) / total_sessions
    avg_accuracy = sum(m.adaptation_accuracy for m in all_metrics) / total_sessions
    
    all_response_times = []
    for metrics in all_metrics:
        all_response_times.extend(metrics.response_times)
    
    avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
    
    # Scenario performance
    scenario_stats = {}
    for metrics in all_metrics:
        scenario = metrics.scenario_name
        if scenario not in scenario_stats:
            scenario_stats[scenario] = {
                "sessions": 0,
                "avg_engagement": 0,
                "avg_accuracy": 0
            }
        
        stats = scenario_stats[scenario]
        stats["sessions"] += 1
        stats["avg_engagement"] = (
            (stats["avg_engagement"] * (stats["sessions"] - 1) + metrics.engagement_score) 
            / stats["sessions"]
        )
        stats["avg_accuracy"] = (
            (stats["avg_accuracy"] * (stats["sessions"] - 1) + metrics.adaptation_accuracy) 
            / stats["sessions"]
        )
    
    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "overall_metrics": {
            "average_engagement_score": round(avg_engagement, 3),
            "average_adaptation_accuracy": round(avg_accuracy, 3),
            "average_response_time": round(avg_response_time, 3)
        },
        "scenario_performance": {
            scenario: {
                "sessions": stats["sessions"],
                "avg_engagement": round(stats["avg_engagement"], 3),
                "avg_accuracy": round(stats["avg_accuracy"], 3)
            }
            for scenario, stats in scenario_stats.items()
        }
    }


# AI Image Generation Endpoints
@demo_router.post("/demo/sessions/{session_id}/photo")
async def upload_user_photo(session_id: str, photo_data: str = Form(...)):
    """Upload user photo for character generation."""
    
    try:
        # Store the user photo
        success = ai_image_generator.store_user_photo(session_id, photo_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid photo data or format")
        
        return {
            "message": "Photo uploaded successfully",
            "session_id": session_id,
            "photo_stored": True
        }
        
    except Exception as e:
        logger.error(f"Error uploading user photo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@demo_router.post("/demo/sessions/{session_id}/generate-image")
async def generate_story_image(session_id: str, request: ImageGenerationRequest):
    """Generate AI image for story scene with optional user photo integration."""
    
    try:
        # Check if user has uploaded a photo
        has_photo = ai_image_generator.get_user_photo(session_id) is not None
        request.has_user_photo = has_photo
        
        # Generate the image
        response = await ai_image_generator.generate_story_image(session_id, request)
        
        return {
            "success": True,
            "image_url": response.image_url,
            "generation_time": response.generation_time,
            "prompt_used": response.prompt_used,
            "style_applied": response.style_applied,
            "has_user_character": has_photo,
            "message": "Image generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating story image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")


@demo_router.get("/demo/sessions/{session_id}/photo")
async def get_user_photo(session_id: str):
    """Get user photo for a session."""
    
    photo_data = ai_image_generator.get_user_photo(session_id)
    
    if not photo_data:
        raise HTTPException(status_code=404, detail="No photo found for this session")
    
    return {
        "session_id": session_id,
        "has_photo": True,
        "photo_data": photo_data
    }


@demo_router.delete("/demo/sessions/{session_id}/photo")
async def delete_user_photo(session_id: str):
    """Delete user photo for a session."""
    
    try:
        ai_image_generator.clear_session_data(session_id)
        
        return {
            "message": "Photo deleted successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting user photo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")


@demo_router.post("/demo/sessions/{session_id}/generate-avatar")
async def generate_user_avatar(session_id: str, request: AvatarGenerationRequest):
    """Generate avatar from user photo."""
    
    try:
        response = await ai_image_generator.generate_avatar_from_photo(session_id, request.style)
        
        return {
            "success": True,
            "avatar_url": response.avatar_url,
            "generation_time": response.generation_time,
            "style_applied": response.style_applied,
            "message": "Avatar generated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating avatar: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate avatar: {str(e)}")


@demo_router.get("/demo/avatar-styles")
async def get_available_avatar_styles():
    """Get available avatar generation styles."""
    
    styles = {
        "children_book_avatar": {
            "name": "Avatar de Cuento",
            "description": "Avatar estilo libro infantil, amigable y colorido"
        },
        "cartoon_avatar": {
            "name": "Avatar Cartoon",
            "description": "Avatar estilo caricatura animada"
        },
        "fantasy_avatar": {
            "name": "Avatar Fantástico",
            "description": "Avatar con elementos mágicos y fantásticos"
        },
        "watercolor_avatar": {
            "name": "Avatar Acuarela",
            "description": "Avatar en estilo acuarela suave"
        }
    }
    
    return {
        "styles": styles,
        "default_style": "children_book_avatar"
    }


@demo_router.get("/demo/image-styles")
async def get_available_image_styles():
    """Get available image generation styles."""
    
    styles = {
        "children_book": {
            "name": "Libro Infantil",
            "description": "Estilo colorido y amigable de ilustración de libros para niños",
            "preview": "/static/images/style_children_book.jpg"
        },
        "watercolor": {
            "name": "Acuarela",
            "description": "Estilo de pintura en acuarela con bordes suaves y colores gentiles",
            "preview": "/static/images/style_watercolor.jpg"
        },
        "cartoon": {
            "name": "Caricatura",
            "description": "Estilo de animación cartoon con colores brillantes y personajes expresivos",
            "preview": "/static/images/style_cartoon.jpg"
        },
        "realistic": {
            "name": "Realista Mágico",
            "description": "Estilo realista con elementos mágicos, detallado e inmersivo",
            "preview": "/static/images/style_realistic.jpg"
        },
        "fantasy": {
            "name": "Fantasía",
            "description": "Estilo de arte fantástico con atmósfera mágica y detalles encantadores",
            "preview": "/static/images/style_fantasy.jpg"
        }
    }
    
    return {
        "styles": styles,
        "default_style": "children_book"
    }