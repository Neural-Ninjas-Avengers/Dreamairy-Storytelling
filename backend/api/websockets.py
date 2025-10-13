"""WebSocket endpoints for real-time storytelling communication."""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, Set
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, ValidationError

from app.core.story_orchestrator import StoryOrchestrator
from app.models.core import EmotionType, EmotionalGoal

logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = StoryOrchestrator()

# WebSocket router
ws_router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}
session_connections: Dict[str, str] = {}  # session_id -> connection_id


# WebSocket Message Models
class WSMessage(BaseModel):
    """Base WebSocket message model."""
    type: str
    session_id: Optional[str] = None
    data: Dict[str, Any] = {}


class EmotionUpdateMessage(BaseModel):
    """WebSocket message for emotion updates."""
    type: str = "emotion_update"
    session_id: str
    emotion: EmotionType
    confidence: float
    intensity: float
    source: str = "websocket"


class StoryRequestMessage(BaseModel):
    """WebSocket message for story requests."""
    type: str = "story_request"
    session_id: str
    action: str  # "start", "continue", "conclude"
    theme: Optional[str] = None


class AudioChunkMessage(BaseModel):
    """WebSocket message for audio chunks."""
    type: str = "audio_chunk"
    session_id: str
    chunk_data: str  # Base64 encoded audio data
    chunk_index: int


