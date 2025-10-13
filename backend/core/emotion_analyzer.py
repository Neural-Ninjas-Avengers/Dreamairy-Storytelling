"""
Emotion analysis using only Rekognition (Transcribe removed - not in allowed services)
"""

import logging
from typing import Dict, Any, Optional, List
from app.core.interfaces import EmotionAnalyzerInterface
from app.models.core import EmotionResult, EmotionState, EmotionType, EmotionSource
from app.services.aws_clients import rekognition_client

logger = logging.getLogger(__name__)

class AudioEmotionDetector:
    """Detects emotions from audio input using only Rekognition for image analysis."""
    
    def __init__(self):
        self.rekognition = rekognition_client
    
    async def analyze_audio_emotion(self, audio_data: bytes, context: Dict[str, Any] = None) -> EmotionResult:
        """
        Analyze emotion from audio - simplified to return neutral since Transcribe is not available.
        """
        try:
            # Since Transcribe is not available, return neutral emotion
            # In a real implementation, you could use other audio processing libraries
            
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.5,
                source=EmotionSource.AUDIO,
                metadata={
                    "method": "fallback",
                    "reason": "transcribe_not_available",
                    "audio_size": len(audio_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Audio emotion analysis failed: {e}")
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.0,
                source=EmotionSource.AUDIO,
                metadata={"error": str(e)}
            )

class EmotionAnalyzer(EmotionAnalyzerInterface):
    """Main emotion analyzer using only allowed AWS services."""
    
    def __init__(self):
        self.audio_detector = AudioEmotionDetector()
        self.rekognition = rekognition_client
    
    async def analyze_emotion(self, 
                            text: Optional[str] = None,
                            audio_data: Optional[bytes] = None,
                            image_data: Optional[bytes] = None,
                            context: Dict[str, Any] = None) -> EmotionResult:
        """Analyze emotion from available inputs using only Rekognition."""
        
        try:
            # Prioritize image analysis since Rekognition works well for that
            if image_data:
                return await self._analyze_image_emotion(image_data, context)
            
            # For audio, use simplified detection
            if audio_data:
                return await self.audio_detector.analyze_audio_emotion(audio_data, context)
            
            # For text, return neutral (could implement text sentiment analysis later)
            if text:
                return EmotionResult(
                    emotion=EmotionType.NEUTRAL,
                    confidence=0.5,
                    source=EmotionSource.TEXT,
                    metadata={"method": "text_fallback", "text_length": len(text)}
                )
            
            # Default fallback
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.0,
                source=EmotionSource.UNKNOWN,
                metadata={"reason": "no_input_provided"}
            )
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.0,
                source=EmotionSource.UNKNOWN,
                metadata={"error": str(e)}
            )
    
    async def _analyze_image_emotion(self, image_data: bytes, context: Dict[str, Any] = None) -> EmotionResult:
        """Analyze emotion from image using Rekognition."""
        
        try:
            # Use Rekognition to detect faces and emotions
            result = await self.rekognition.detect_faces_with_emotions(image_data)
            
            if result.get('faces') and len(result['faces']) > 0:
                # Get the most confident emotion from the first face
                face = result['faces'][0]
                emotions = face.get('emotions', [])
                
                if emotions:
                    # Find the emotion with highest confidence
                    top_emotion = max(emotions, key=lambda x: x.get('confidence', 0))
                    
                    emotion_name = top_emotion.get('type', 'NEUTRAL').upper()
                    confidence = top_emotion.get('confidence', 0) / 100.0
                    
                    # Map Rekognition emotions to our EmotionType
                    emotion_mapping = {
                        'HAPPY': EmotionType.JOY,
                        'SAD': EmotionType.SADNESS,
                        'ANGRY': EmotionType.ANGER,
                        'SURPRISED': EmotionType.SURPRISE,
                        'FEAR': EmotionType.FEAR,
                        'DISGUSTED': EmotionType.DISGUST,
                        'CALM': EmotionType.NEUTRAL,
                        'CONFUSED': EmotionType.NEUTRAL
                    }
                    
                    emotion_type = emotion_mapping.get(emotion_name, EmotionType.NEUTRAL)
                    
                    return EmotionResult(
                        emotion=emotion_type,
                        confidence=confidence,
                        source=EmotionSource.IMAGE,
                        metadata={
                            "rekognition_emotion": emotion_name,
                            "face_count": len(result['faces']),
                            "all_emotions": emotions
                        }
                    )
            
            # No faces detected
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.0,
                source=EmotionSource.IMAGE,
                metadata={"reason": "no_faces_detected"}
            )
            
        except Exception as e:
            logger.error(f"Image emotion analysis failed: {e}")
            return EmotionResult(
                emotion=EmotionType.NEUTRAL,
                confidence=0.0,
                source=EmotionSource.IMAGE,
                metadata={"error": str(e)}
            )
