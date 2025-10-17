"""Story orchestration engine that coordinates all storytelling components."""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.core.interfaces import StoryOrchestratorInterface
from app.models.core import (
    ChildProfile, AdaptationAction, StorySegment, StoryContext,
    EmotionResult, EmotionState, SessionSummary, VoiceConfig
)
from app.core.emotion_analyzer import EmotionAnalyzer
from app.core.story_generator import StoryGenerator, EmotionAdaptationEngine, StoryContextManager
from app.core.voice_narrator import VoiceNarrator, AdaptiveAudioManager
from app.core.session_manager import SessionManager
from app.utils.voice_config import VoiceConfigManager

logger = logging.getLogger(__name__)


class StoryOrchestrator(StoryOrchestratorInterface):
    """Central orchestrator that coordinates emotion detection, story adaptation, and narration."""
    
    def __init__(self):
        # Initialize core components
        self.emotion_analyzer = EmotionAnalyzer()
        self.story_generator = StoryGenerator()
        self.voice_narrator = VoiceNarrator()
        self.session_manager = SessionManager()
        
        # Initialize specialized managers
        self.adaptation_engine = EmotionAdaptationEngine()
        self.story_context_manager = StoryContextManager()
        self.audio_manager = AdaptiveAudioManager()
        self.voice_config_manager = VoiceConfigManager()
        
        # Orchestration state
        self.active_orchestrations: Dict[str, Dict[str, Any]] = {}
        self.processing_locks: Dict[str, asyncio.Lock] = {}
    
    async def start_session(self, child_profile: ChildProfile) -> UUID:
        """Start a new storytelling session."""
        
        try:
            # Create session
            session = await self.session_manager.create_session(child_profile)
            session_id = str(session.session_id)
            
            # Initialize orchestration state
            self.active_orchestrations[session_id] = {
                "session": session,
                "story_started": False,
                "last_emotion_update": None,
                "adaptation_count": 0,
                "audio_streaming": False
            }
            
            # Create processing lock for this session
            self.processing_locks[session_id] = asyncio.Lock()
            
            # Set up voice configuration
            base_voice_config = self.voice_config_manager.create_base_config(
                child_profile.age, child_profile.voice_preference
            )
            self.voice_narrator.set_session_voice_config(session_id, base_voice_config)
            
            # Initialize adaptive audio session
            await self.audio_manager.start_adaptive_session(session_id, base_voice_config)
            
            logger.info(f"Started storytelling session: {session_id}")
            
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise
    
    async def process_emotion_update(
        self, 
        session_id: UUID, 
        emotion_data: EmotionResult
    ) -> AdaptationAction:
        """Process emotion update and determine adaptation action."""
        
        session_id_str = str(session_id)
        
        # Use processing lock to prevent concurrent updates
        async with self.processing_locks.get(session_id_str, asyncio.Lock()):
            try:
                orchestration = self.active_orchestrations.get(session_id_str)
                if not orchestration:
                    raise ValueError(f"No active orchestration for session: {session_id}")
                
                session = orchestration["session"]
                
                # Validate emotion confidence
                if not self.emotion_analyzer.validate_emotion_confidence(emotion_data):
                    logger.debug(f"Low confidence emotion ignored for session {session_id}")
                    return AdaptationAction(
                        action_type="no_action",
                        parameters={},
                        reason="Low confidence emotion detection",
                        confidence=emotion_data.emotion_state.confidence
                    )
                
                # Update emotion state in analyzer
                self.emotion_analyzer.state_manager.add_emotion_state(
                    session_id_str, emotion_data.emotion_state
                )
                
                # Get current story context
                story_context = self.story_context_manager.get_story_context(session_id_str)
                if not story_context:
                    # If no story context yet, start the story
                    return await self._initiate_story_generation(session_id_str, session)
                
                # Get emotion trend analysis
                emotion_trend = self.emotion_analyzer.get_emotion_trend(session_id_str)
                
                # Analyze if adaptation is needed
                adaptation_plan = self.adaptation_engine.analyze_adaptation_need(
                    session_id_str,
                    emotion_data.emotion_state,
                    emotion_trend,
                    session.child_profile.emotional_goal,
                    story_context
                )
                
                if adaptation_plan:
                    # Execute adaptation
                    return await self._execute_story_adaptation(
                        session_id_str, adaptation_plan, story_context
                    )
                else:
                    # Continue with current story flow
                    return AdaptationAction(
                        action_type="continue",
                        parameters={"emotion_acknowledged": True},
                        reason="Emotion detected but no adaptation needed",
                        confidence=emotion_data.emotion_state.confidence
                    )
                
            except Exception as e:
                logger.error(f"Error processing emotion update for session {session_id}: {e}")
                return AdaptationAction(
                    action_type="error",
                    parameters={"error": str(e)},
                    reason="Processing error occurred",
                    confidence=0.0
                )
    
    async def generate_story_segment(
        self, 
        session_id: UUID, 
        context: StoryContext
    ) -> StorySegment:
        """Generate the next story segment."""
        
        session_id_str = str(session_id)
        
        try:
            orchestration = self.active_orchestrations.get(session_id_str)
            if not orchestration:
                raise ValueError(f"No active orchestration for session: {session_id}")
            
            session = orchestration["session"]
            
            # Check if story should be concluded
            if self.story_context_manager.should_conclude_story(session_id_str):
                return await self.story_generator.generate_story_conclusion(context)
            
            # Get current emotion state
            current_emotion = await self.emotion_analyzer.get_current_emotion(session_id_str)
            
            # Generate next segment
            if not orchestration["story_started"]:
                # Generate initial story with language
                language = context.target_language or 'en'
                segment = await self.story_generator.generate_initial_story(
                    session.child_profile, context.theme, language
                )
                orchestration["story_started"] = True
                
                # Create story context
                story_context = self.story_context_manager.create_story_context(
                    session_id_str, session.child_profile, context.theme, segment
                )
                
                # Update session with story context
                session.story_context = story_context
                await self.session_manager.update_session_state(session_id, session)
                
            else:
                # Generate adapted segment
                if current_emotion:
                    segment = await self.story_generator.adapt_story_segment(
                        context, current_emotion, session.child_profile.emotional_goal
                    )
                else:
                    # Continue story naturally without specific adaptation
                    segment = await self._generate_continuation_segment(context, session)
                
                # Update story context
                self.story_context_manager.update_story_context(
                    session_id_str, segment, current_emotion
                )
            
            # Generate audio for the segment
            await self._generate_and_stream_audio(session_id_str, segment, current_emotion)
            
            return segment
            
        except Exception as e:
            logger.error(f"Error generating story segment for session {session_id}: {e}")
            raise
    
    async def end_session(self, session_id: UUID) -> SessionSummary:
        """End a storytelling session and return summary."""
        
        session_id_str = str(session_id)
        
        try:
            # Get orchestration state
            orchestration = self.active_orchestrations.get(session_id_str)
            if not orchestration:
                raise ValueError(f"No active orchestration for session: {session_id}")
            
            # End session through session manager
            summary = await self.session_manager.lifecycle_manager.end_session(
                session_id_str, "user_requested"
            )
            
            # Clean up orchestration resources
            await self._cleanup_orchestration(session_id_str)
            
            logger.info(f"Ended storytelling session: {session_id}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            raise
    
    async def _initiate_story_generation(
        self, 
        session_id: str, 
        session
    ) -> AdaptationAction:
        """Initiate story generation for a new session."""
        
        try:
            # Determine story theme based on preferences
            theme = self._select_story_theme(session.child_profile)
            
            # Generate initial story segment
            initial_segment = await self.story_generator.generate_initial_story(
                session.child_profile, theme
            )
            
            # Create story context
            story_context = self.story_context_manager.create_story_context(
                session_id, session.child_profile, theme, initial_segment
            )
            
            # Update session
            session.story_context = story_context
            await self.session_manager.update_session_state(
                UUID(session_id), session
            )
            
            # Generate and stream audio
            current_emotion = await self.emotion_analyzer.get_current_emotion(session_id)
            await self._generate_and_stream_audio(session_id, initial_segment, current_emotion)
            
            # Mark story as started
            self.active_orchestrations[session_id]["story_started"] = True
            
            return AdaptationAction(
                action_type="story_initiated",
                parameters={
                    "theme": theme,
                    "segment_text": initial_segment.text[:100] + "..."
                },
                reason="Initial story generation",
                confidence=1.0
            )
            
        except Exception as e:
            logger.error(f"Failed to initiate story for session {session_id}: {e}")
            raise
    
    async def _execute_story_adaptation(
        self,
        session_id: str,
        adaptation_plan: Dict[str, Any],
        story_context: StoryContext
    ) -> AdaptationAction:
        """Execute a story adaptation based on the adaptation plan."""
        
        try:
            # Get current emotion
            current_emotion = await self.emotion_analyzer.get_current_emotion(session_id)
            if not current_emotion:
                raise ValueError("No current emotion available for adaptation")
            
            # Get session
            orchestration = self.active_orchestrations[session_id]
            session = orchestration["session"]
            
            # Generate adapted story segment
            adapted_segment = await self.story_generator.adapt_story_segment(
                story_context, current_emotion, session.child_profile.emotional_goal
            )
            
            # Update story context
            self.story_context_manager.update_story_context(
                session_id, adapted_segment, current_emotion
            )
            
            # Generate and stream adapted audio
            await self._generate_and_stream_audio(session_id, adapted_segment, current_emotion)
            
            # Update adaptation count
            orchestration["adaptation_count"] += 1
            
            return AdaptationAction(
                action_type=adaptation_plan["adaptation_type"],
                parameters={
                    "adapted_segment": adapted_segment.text[:100] + "...",
                    "emotion_trigger": current_emotion.primary_emotion.value,
                    "adaptation_reason": adaptation_plan.get("implementation_details", {})
                },
                reason=f"Story adapted for {current_emotion.primary_emotion.value}",
                confidence=current_emotion.confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to execute adaptation for session {session_id}: {e}")
            raise
    
    async def _generate_continuation_segment(
        self, 
        context: StoryContext, 
        session
    ) -> StorySegment:
        """Generate a natural story continuation without specific adaptation."""
        
        # Create a neutral emotion state for continuation
        neutral_emotion = EmotionState(
            primary_emotion="neutral",
            confidence=0.5,
            intensity=0.5,
            timestamp=datetime.utcnow(),
            source="system"
        )
        
        return await self.story_generator.adapt_story_segment(
            context, neutral_emotion, session.child_profile.emotional_goal
        )
    
    async def _generate_and_stream_audio(
        self,
        session_id: str,
        segment: StorySegment,
        current_emotion: Optional[EmotionState]
    ) -> None:
        """Generate audio for story segment and add to stream."""
        
        try:
            # Get voice configuration
            base_config = self.voice_narrator.get_session_voice_config(session_id)
            if not base_config:
                # Create default config
                base_config = VoiceConfig(voice_id="Joanna")
            
            # Get story context for characters
            story_context = self.story_context_manager.get_story_context(session_id)
            characters = story_context.characters if story_context else []
            
            # Generate audio with emotion adaptation
            audio_data = await self.voice_narrator.narrate_with_emotion_adaptation(
                segment, base_config, current_emotion, characters
            )
            
            # Process and stream audio
            await self.audio_manager.process_story_segment_audio(
                session_id, audio_data, segment, current_emotion
            )
            
            # Mark audio as streaming
            self.active_orchestrations[session_id]["audio_streaming"] = True
            
        except Exception as e:
            logger.error(f"Failed to generate audio for session {session_id}: {e}")
    
    def _select_story_theme(self, child_profile: ChildProfile) -> str:
        """Select appropriate story theme based on child profile."""
        
        # Use preferences if available
        if child_profile.preferences:
            return child_profile.preferences[0]
        
        # Default themes by age
        age_themes = {
            (3, 5): "animals",
            (6, 8): "adventure", 
            (9, 12): "friendship"
        }
        
        for age_range, theme in age_themes.items():
            if age_range[0] <= child_profile.age <= age_range[1]:
                return theme
        
        return "friendship"  # Default fallback
    
    async def _cleanup_orchestration(self, session_id: str) -> None:
        """Clean up orchestration resources for a session."""
        
        try:
            # Stop adaptive audio session
            await self.audio_manager.stop_adaptive_session(session_id)
            
            # Clean up voice narrator session
            self.voice_narrator.cleanup_session(session_id)
            
            # Clean up emotion analyzer session
            self.emotion_analyzer.cleanup_session(session_id)
            
            # Clean up story context
            self.story_context_manager.cleanup_session(session_id)
            
            # Clean up adaptation engine
            self.adaptation_engine.cleanup_session(session_id)
            
            # Remove orchestration state
            self.active_orchestrations.pop(session_id, None)
            self.processing_locks.pop(session_id, None)
            
            logger.debug(f"Cleaned up orchestration for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up orchestration for session {session_id}: {e}")
    
    async def get_session_status(self, session_id: UUID) -> Dict[str, Any]:
        """Get comprehensive status for a storytelling session."""
        
        session_id_str = str(session_id)
        
        try:
            orchestration = self.active_orchestrations.get(session_id_str)
            if not orchestration:
                return {"status": "not_found"}
            
            # Get session info
            session = orchestration["session"]
            
            # Get story context
            story_context = self.story_context_manager.get_story_context(session_id_str)
            
            # Get current emotion
            current_emotion = await self.emotion_analyzer.get_current_emotion(session_id_str)
            
            # Get emotion summary
            emotion_summary = self.emotion_analyzer.get_session_summary(session_id_str)
            
            # Get audio status
            audio_status = self.audio_manager.get_session_audio_status(session_id_str)
            
            return {
                "status": "active",
                "session_info": {
                    "session_id": session_id_str,
                    "child_age": session.child_profile.age,
                    "emotional_goal": session.child_profile.emotional_goal.value,
                    "created_at": session.created_at.isoformat(),
                    "state": session.state.value
                },
                "story_progress": {
                    "story_started": orchestration["story_started"],
                    "theme": story_context.theme if story_context else None,
                    "segments_generated": len(story_context.plot_points) if story_context else 0,
                    "characters": [char.name for char in story_context.characters] if story_context else [],
                    "adaptations_made": orchestration["adaptation_count"]
                },
                "emotion_status": {
                    "current_emotion": current_emotion.primary_emotion.value if current_emotion else None,
                    "confidence": current_emotion.confidence if current_emotion else 0.0,
                    "emotion_summary": emotion_summary
                },
                "audio_status": audio_status
            }
            
        except Exception as e:
            logger.error(f"Error getting session status for {session_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def process_multimodal_input(
        self,
        session_id: UUID,
        audio_data: Optional[bytes] = None,
        image_data: Optional[bytes] = None
    ) -> Optional[AdaptationAction]:
        """Process multimodal input (audio + visual) and trigger adaptations."""
        
        session_id_str = str(session_id)
        
        try:
            # Process multimodal emotion detection
            emotion_state = await self.emotion_analyzer.process_multimodal_input(
                session_id_str, audio_data, image_data
            )
            
            if emotion_state:
                # Create emotion result
                emotion_result = EmotionResult(
                    emotion_state=emotion_state,
                    raw_data={"source": "multimodal"},
                    processing_time=0.0
                )
                
                # Process emotion update
                return await self.process_emotion_update(session_id, emotion_result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing multimodal input for session {session_id}: {e}")
            return None
    
    async def get_audio_stream(self, session_id: UUID):
        """Get audio stream for a session."""
        
        session_id_str = str(session_id)
        
        try:
            async for chunk in self.audio_manager.get_streaming_chunks(session_id_str):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error streaming audio for session {session_id}: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown orchestrator and cleanup all resources."""
        
        logger.info("Shutting down story orchestrator...")
        
        # End all active sessions
        active_session_ids = list(self.active_orchestrations.keys())
        for session_id in active_session_ids:
            try:
                await self._cleanup_orchestration(session_id)
            except Exception as e:
                logger.error(f"Error cleaning up session {session_id} during shutdown: {e}")
        
        # Shutdown session manager
        await self.session_manager.shutdown()
        
        logger.info("Story orchestrator shutdown complete")