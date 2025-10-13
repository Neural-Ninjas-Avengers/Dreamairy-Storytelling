"""Session management and lifecycle handling for storytelling sessions."""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
import json

from app.core.interfaces import SessionManagerInterface
from app.models.core import (
    Session, ChildProfile, SessionState, SessionSummary,
    StoryContext, EmotionState, VoiceConfig
)
from app.services.aws_clients import s3_client

logger = logging.getLogger(__name__)


class SessionLifecycleManager:
    """Manages the complete lifecycle of storytelling sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Session] = {}
        self.session_timers: Dict[str, asyncio.Task] = {}
        self.max_session_duration = 1800  # 30 minutes
        self.cleanup_interval = 300  # 5 minutes
        self.privacy_retention_hours = 24  # Data retention period
        
        # Cleanup task will be created when needed
        self._cleanup_task = None
    
    def _ensure_cleanup_task(self):
        """Ensure the cleanup task is running."""
        if self._cleanup_task is None or self._cleanup_task.done():
            try:
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            except RuntimeError:
                # No event loop running, task will be created later
                pass
    
    async def create_session(self, child_profile: ChildProfile) -> Session:
        """Create a new storytelling session."""
        
        try:
            # Ensure cleanup task is running
            self._ensure_cleanup_task()
            
            # Generate session ID
            session_id = uuid4()
            
            # Create session object
            session = Session(
                session_id=session_id,
                child_profile=child_profile,
                state=SessionState.CREATED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in active sessions
            self.active_sessions[str(session_id)] = session
            
            # Set up session timeout
            await self._setup_session_timeout(str(session_id))
            
            logger.info(f"Created new session: {session_id} for age {child_profile.age}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        
        session = self.active_sessions.get(session_id)
        
        if session:
            # Update last accessed time
            session.updated_at = datetime.utcnow()
        
        return session
    
    async def update_session_state(self, session_id: str, new_state: SessionState) -> bool:
        """Update session state."""
        
        session = self.active_sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found for state update: {session_id}")
            return False
        
        old_state = session.state
        session.update_state(new_state)
        
        logger.info(f"Session {session_id} state changed: {old_state.value} -> {new_state.value}")
        
        # Handle state-specific actions
        if new_state == SessionState.COMPLETED:
            await self._handle_session_completion(session_id)
        elif new_state == SessionState.ERROR:
            await self._handle_session_error(session_id)
        
        return True
    
    async def update_session_context(self, session_id: str, story_context: StoryContext) -> bool:
        """Update session with story context."""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.story_context = story_context
        session.updated_at = datetime.utcnow()
        
        return True
    
    async def end_session(self, session_id: str, reason: str = "user_requested") -> SessionSummary:
        """End a storytelling session and generate summary."""
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # Update session state
            await self.update_session_state(session_id, SessionState.COMPLETED)
            
            # Generate session summary
            summary = await self._generate_session_summary(session, reason)
            
            # Schedule cleanup
            await self._schedule_session_cleanup(session_id)
            
            logger.info(f"Session ended: {session_id}, reason: {reason}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise
    
    async def cleanup_session_data(self, session_id: str) -> None:
        """Clean up session data for privacy compliance."""
        
        try:
            # Remove from active sessions
            session = self.active_sessions.pop(session_id, None)
            
            # Cancel session timer
            if session_id in self.session_timers:
                self.session_timers[session_id].cancel()
                del self.session_timers[session_id]
            
            # Clean up any stored user data
            if session and session.child_profile.anonymous_id:
                await self._cleanup_user_data(session.child_profile.anonymous_id)
            
            logger.info(f"Cleaned up session data: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions."""
        
        active_sessions = []
        
        for session_id, session in self.active_sessions.items():
            session_info = {
                "session_id": str(session.session_id),
                "state": session.state.value,
                "child_age": session.child_profile.age,
                "created_at": session.created_at.isoformat(),
                "duration_minutes": (datetime.utcnow() - session.created_at).total_seconds() / 60,
                "has_story_context": session.story_context is not None
            }
            active_sessions.append(session_info)
        
        return active_sessions
    
    async def _setup_session_timeout(self, session_id: str) -> None:
        """Set up automatic session timeout."""
        
        async def timeout_handler():
            try:
                await asyncio.sleep(self.max_session_duration)
                
                # Check if session is still active
                if session_id in self.active_sessions:
                    logger.info(f"Session timeout reached: {session_id}")
                    await self.end_session(session_id, "timeout")
                    
            except asyncio.CancelledError:
                pass  # Timer was cancelled
            except Exception as e:
                logger.error(f"Session timeout handler error: {e}")
        
        # Store timer task
        self.session_timers[session_id] = asyncio.create_task(timeout_handler())
    
    async def _handle_session_completion(self, session_id: str) -> None:
        """Handle session completion tasks."""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Store user preferences if any insights were gathered
        if session.story_context:
            await self._store_user_insights(session)
    
    async def _handle_session_error(self, session_id: str) -> None:
        """Handle session error cleanup."""
        
        logger.warning(f"Session entered error state: {session_id}")
        
        # Schedule immediate cleanup for error sessions
        await asyncio.sleep(60)  # Wait 1 minute before cleanup
        await self.cleanup_session_data(session_id)
    
    async def _generate_session_summary(self, session: Session, end_reason: str) -> SessionSummary:
        """Generate a comprehensive session summary."""
        
        duration = (datetime.utcnow() - session.created_at).total_seconds() / 60
        
        # Count story segments
        total_segments = 0
        emotions_detected = []
        adaptations_made = 0
        
        if session.story_context:
            total_segments = len(session.story_context.plot_points)
            emotions_detected = [
                emotion.primary_emotion for emotion in session.story_context.emotional_arc
            ]
            # Count adaptations (segments with adaptation reasons)
            adaptations_made = sum(
                1 for point in session.story_context.plot_points 
                if "adapted" in point.lower()
            )
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(session)
        
        return SessionSummary(
            session_id=session.session_id,
            duration_minutes=duration,
            total_segments=total_segments,
            emotions_detected=list(set(emotions_detected)),  # Unique emotions
            adaptations_made=adaptations_made,
            engagement_score=engagement_score
        )
    
    def _calculate_engagement_score(self, session: Session) -> Optional[float]:
        """Calculate engagement score based on session data."""
        
        if not session.story_context or not session.story_context.emotional_arc:
            return None
        
        emotions = session.story_context.emotional_arc
        
        # Calculate average confidence and intensity
        avg_confidence = sum(e.confidence for e in emotions) / len(emotions)
        avg_intensity = sum(e.intensity for e in emotions) / len(emotions)
        
        # Positive emotions boost score
        positive_emotions = ["joy", "excitement", "calm"]
        positive_ratio = sum(
            1 for e in emotions if e.primary_emotion.value in positive_emotions
        ) / len(emotions)
        
        # Combine factors
        engagement_score = (avg_confidence * 0.3 + avg_intensity * 0.4 + positive_ratio * 0.3)
        
        return min(1.0, max(0.0, engagement_score))
    
    async def _store_user_insights(self, session: Session) -> None:
        """Store user insights for future personalization."""
        
        try:
            if not session.story_context:
                return
            
            insights = {
                "preferred_themes": [session.story_context.theme],
                "character_preferences": [char.name for char in session.story_context.characters],
                "emotional_responses": [
                    {
                        "emotion": e.primary_emotion.value,
                        "confidence": e.confidence,
                        "intensity": e.intensity
                    }
                    for e in session.story_context.emotional_arc[-5:]  # Last 5 emotions
                ],
                "session_duration": (datetime.utcnow() - session.created_at).total_seconds(),
                "engagement_score": self._calculate_engagement_score(session),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Store insights using anonymous ID
            anonymous_id = session.child_profile.anonymous_id
            await s3_client.store_user_preferences(anonymous_id, insights)
            
        except Exception as e:
            logger.error(f"Failed to store user insights: {e}")
    
    async def _cleanup_user_data(self, anonymous_id: str) -> None:
        """Clean up user data for privacy compliance."""
        
        try:
            # Delete user preferences from S3
            await s3_client.delete_user_data(anonymous_id)
            
        except Exception as e:
            logger.error(f"Failed to cleanup user data for {anonymous_id}: {e}")
    
    async def _schedule_session_cleanup(self, session_id: str) -> None:
        """Schedule session cleanup after retention period."""
        
        async def delayed_cleanup():
            try:
                # Wait for retention period
                await asyncio.sleep(self.privacy_retention_hours * 3600)
                await self.cleanup_session_data(session_id)
                
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Delayed cleanup error for {session_id}: {e}")
        
        # Start cleanup task
        asyncio.create_task(delayed_cleanup())
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired sessions."""
        
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check if session has been inactive too long
                    inactive_duration = (current_time - session.updated_at).total_seconds()
                    
                    if inactive_duration > self.max_session_duration:
                        expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    logger.info(f"Cleaning up expired session: {session_id}")
                    await self.end_session(session_id, "expired")
                
            except Exception as e:
                logger.error(f"Periodic cleanup error: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown session manager and cleanup resources."""
        
        # Cancel cleanup task
        if hasattr(self, '_cleanup_task'):
            self._cleanup_task.cancel()
        
        # End all active sessions
        active_session_ids = list(self.active_sessions.keys())
        for session_id in active_session_ids:
            try:
                await self.end_session(session_id, "shutdown")
            except Exception as e:
                logger.error(f"Error ending session {session_id} during shutdown: {e}")
        
        # Cancel all timers
        for timer in self.session_timers.values():
            timer.cancel()
        
        logger.info("Session manager shutdown complete")


class UserPreferenceManager:
    """Manages user preferences and personalization data."""
    
    def __init__(self):
        self.preference_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.cache_timestamps: Dict[str, datetime] = {}
    
    async def get_user_preferences(self, anonymous_id: str) -> Dict[str, Any]:
        """Get user preferences by anonymous ID."""
        
        try:
            # Check cache first
            if self._is_cache_valid(anonymous_id):
                return self.preference_cache[anonymous_id]
            
            # Load from storage
            preferences = await s3_client.get_user_preferences(anonymous_id)
            
            if preferences:
                # Update cache
                self.preference_cache[anonymous_id] = preferences
                self.cache_timestamps[anonymous_id] = datetime.utcnow()
                return preferences
            
            # Return default preferences for new users
            return self._get_default_preferences()
            
        except Exception as e:
            logger.error(f"Failed to get user preferences for {anonymous_id}: {e}")
            return self._get_default_preferences()
    
    async def update_user_preferences(self, anonymous_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        
        try:
            # Merge with existing preferences
            existing_prefs = await self.get_user_preferences(anonymous_id)
            merged_prefs = self._merge_preferences(existing_prefs, preferences)
            
            # Store updated preferences
            await s3_client.store_user_preferences(anonymous_id, merged_prefs)
            
            # Update cache
            self.preference_cache[anonymous_id] = merged_prefs
            self.cache_timestamps[anonymous_id] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update user preferences for {anonymous_id}: {e}")
    
    def _is_cache_valid(self, anonymous_id: str) -> bool:
        """Check if cached preferences are still valid."""
        
        if anonymous_id not in self.preference_cache:
            return False
        
        if anonymous_id not in self.cache_timestamps:
            return False
        
        cache_age = (datetime.utcnow() - self.cache_timestamps[anonymous_id]).total_seconds()
        return cache_age < self.cache_ttl
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences for new users."""
        
        return {
            "preferred_themes": ["animals", "friendship"],
            "character_preferences": [],
            "emotional_responses": [],
            "voice_preferences": {},
            "session_history": [],
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _merge_preferences(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new preferences with existing ones."""
        
        merged = existing.copy()
        
        # Merge lists (themes, characters, etc.)
        for key in ["preferred_themes", "character_preferences"]:
            if key in new:
                existing_items = set(merged.get(key, []))
                new_items = set(new[key])
                merged[key] = list(existing_items.union(new_items))
        
        # Append emotional responses (keep recent ones)
        if "emotional_responses" in new:
            existing_responses = merged.get("emotional_responses", [])
            existing_responses.extend(new["emotional_responses"])
            # Keep only last 20 responses
            merged["emotional_responses"] = existing_responses[-20:]
        
        # Update other fields
        for key, value in new.items():
            if key not in ["preferred_themes", "character_preferences", "emotional_responses"]:
                merged[key] = value
        
        merged["last_updated"] = datetime.utcnow().isoformat()
        
        return merged
    
    def clear_cache(self) -> None:
        """Clear the preference cache."""
        self.preference_cache.clear()
        self.cache_timestamps.clear()


class SessionManager(SessionManagerInterface):
    """Main session manager that coordinates all session-related operations."""
    
    def __init__(self):
        self.lifecycle_manager = SessionLifecycleManager()
        self.preference_manager = UserPreferenceManager()
    
    async def create_session(self, child_profile: ChildProfile) -> Session:
        """Create a new storytelling session."""
        
        # Load user preferences to enhance profile
        preferences = await self.preference_manager.get_user_preferences(
            child_profile.anonymous_id
        )
        
        # Enhance child profile with preferences
        enhanced_profile = self._enhance_profile_with_preferences(child_profile, preferences)
        
        return await self.lifecycle_manager.create_session(enhanced_profile)
    
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieve a session by ID."""
        return await self.lifecycle_manager.get_session(str(session_id))
    
    async def update_session_state(self, session_id: UUID, session: Session) -> None:
        """Update session state and context."""
        
        # Update session state
        await self.lifecycle_manager.update_session_state(str(session_id), session.state)
        
        # Update story context if present
        if session.story_context:
            await self.lifecycle_manager.update_session_context(str(session_id), session.story_context)
    
    async def cleanup_session_data(self, session_id: UUID) -> None:
        """Clean up session data for privacy compliance."""
        await self.lifecycle_manager.cleanup_session_data(str(session_id))
    
    async def get_user_preferences(self, anonymous_id: str) -> dict:
        """Get user preferences by anonymous ID."""
        return await self.preference_manager.get_user_preferences(anonymous_id)
    
    async def update_user_preferences(self, anonymous_id: str, preferences: dict) -> None:
        """Update user preferences."""
        await self.preference_manager.update_user_preferences(anonymous_id, preferences)
    
    def _enhance_profile_with_preferences(
        self, 
        profile: ChildProfile, 
        preferences: Dict[str, Any]
    ) -> ChildProfile:
        """Enhance child profile with stored preferences."""
        
        # Add preferred themes to profile preferences
        preferred_themes = preferences.get("preferred_themes", [])
        enhanced_preferences = list(set(profile.preferences + preferred_themes))
        
        # Get voice preference
        voice_prefs = preferences.get("voice_preferences", {})
        voice_preference = voice_prefs.get("preferred_voice", profile.voice_preference)
        
        return ChildProfile(
            age=profile.age,
            preferences=enhanced_preferences,
            emotional_goal=profile.emotional_goal,
            voice_preference=voice_preference,
            anonymous_id=profile.anonymous_id
        )
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get overall session statistics."""
        
        active_sessions = await self.lifecycle_manager.get_active_sessions()
        
        return {
            "total_active_sessions": len(active_sessions),
            "sessions_by_state": self._count_sessions_by_state(active_sessions),
            "average_session_duration": self._calculate_average_duration(active_sessions),
            "age_distribution": self._get_age_distribution(active_sessions)
        }
    
    def _count_sessions_by_state(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count sessions by state."""
        
        state_counts = {}
        for session in sessions:
            state = session["state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return state_counts
    
    def _calculate_average_duration(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate average session duration."""
        
        if not sessions:
            return 0.0
        
        total_duration = sum(session["duration_minutes"] for session in sessions)
        return total_duration / len(sessions)
    
    def _get_age_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get age distribution of active sessions."""
        
        age_groups = {"3-5": 0, "6-8": 0, "9-12": 0, "other": 0}
        
        for session in sessions:
            age = session["child_age"]
            if 3 <= age <= 5:
                age_groups["3-5"] += 1
            elif 6 <= age <= 8:
                age_groups["6-8"] += 1
            elif 9 <= age <= 12:
                age_groups["9-12"] += 1
            else:
                age_groups["other"] += 1
        
        return age_groups
    
    async def shutdown(self) -> None:
        """Shutdown session manager."""
        await self.lifecycle_manager.shutdown()