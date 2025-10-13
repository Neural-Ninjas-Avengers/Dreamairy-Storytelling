"""AWS service client wrappers with error handling and configuration."""

import json
import logging
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import get_settings
from app.utils.error_handling import (
    with_circuit_breaker, with_retry, with_fallback,
    ServiceType, handle_service_error, degradation_manager
)

logger = logging.getLogger(__name__)

class AWSClientError(Exception):
    """Custom exception for AWS client errors."""
    pass

class BedrockClient:
    """Bedrock client wrapper for story generation."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._runtime_client = None
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _get_client(self):
        """Get or create Bedrock client."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'bedrock',
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create Bedrock client: {e}")
                raise AWSClientError(f"Bedrock client initialization failed: {e}")
        return self._client
    
    def _get_runtime_client(self):
        """Get or create Bedrock Runtime client."""
        if self._runtime_client is None:
            try:
                self._runtime_client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create Bedrock Runtime client: {e}")
                raise AWSClientError(f"Bedrock Runtime client initialization failed: {e}")
        return self._runtime_client
    
    @with_circuit_breaker(ServiceType.BEDROCK.value)
    @with_retry(max_retries=2, base_delay=1.0)
    async def generate_story(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate story content using Bedrock."""
        try:
            # Prepare the request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Run the synchronous call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._invoke_model,
                json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                # Mark service as available
                degradation_manager.mark_service_available(ServiceType.BEDROCK.value)
                return response_body['content'][0]['text']
            else:
                raise AWSClientError("No content in Bedrock response")
                
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            await handle_service_error(ServiceType.BEDROCK.value, e, {"prompt": prompt[:100]})
            raise AWSClientError(f"Story generation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in story generation: {e}")
            await handle_service_error(ServiceType.BEDROCK.value, e, {"prompt": prompt[:100]})
            raise AWSClientError(f"Story generation failed: {e}")
    
    def _invoke_model(self, body: str) -> Dict[str, Any]:
        """Synchronous model invocation."""
        client = self._get_runtime_client()
        return client.invoke_model(
            modelId=self.settings.bedrock_model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List available foundation models."""
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                client.list_foundation_models
            )
            return response.get('modelSummaries', [])
        except ClientError as e:
            logger.error(f"Failed to list Bedrock models: {e}")
            raise AWSClientError(f"Model listing failed: {e}")

    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _get_client(self):
        if self._client is None:
            try:
                self._client = boto3.client(
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
        return self._client
    
    @with_retry(max_retries=2, base_delay=0.5)
    async def start_streaming_transcription(self, audio_stream: bytes, language_code: str = "en-US") -> Dict[str, Any]:
        """Start streaming transcription (simplified for demo)."""
        try:
            # For demo purposes, we'll use a simple transcription job
            # In production, you'd use the streaming API
            client = self._get_client()
            
            # This is a placeholder - real streaming would require WebSocket connection
            # For now, return a mock response structure
            response = {
                "TranscriptEvent": {
                    "Transcript": {
                        "Results": [
                            {
                                "Alternatives": [
                                    {
                                        "Transcript": "Sample transcription for demo",
                                        "Confidence": 0.95
                                    }
                                ],
                                "IsPartial": False
                            }
                        ]
                    }
                }
            }
            
            # Mark service as available
            return response
            
        except ClientError as e:
            raise AWSClientError(f"Audio transcription failed: {e}")
    
    async def analyze_audio_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment from transcript (using basic keyword analysis for demo)."""
        # This is a simplified sentiment analysis for demo purposes
        # In production, you might use Amazon Comprehend
        
        positive_words = ['happy', 'excited', 'joy', 'fun', 'great', 'love', 'wonderful']
        negative_words = ['sad', 'angry', 'upset', 'scared', 'worried', 'tired', 'bored']
        
        transcript_lower = transcript.lower()
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            confidence = min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            confidence = min(0.9, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "NEUTRAL"
            confidence = 0.6
        
        return {
            "Sentiment": sentiment,
            "SentimentScore": {
                "Positive": positive_count / max(1, positive_count + negative_count),
                "Negative": negative_count / max(1, positive_count + negative_count),
                "Neutral": 1 - (positive_count + negative_count) / max(1, positive_count + negative_count + 1)
            },
            "Confidence": confidence
        }

class RekognitionClient:
    """Rekognition client wrapper for facial emotion detection."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _get_client(self):
        """Get or create Rekognition client."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'rekognition',
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create Rekognition client: {e}")
                raise AWSClientError(f"Rekognition client initialization failed: {e}")
        return self._client
    
    async def detect_faces_and_emotions(self, image_bytes: bytes) -> Dict[str, Any]:
        """Detect faces and emotions in an image."""
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                self.executor,
                self._detect_faces,
                image_bytes
            )
            
            return response
            
        except ClientError as e:
            logger.error(f"Rekognition API error: {e}")
            raise AWSClientError(f"Face/emotion detection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in emotion detection: {e}")
            raise AWSClientError(f"Emotion detection failed: {e}")
    
    def _detect_faces(self, image_bytes: bytes) -> Dict[str, Any]:
        """Synchronous face detection."""
        client = self._get_client()
        return client.detect_faces(
            Image={'Bytes': image_bytes},
            Attributes=['ALL']
        )
    
    async def extract_primary_emotion(self, detection_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract the primary emotion from detection response."""
        try:
            if not detection_response.get('FaceDetails'):
                return None
            
            # Get the first face (assuming single child)
            face = detection_response['FaceDetails'][0]
            emotions = face.get('Emotions', [])
            
            if not emotions:
                return None
            
            # Find the emotion with highest confidence
            primary_emotion = max(emotions, key=lambda x: x['Confidence'])
            
            return {
                'emotion': primary_emotion['Type'].lower(),
                'confidence': primary_emotion['Confidence'] / 100.0,  # Convert to 0-1 scale
                'all_emotions': {
                    emotion['Type'].lower(): emotion['Confidence'] / 100.0 
                    for emotion in emotions
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting emotion: {e}")
            return None

class PollyClient:
    """Polly client wrapper for text-to-speech conversion."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _get_client(self):
        """Get or create Polly client."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'polly',
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create Polly client: {e}")
                raise AWSClientError(f"Polly client initialization failed: {e}")
        return self._client
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        output_format: str = "mp3",
        sample_rate: str = "22050"
    ) -> bytes:
        """Convert text to speech."""
        try:
            client = self._get_client()
            voice = voice_id or self.settings.polly_voice_id
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._synthesize_speech_sync,
                text, voice, output_format, sample_rate
            )
            
            # Read the audio stream
            audio_data = response['AudioStream'].read()
            return audio_data
            
        except ClientError as e:
            logger.error(f"Polly API error: {e}")
            raise AWSClientError(f"Speech synthesis failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in speech synthesis: {e}")
            raise AWSClientError(f"Speech synthesis failed: {e}")
    
    def _synthesize_speech_sync(self, text: str, voice_id: str, output_format: str, sample_rate: str):
        """Synchronous speech synthesis."""
        client = self._get_client()
        return client.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_id,
            SampleRate=sample_rate
        )
    
    async def list_available_voices(self, language_code: str = "en-US") -> List[Dict[str, Any]]:
        """List available voices for a language."""
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                self.executor,
                client.describe_voices,
                LanguageCode=language_code
            )
            
            return response.get('Voices', [])
            
        except ClientError as e:
            logger.error(f"Failed to list Polly voices: {e}")
            raise AWSClientError(f"Voice listing failed: {e}")
    
    async def create_ssml_text(self, text: str, emotion: str = "neutral", rate: str = "medium") -> str:
        """Create SSML formatted text for emotional speech."""
        # Map emotions to SSML prosody attributes
        emotion_mapping = {
            "excited": {"rate": "fast", "pitch": "high", "volume": "loud"},
            "calm": {"rate": "slow", "pitch": "low", "volume": "soft"},
            "happy": {"rate": "medium", "pitch": "high", "volume": "medium"},
            "sad": {"rate": "slow", "pitch": "low", "volume": "soft"},
            "neutral": {"rate": "medium", "pitch": "medium", "volume": "medium"}
        }
        
        prosody = emotion_mapping.get(emotion, emotion_mapping["neutral"])
        
        ssml = f"""<speak>
            <prosody rate="{prosody['rate']}" pitch="{prosody['pitch']}" volume="{prosody['volume']}">
                {text}
            </prosody>
        </speak>"""
        
        return ssml