class ConnectionManager:
    """Manages WebSocket connections and message routing."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}
        self.connection_sessions: Dict[str, str] = {}  # connection_id -> session_id
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection."""
        # Clean up connection mappings
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if connection_id in self.connection_sessions:
            session_id = self.connection_sessions[connection_id]
            if session_id in self.session_connections:
                del self.session_connections[session_id]
            del self.connection_sessions[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    def associate_session(self, connection_id: str, session_id: str) -> None:
        """Associate a connection with a session."""
        self.session_connections[session_id] = connection_id
        self.connection_sessions[connection_id] = session_id
        logger.info(f"Associated connection {connection_id} with session {session_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str) -> None:
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_session_message(self, message: Dict[str, Any], session_id: str) -> None:
        """Send a message to a session's connection."""
        if session_id in self.session_connections:
            connection_id = self.session_connections[session_id]
            await self.send_personal_message(message, connection_id)
    
    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connections."""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)


# Global connection manager
manager = ConnectionManager()


class WebSocketHandler:
    """Handles WebSocket message processing and responses."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.message_handlers = {
            "session_create": self._handle_session_create,
            "session_join": self._handle_session_join,
            "emotion_update": self._handle_emotion_update,
            "story_request": self._handle_story_request,
            "audio_chunk": self._handle_audio_chunk,
            "ping": self._handle_ping
        }
    
    async def handle_message(self, websocket: WebSocket, connection_id: str, message_data: str) -> None:
        """Handle incoming WebSocket message."""
        
        try:
            # Parse message
            message_dict = json.loads(message_data)
            message_type = message_dict.get("type")
            
            if message_type not in self.message_handlers:
                await self._send_error(connection_id, f"Unknown message type: {message_type}")
                return
            
            # Handle message
            handler = self.message_handlers[message_type]
            await handler(connection_id, message_dict)
            
        except json.JSONDecodeError:
            await self._send_error(connection_id, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_error(connection_id, f"Message processing error: {str(e)}")
    
    async def _handle_session_create(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle session creation request."""
        
        try:
            data = message.get("data", {})
            
            # Create child profile
            from app.models.core import ChildProfile
            child_profile = ChildProfile(
                age=data.get("age", 6),
                preferences=data.get("preferences", []),
                emotional_goal=EmotionalGoal(data.get("emotional_goal", "entertain")),
                voice_preference=data.get("voice_preference")
            )
            
            # Create session
            session_id = await orchestrator.start_session(child_profile)
            
            # Associate connection with session
            self.manager.associate_session(connection_id, str(session_id))
            
            # Send success response
            await self.manager.send_personal_message({
                "type": "session_created",
                "session_id": str(session_id),
                "status": "success",
                "message": "Session created successfully"
            }, connection_id)
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to create session: {str(e)}")
    
    async def _handle_session_join(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle session join request."""
        
        try:
            session_id = message.get("session_id")
            if not session_id:
                await self._send_error(connection_id, "Session ID is required")
                return
            
            # Verify session exists
            session = await orchestrator.session_manager.get_session(UUID(session_id))
            if not session:
                await self._send_error(connection_id, "Session not found")
                return
            
            # Associate connection with session
            self.manager.associate_session(connection_id, session_id)
            
            # Send session status
            status = await orchestrator.get_session_status(UUID(session_id))
            
            await self.manager.send_personal_message({
                "type": "session_joined",
                "session_id": session_id,
                "status": "success",
                "session_status": status
            }, connection_id)
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to join session: {str(e)}")
    
    async def _handle_emotion_update(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle emotion update from client."""
        
        try:
            data = message.get("data", {})
            session_id = message.get("session_id")
            
            if not session_id:
                await self._send_error(connection_id, "Session ID is required")
                return
            
            # Create emotion result
            from app.models.core import EmotionResult, EmotionState, EmotionSource
            from datetime import datetime
            
            emotion_state = EmotionState(
                primary_emotion=EmotionType(data.get("emotion", "neutral")),
                confidence=data.get("confidence", 0.5),
                intensity=data.get("intensity", 0.5),
                timestamp=datetime.utcnow(),
                source=EmotionSource.COMBINED
            )
            
            emotion_result = EmotionResult(
                emotion_state=emotion_state,
                raw_data={"source": "websocket"},
                processing_time=0.0
            )
            
            # Process emotion update
            adaptation_action = await orchestrator.process_emotion_update(
                UUID(session_id), emotion_result
            )
            
            # Send response
            await self.manager.send_personal_message({
                "type": "emotion_processed",
                "session_id": session_id,
                "adaptation": {
                    "action_type": adaptation_action.action_type,
                    "reason": adaptation_action.reason,
                    "confidence": adaptation_action.confidence
                } if adaptation_action else None
            }, connection_id)
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to process emotion: {str(e)}")
    
    async def _handle_story_request(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle story generation request."""
        
        try:
            data = message.get("data", {})
            session_id = message.get("session_id")
            action = data.get("action", "start")
            
            logger.info(f"Processing story request: session_id={session_id}, action={action}")
            
            if not session_id:
                await self._send_error(connection_id, "Session ID is required")
                return
            
            if action == "start":
                # Start new story
                theme = data.get("theme", "adventure")
                
                # Check if orchestration exists, if not this means session wasn't properly created
                if session_id not in orchestrator.active_orchestrations:
                    logger.error(f"No orchestration found for session {session_id}. Active orchestrations: {list(orchestrator.active_orchestrations.keys())}")
                    await self._send_error(connection_id, "Session not properly initialized. Please create a session first.")
                    return
                
                logger.info(f"Found orchestration for session {session_id}")
                
                # Get the session
                orchestration = orchestrator.active_orchestrations[session_id]
                session = orchestration["session"]
                
                # Create or update story context
                from app.models.core import StoryContext
                story_context = StoryContext(
                    session_id=UUID(session_id),
                    theme=theme,
                    target_age=session.child_profile.age
                )
                
                # Update session with story context
                session.story_context = story_context
                await orchestrator.session_manager.update_session_state(UUID(session_id), session)
                
                # Generate story segment
                segment = await orchestrator.generate_story_segment(UUID(session_id), story_context)
                
                await self.manager.send_personal_message({
                    "type": "story_segment",
                    "session_id": session_id,
                    "segment": {
                        "text": segment.text,
                        "emotional_tone": segment.emotional_tone,
                        "pacing": segment.pacing,
                        "characters": segment.characters_involved,
                        "sequence_number": segment.sequence_number,
                        "illustration": segment.illustration
                    }
                }, connection_id)
            
            elif action == "continue":
                # Continue existing story
                session = await orchestrator.session_manager.get_session(UUID(session_id))
                if not session or not session.story_context:
                    await self._send_error(connection_id, "No active story found")
                    return
                
                segment = await orchestrator.generate_story_segment(UUID(session_id), session.story_context)
                
                await self.manager.send_personal_message({
                    "type": "story_segment",
                    "session_id": session_id,
                    "segment": {
                        "text": segment.text,
                        "emotional_tone": segment.emotional_tone,
                        "pacing": segment.pacing,
                        "characters": segment.characters_involved,
                        "sequence_number": segment.sequence_number,
                        "illustration": segment.illustration
                    }
                }, connection_id)
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to process story request: {str(e)}")
    
    async def _handle_audio_chunk(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle audio chunk for emotion detection."""
        
        try:
            data = message.get("data", {})
            session_id = message.get("session_id")
            
            if not session_id:
                await self._send_error(connection_id, "Session ID is required")
                return
            
            # Decode audio data
            import base64
            chunk_data = data.get("chunk_data", "")
            audio_bytes = base64.b64decode(chunk_data)
            
            # Process audio emotion
            adaptation_action = await orchestrator.process_multimodal_input(
                UUID(session_id), audio_data=audio_bytes
            )
            
            # Send response
            await self.manager.send_personal_message({
                "type": "audio_processed",
                "session_id": session_id,
                "chunk_index": data.get("chunk_index", 0),
                "adaptation": {
                    "action_type": adaptation_action.action_type,
                    "reason": adaptation_action.reason,
                    "confidence": adaptation_action.confidence
                } if adaptation_action else None
            }, connection_id)
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to process audio chunk: {str(e)}")
    
    async def _handle_ping(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle ping message for connection health check."""
        
        await self.manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, connection_id)
    
    async def _send_error(self, connection_id: str, error_message: str) -> None:
        """Send error message to client."""
        
        await self.manager.send_personal_message({
            "type": "error",
            "message": error_message
        }, connection_id)


# Global WebSocket handler
ws_handler = WebSocketHandler(manager)


@ws_router.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """Main WebSocket endpoint for real-time storytelling communication."""
    
    await manager.connect(websocket, connection_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "connection_id": connection_id,
            "message": "Connected to Adaptive Storytelling Agent"
        }, connection_id)
        
        # Message handling loop
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                
                # Handle message
                await ws_handler.handle_message(websocket, connection_id, data)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for connection {connection_id}: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Processing error: {str(e)}"
                }, connection_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        manager.disconnect(connection_id)


@ws_router.websocket("/ws/audio/{session_id}")
async def audio_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time audio streaming."""
    
    await websocket.accept()
    
    try:
        # Verify session exists
        session = await orchestrator.session_manager.get_session(UUID(session_id))
        if not session:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Session not found"
            }))
            return
        
        # Send initial message
        await websocket.send_text(json.dumps({
            "type": "audio_stream_started",
            "session_id": session_id
        }))
        
        # Stream audio chunks
        try:
            async for audio_chunk in orchestrator.get_audio_stream(UUID(session_id)):
                if audio_chunk:
                    # Encode audio chunk as base64
                    import base64
                    encoded_chunk = base64.b64encode(audio_chunk).decode('utf-8')
                    
                    await websocket.send_text(json.dumps({
                        "type": "audio_chunk",
                        "session_id": session_id,
                        "data": encoded_chunk
                    }))
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Audio streaming error: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Audio streaming error: {str(e)}"
            }))
    
    except WebSocketDisconnect:
        logger.info(f"Audio WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"Audio WebSocket error: {e}")
    finally:
        await websocket.close()


# WebSocket utility functions
async def notify_session_update(session_id: str, update_data: Dict[str, Any]) -> None:
    """Notify a session about updates via WebSocket."""
    
    await manager.send_session_message({
        "type": "session_update",
        "session_id": session_id,
        "data": update_data
    }, session_id)


async def broadcast_system_message(message: str, message_type: str = "system") -> None:
    """Broadcast a system message to all connected clients."""
    
    await manager.broadcast_message({
        "type": message_type,
        "message": message,
        "timestamp": asyncio.get_event_loop().time()
    })


# Connection statistics
@ws_router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    
    return {
        "active_connections": len(manager.active_connections),
        "session_connections": len(manager.session_connections),
        "connections": list(manager.active_connections.keys()),
        "sessions": list(manager.session_connections.keys())
    }