class S3Client:
    """S3 client wrapper for story templates and preference storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.bucket_name = self.settings.s3_bucket_name
    
    def _get_client(self):
        """Get or create S3 client."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    's3',
                    region_name=self.settings.aws_region,
                    aws_access_key_id=self.settings.aws_access_key_id,
                    aws_secret_access_key=self.settings.aws_secret_access_key,
                    aws_session_token=self.settings.aws_session_token
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise AWSClientError(f"S3 client initialization failed: {e}")
        return self._client
    
    async def store_user_preferences(self, anonymous_id: str, preferences: Dict[str, Any]) -> bool:
        """Store user preferences in S3."""
        if not self.bucket_name:
            logger.warning("S3 bucket not configured, skipping preference storage")
            return False
        
        try:
            client = self._get_client()
            key = f"preferences/{anonymous_id}.json"
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._put_object,
                key, json.dumps(preferences)
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to store preferences: {e}")
            return False
    
    async def get_user_preferences(self, anonymous_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user preferences from S3."""
        if not self.bucket_name:
            return None
        
        try:
            client = self._get_client()
            key = f"preferences/{anonymous_id}.json"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._get_object,
                key
            )
            
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Failed to retrieve preferences: {e}")
            return None
    
    async def store_story_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Store a story template in S3."""
        if not self.bucket_name:
            logger.warning("S3 bucket not configured, skipping template storage")
            return False
        
        try:
            client = self._get_client()
            key = f"templates/{template_id}.json"
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._put_object,
                key, json.dumps(template_data)
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to store template: {e}")
            return False
    
    async def get_story_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a story template from S3."""
        if not self.bucket_name:
            return None
        
        try:
            client = self._get_client()
            key = f"templates/{template_id}.json"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self._get_object,
                key
            )
            
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Failed to retrieve template: {e}")
            return None
    
    async def delete_user_data(self, anonymous_id: str) -> bool:
        """Delete all user data for privacy compliance."""
        if not self.bucket_name:
            return True
        
        try:
            client = self._get_client()
            
            # List all objects with the user's prefix
            prefix = f"preferences/{anonymous_id}"
            loop = asyncio.get_event_loop()
            
            # Delete preferences
            try:
                await loop.run_in_executor(
                    self.executor,
                    self._delete_object,
                    f"{prefix}.json"
                )
            except ClientError:
                pass  # Object might not exist
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete user data: {e}")
            return False
    
    def _put_object(self, key: str, body: str):
        """Synchronous put object."""
        client = self._get_client()
        return client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            ContentType='application/json'
        )
    
    def _get_object(self, key: str):
        """Synchronous get object."""
        client = self._get_client()
        return client.get_object(Bucket=self.bucket_name, Key=key)
    
    def _delete_object(self, key: str):
        """Synchronous delete object."""
        client = self._get_client()
        return client.delete_object(Bucket=self.bucket_name, Key=key)

# Global client instances - will be mock or real based on config
def _get_client_instance(client_class, mock_client):
    """Get client instance based on configuration."""
    settings = get_settings()
    if settings.use_mock_services or settings.offline_mode:
        return mock_client
    return client_class()

# Import mock clients
from app.services.mock_services import (
    mock_polly_client, mock_s3_client
)

# Initialize clients based on configuration
bedrock_client = _get_client_instance(BedrockClient, mock_bedrock_client)
rekognition_client = _get_client_instance(RekognitionClient, mock_rekognition_client)
polly_client = _get_client_instance(PollyClient, mock_polly_client)
s3_client = _get_client_instance(S3Client, mock_s3_client)