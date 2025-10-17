#!/usr/bin/env python3
"""
AWS Connector for DreamAIry Admin Module
Handles AWS service integration and testing
"""

import json
import base64
import logging
import io
from datetime import datetime
from typing import Dict, Any, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

class AWSConnector:
    """AWS service connector and testing utilities"""
    
    # Class-level rate limiting
    _last_bedrock_call = None
    _min_delay_between_calls = 3.0  # Minimum 3 seconds between Bedrock calls (increased for throttling)
    
    def __init__(self, credentials: Dict[str, str]):
        """Initialize AWS connector with credentials"""
        self.credentials = credentials
        self.region = credentials.get('region', 'eu-west-1')
        
        # Initialize clients lazily
        self._bedrock_client = None
        self._polly_client = None
        self._rekognition_client = None
        self._s3_client = None
        self._dynamodb_client = None
    
    def _rate_limit_bedrock(self):
        """Enforce rate limiting for Bedrock API calls"""
        import time
        
        if AWSConnector._last_bedrock_call is not None:
            elapsed = time.time() - AWSConnector._last_bedrock_call
            if elapsed < self._min_delay_between_calls:
                sleep_time = self._min_delay_between_calls - elapsed
                logger.debug(f"⏱️ Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        AWSConnector._last_bedrock_call = time.time()
    
    def _get_boto3_session(self):
        """Get boto3 session with credentials"""
        try:
            import boto3
            return boto3.Session(
                aws_access_key_id=self.credentials['accessKeyId'],
                aws_secret_access_key=self.credentials['secretAccessKey'],
                region_name=self.region
            )
        except Exception as e:
            logger.error(f"Failed to create boto3 session: {e}")
            raise
    
    def _get_bedrock_client(self):
        """Get Bedrock client"""
        if not self._bedrock_client:
            try:
                session = self._get_boto3_session()
                self._bedrock_client = session.client('bedrock-runtime', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create Bedrock client: {e}")
                raise
        return self._bedrock_client
    
    def _get_polly_client(self):
        """Get Polly client"""
        if not self._polly_client:
            try:
                session = self._get_boto3_session()
                self._polly_client = session.client('polly', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create Polly client: {e}")
                raise
        return self._polly_client
    
    def _get_rekognition_client(self):
        """Get Rekognition client"""
        if not self._rekognition_client:
            try:
                session = self._get_boto3_session()
                self._rekognition_client = session.client('rekognition', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create Rekognition client: {e}")
                raise
        return self._rekognition_client
    
    def _get_s3_client(self):
        """Get S3 client"""
        if not self._s3_client:
            try:
                session = self._get_boto3_session()
                self._s3_client = session.client('s3', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise
        return self._s3_client
    
    def _get_dynamodb_client(self):
        """Get DynamoDB client"""
        if not self._dynamodb_client:
            try:
                session = self._get_boto3_session()
                self._dynamodb_client = session.client('dynamodb', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create DynamoDB client: {e}")
                raise
        return self._dynamodb_client
    
    def _get_voice_engine(self, voice_id: str) -> str:
        """Determine the best engine for a given voice ID"""
        # Neural voices (support neural engine)
        neural_voices = {
            # English neural voices
            'Joanna', 'Matthew', 'Amy', 'Brian', 'Emma', 'Olivia', 'Aria', 'Ayanda',
            'Ivy', 'Kendra', 'Kimberly', 'Salli', 'Joey', 'Justin', 'Kevin', 'Ruth',
            # Spanish neural voices
            'Lucia', 'Mia', 'Lupe',
            # Other languages with neural support
            'Camila', 'Gabrielle', 'Vicki', 'Seoyeon', 'Takumi', 'Kazuha', 'Tomoko'
        }
        
        # Standard-only voices (only support standard engine)
        standard_voices = {
            # Spanish standard voices
            'Enrique', 'Conchita', 'Miguel', 'Penelope',
            # English standard voices
            'Geraint', 'Nicole', 'Russell', 'Marlene', 'Hans', 'Naja', 'Mads',
            # Other standard voices
            'Carla', 'Giorgio', 'Mizuki', 'Chit', 'Dora', 'Karl', 'Liv'
        }
        
        if voice_id in neural_voices:
            return 'neural'
        elif voice_id in standard_voices:
            return 'standard'
        else:
            # Default to standard for unknown voices to avoid errors
            logger.warning(f"Unknown voice {voice_id}, defaulting to standard engine")
            return 'standard'
    
    def test_bedrock(self, model_id=None) -> Dict[str, Any]:
        """Test Bedrock service connectivity and functionality"""
        try:
            start_time = datetime.now()
            
            client = self._get_bedrock_client()
            
            # Use provided model_id or default to a more accessible one
            if not model_id:
                model_id = "amazon.titan-text-express-v1"  # More accessible default
            
            # Test with a simple prompt
            test_prompt = "Tell me a very short story about a happy rabbit."
            
            # Prepare request body based on model type
            if "anthropic.claude" in model_id:
                # Anthropic Claude format
                body = json.dumps({
                    "prompt": f"\\n\\nHuman: {test_prompt}\\n\\nAssistant:",
                    "max_tokens_to_sample": 100,
                    "temperature": 0.7,
                    "top_p": 1,
                })
            elif "amazon.titan" in model_id:
                # Amazon Titan format
                body = json.dumps({
                    "inputText": test_prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 100,
                        "temperature": 0.7,
                        "topP": 1
                    }
                })
            elif "meta.llama" in model_id:
                # Meta Llama format
                body = json.dumps({
                    "prompt": test_prompt,
                    "max_gen_len": 100,
                    "temperature": 0.7,
                    "top_p": 1
                })
            elif "ai21.j2" in model_id:
                # AI21 Jurassic format
                body = json.dumps({
                    "prompt": test_prompt,
                    "maxTokens": 100,
                    "temperature": 0.7,
                    "topP": 1
                })
            elif "cohere.command" in model_id:
                # Cohere Command format
                body = json.dumps({
                    "prompt": test_prompt,
                    "max_tokens": 100,
                    "temperature": 0.7,
                    "p": 1
                })
            else:
                # Generic format (fallback)
                body = json.dumps({
                    "prompt": test_prompt,
                    "max_tokens": 100,
                    "temperature": 0.7
                })
            
            response = client.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Extract text based on model type
            if "anthropic.claude" in model_id:
                output_text = response_body.get('completion', '')
            elif "amazon.titan" in model_id:
                results = response_body.get('results', [])
                output_text = results[0].get('outputText', '') if results else ''
            elif "meta.llama" in model_id:
                output_text = response_body.get('generation', '')
            elif "ai21.j2" in model_id:
                completions = response_body.get('completions', [])
                output_text = completions[0].get('data', {}).get('text', '') if completions else ''
            elif "cohere.command" in model_id:
                generations = response_body.get('generations', [])
                output_text = generations[0].get('text', '') if generations else ''
            else:
                # Try common response fields
                output_text = (response_body.get('completion') or 
                             response_body.get('text') or 
                             response_body.get('generated_text') or 
                             str(response_body))
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "service": "bedrock",
                "response_time": response_time,
                "model_used": model_id,
                "test_output": output_text[:100] + "..." if len(output_text) > 100 else output_text,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bedrock test failed with model {model_id}: {e}")
            return {
                "success": False,
                "service": "bedrock",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_polly(self) -> Dict[str, Any]:
        """Test Polly service connectivity and functionality"""
        try:
            start_time = datetime.now()
            
            client = self._get_polly_client()
            
            # Test with simple text
            test_text = "Hello, this is a test of Amazon Polly text to speech service."
            
            response = client.synthesize_speech(
                Text=test_text,
                OutputFormat='mp3',
                VoiceId='Joanna',
                Engine='neural'
            )
            
            # Get audio stream size as a basic test
            audio_stream = response['AudioStream']
            audio_data = audio_stream.read()
            audio_size = len(audio_data)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "service": "polly",
                "response_time": response_time,
                "voice_used": "Joanna",
                "audio_size_bytes": audio_size,
                "test_text": test_text,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Polly test failed: {e}")
            return {
                "success": False,
                "service": "polly",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_rekognition(self) -> Dict[str, Any]:
        """Test Rekognition service connectivity and functionality"""
        try:
            start_time = datetime.now()
            
            client = self._get_rekognition_client()
            
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            )
            
            # Test face detection (will likely find no faces, but tests connectivity)
            response = client.detect_faces(
                Image={'Bytes': test_image_data},
                Attributes=['ALL']
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "service": "rekognition",
                "response_time": response_time,
                "faces_detected": len(response.get('FaceDetails', [])),
                "test_completed": True,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Rekognition test failed: {e}")
            return {
                "success": False,
                "service": "rekognition",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_s3(self) -> Dict[str, Any]:
        """Test S3 service connectivity and functionality"""
        try:
            start_time = datetime.now()
            
            client = self._get_s3_client()
            
            # List buckets as a basic connectivity test
            response = client.list_buckets()
            
            buckets = response.get('Buckets', [])
            bucket_count = len(buckets)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "service": "s3",
                "response_time": response_time,
                "buckets_accessible": bucket_count,
                "test_completed": True,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"S3 test failed: {e}")
            return {
                "success": False,
                "service": "s3",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_dynamodb(self) -> Dict[str, Any]:
        """Test DynamoDB service connectivity and functionality"""
        try:
            start_time = datetime.now()
            
            client = self._get_dynamodb_client()
            
            # List tables as a basic connectivity test
            response = client.list_tables()
            
            tables = response.get('TableNames', [])
            table_count = len(tables)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "service": "dynamodb",
                "response_time": response_time,
                "tables_accessible": table_count,
                "test_completed": True,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"DynamoDB test failed: {e}")
            return {
                "success": False,
                "service": "dynamodb",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_story_with_bedrock(self, prompt: str, max_tokens: int = 1000) -> Tuple[bool, str]:
        """Generate story using Bedrock with Claude 3.5 Sonnet with retry logic for throttling"""
        import time
        
        max_retries = 4  # Increased from 3 to 4
        base_delay = 5  # Increased from 2 to 5 seconds for better throttling handling
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before making the call
                self._rate_limit_bedrock()
                
                client = self._get_bedrock_client()
                
                # Use Claude 3.5 Sonnet - MUCH better for creative storytelling
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": 0.8,  # Higher temperature for more creativity
                    "top_p": 0.9,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
                
                # Use Claude 3 Sonnet - excellent for creative storytelling
                response = client.invoke_model(
                    body=body,
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Claude 3 Sonnet
                    accept="application/json",
                    contentType="application/json"
                )
                
                response_body = json.loads(response.get('body').read())
                story_text = response_body.get('content', [{}])[0].get('text', '').strip()
                
                logger.info("✨ Story generated successfully with Claude 3 Sonnet")
                return True, story_text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a throttling error
                if 'ThrottlingException' in error_str or 'Too many requests' in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 5s, 10s, 20s, 40s
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"⏳ Throttling detected (attempt {attempt + 1}/{max_retries}), waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.warning(f"⚠️ Max retries ({max_retries}) reached for Claude after throttling, using Titan fallback")
                else:
                    logger.error(f"❌ Claude 3 Sonnet story generation failed: {e}")
                
                # Fallback to Titan if Claude fails or max retries reached
                try:
                    logger.info("🔄 Falling back to Titan Text Express...")
                    body = json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": max_tokens,
                            "temperature": 0.7,
                            "topP": 0.9,
                            "stopSequences": []
                        }
                    })
                    
                    response = client.invoke_model(
                        body=body,
                        modelId="amazon.titan-text-express-v1",
                        accept="application/json",
                        contentType="application/json"
                    )
                    
                    response_body = json.loads(response.get('body').read())
                    story_text = response_body.get('results', [{}])[0].get('outputText', '').strip()
                    
                    logger.info("✅ Story generated with Titan (fallback)")
                    return True, story_text
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error}")
                return False, f"Error: {str(e)}"
    
    def synthesize_speech_with_polly(self, text: str, voice_id: str = "Joanna") -> Tuple[bool, bytes]:
        """Synthesize speech using Polly"""
        try:
            client = self._get_polly_client()
            
            response = client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural'
            )
            
            audio_data = response['AudioStream'].read()
            
            logger.info("Speech synthesized successfully with Polly")
            return True, audio_data
            
        except Exception as e:
            logger.error(f"Polly speech synthesis failed: {e}")
            return False, b""
    
    def detect_faces(self, image_bytes: bytes) -> Tuple[bool, list]:
        """Detect faces and get age/gender using Rekognition"""
        try:
            client = self._get_rekognition_client()
            
            response = client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            faces = response.get('FaceDetails', [])
            logger.info(f"Rekognition detected {len(faces)} faces")
            return True, faces
            
        except Exception as e:
            logger.error(f"Rekognition face detection failed: {e}")
            return False, []
    
    def analyze_emotion_with_rekognition(self, image_bytes: bytes) -> Tuple[bool, Dict]:
        """Analyze emotions using Rekognition"""
        try:
            client = self._get_rekognition_client()
            
            response = client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['EMOTIONS']
            )
            
            faces = response.get('FaceDetails', [])
            
            if faces:
                emotions = faces[0].get('Emotions', [])
                # Get the emotion with highest confidence
                if emotions:
                    top_emotion = max(emotions, key=lambda x: x['Confidence'])
                    result = {
                        "emotion": top_emotion['Type'].lower(),
                        "confidence": top_emotion['Confidence'] / 100.0,
                        "all_emotions": emotions
                    }
                else:
                    result = {"emotion": "neutral", "confidence": 0.5, "all_emotions": []}
            else:
                result = {"emotion": "neutral", "confidence": 0.0, "all_emotions": []}
            
            logger.info("Emotion analysis completed with Rekognition")
            return True, result
            
        except Exception as e:
            logger.error(f"Rekognition emotion analysis failed: {e}")
            return False, {"emotion": "neutral", "confidence": 0.0, "error": str(e)}
    
    def generate_image_with_titan(self, prompt: str, style: str = "photographic") -> Tuple[bool, str, str]:
        """Generate image using Amazon Nova Canvas"""
        try:
            # Apply rate limiting before making the call
            self._rate_limit_bedrock()
            
            start_time = datetime.now()
            
            # Validate prompt length
            if len(prompt) > 1024:
                logger.warning(f"Prompt too long ({len(prompt)} chars), truncating to 1024")
                prompt = prompt[:1021] + "..."
            
            logger.info(f"Generating image with Amazon Nova Canvas: prompt length = {len(prompt)} chars")
            
            client = self._get_bedrock_client()
            
            # Prepare request body for Amazon Nova Canvas
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": "blurry, low quality, distorted, scary, violent, inappropriate, adult content, dark themes, realistic photography, amateur art, sketch, unfinished, watermark, text, words"
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 8.0,
                    "seed": 42,
                    "quality": "premium"
                }
            })
            
            response = client.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Extract image data from Nova Canvas response
            images = response_body.get('images', [])
            if images and len(images) > 0:
                image_data = images[0]  # Nova Canvas returns base64 directly
                
                # Convert to base64 data URL
                image_url = f"data:image/png;base64,{image_data}"
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                logger.info(f"Amazon Nova Canvas image generated successfully in {response_time:.2f}s")
                return True, image_url, f"Generated in {response_time:.2f}s"
            else:
                return False, "", "No image data in response"
                
        except Exception as e:
            logger.error(f"Amazon Nova Canvas image generation failed: {e}")
            return False, "", str(e)
    
    def generate_storybook_avatar_with_titan(self, user_photo_base64: str, scene_description: str, child_age: int) -> Tuple[bool, str, str]:
        """Generate professional storybook avatar using user photo as input with Titan Image Generator"""
        try:
            start_time = datetime.now()
            
            client = self._get_bedrock_client()
            
            # Extract base64 data from data URL if needed
            if user_photo_base64.startswith('data:image'):
                # Remove data URL prefix to get pure base64
                user_photo_base64 = user_photo_base64.split(',')[1]
            
            # Resize image to meet AWS Bedrock requirements (height between 320 and 4096)
            user_photo_base64 = self._resize_image_for_bedrock(user_photo_base64)
            
            # Create age-appropriate transformation prompt
            if child_age <= 5:
                style_desc = "cute toddler character, soft colors, gentle features"
            elif child_age <= 8:
                style_desc = "cheerful child character, bright colors, friendly expression"
            elif child_age <= 12:
                style_desc = "adventurous young character, vibrant colors, confident pose"
            else:
                style_desc = "brave young hero, rich colors, determined expression"
            
            # Create prompt for storybook transformation
            transformation_prompt = f"Transform into a {style_desc} in professional children's book illustration style. Disney/Pixar quality, magical storybook art, award-winning illustration"
            
            # Ensure prompt doesn't exceed 512 characters
            if len(transformation_prompt) > 512:
                transformation_prompt = transformation_prompt[:509] + "..."

            # Use IMAGE_VARIATION task to transform the user photo
            body = json.dumps({
                "taskType": "IMAGE_VARIATION",
                "imageVariationParams": {
                    "text": transformation_prompt,
                    "negativeText": "realistic photo, photography, scary, violent, inappropriate, low quality, blurry, adult",
                    "images": [user_photo_base64]  # User's photo as input
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 512,
                    "width": 512,
                    "cfgScale": 7.0,  # Moderate guidance for good transformation
                    "seed": 123  # Fixed seed for consistency
                }
            })
            
            response = client.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Extract image data
            images = response_body.get('images', [])
            if images:
                image_data = images[0]  # Get first image
                
                # Convert to base64 data URL
                image_url = f"data:image/jpeg;base64,{image_data}"
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                logger.info(f"Professional storybook avatar generated in {response_time:.2f}s for {child_age}yr old")
                return True, image_url, f"Professional avatar generated in {response_time:.2f}s"
            else:
                return False, "", "No avatar data in response"
                
        except Exception as e:
            logger.error(f"Storybook avatar generation failed: {e}")
            return False, "", str(e)
    
    def generate_speech_with_polly(self, text: str, language: str = "es", voice_id: str = None) -> Tuple[bool, str, str]:
        """Generate speech using Amazon Polly"""
        try:
            start_time = datetime.now()
            
            client = self._get_polly_client()
            
            # Select voice based on language and user preference
            if not voice_id:
                if language == "es":
                    voice_id = "Lucia"  # Spanish (Spain) Neural voice
                    language_code = "es-ES"
                elif language == "en":
                    voice_id = "Joanna"  # English (US) Neural voice
                    language_code = "en-US"
                else:
                    voice_id = "Joanna"  # Default to English
                    language_code = "en-US"
            else:
                # Use provided voice_id and determine language_code
                if voice_id in ["Lucia", "Enrique", "Conchita", "Mia", "Lupe"]:
                    language_code = "es-ES"
                else:
                    language_code = "en-US"
            
            # Determine the best engine for this voice
            engine = self._get_voice_engine(voice_id)
            
            logger.info(f"Generating speech with Polly: voice={voice_id}, language={language_code}, engine={engine}")
            
            # Generate speech
            response = client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine,
                LanguageCode=language_code
            )
            
            # Get audio data
            audio_stream = response['AudioStream']
            audio_data = audio_stream.read()
            
            # Convert to base64 for web transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            audio_url = f"data:audio/mp3;base64,{audio_base64}"
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Polly speech generated successfully in {response_time:.2f}s")
            logger.info(f"Audio size: {len(audio_data)} bytes")
            
            return True, audio_url, f"Generated in {response_time:.2f}s with {voice_id}"
            
        except Exception as e:
            logger.error(f"Polly speech generation failed: {e}")
            return False, "", str(e)
    
    def generate_story_image_with_avatar(self, scene_description: str, avatar_url: str, theme: str, child_age: int) -> Tuple[bool, str, str]:
        """Generate story illustration using user avatar as reference with retry strategy"""
        try:
            start_time = datetime.now()
            
            logger.info(f"🎭 Generating story image with avatar reference")
            
            # Extract base64 from avatar URL
            if avatar_url.startswith('data:image'):
                avatar_base64 = avatar_url.split(',')[1]
            else:
                logger.error("Avatar URL is not in base64 format")
                return False, "", "Invalid avatar format"
            
            client = self._get_bedrock_client()
            
            # Strategy 1: Try with story scene
            try:
                story_prompt = f"Magical {theme} scene, children's book illustration, colorful, happy, friendly"
                
                # Ensure prompt is under 512 characters
                if len(story_prompt) > 512:
                    story_prompt = story_prompt[:509] + "..."
                
                result = self._generate_image_variation_with_avatar(client, story_prompt, avatar_base64)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Story image with avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Story image with avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Story scene blocked, trying simpler prompt...")
                else:
                    raise e
            
            # Strategy 2: Ultra-safe prompt
            try:
                safe_prompt = f"Colorful {theme} illustration, magical, bright, children's book art"
                
                result = self._generate_image_variation_with_avatar(client, safe_prompt, avatar_base64)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Safe story image with avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Safe story image with avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Safe prompt also blocked, trying minimal...")
                else:
                    raise e
            
            # Strategy 3: Minimal prompt
            try:
                minimal_prompt = f"{theme} illustration, colorful, magical"
                
                result = self._generate_image_variation_with_avatar(client, minimal_prompt, avatar_base64)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Minimal story image with avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Minimal story image with avatar generated in {response_time:.2f}s"
            except Exception as e:
                logger.error(f"All avatar image generation strategies failed: {e}")
                return False, "", str(e)
            
            return False, "", "All generation strategies failed"
                
        except Exception as e:
            logger.error(f"Story image with avatar generation failed: {e}")
            return False, "", str(e)
    
    def _generate_image_variation_with_avatar(self, client, prompt: str, avatar_base64: str) -> Tuple[bool, str]:
        """Helper method to generate image variation with avatar"""
        body = json.dumps({
            "taskType": "IMAGE_VARIATION",
            "imageVariationParams": {
                "text": prompt,
                "negativeText": "scary, violent, inappropriate, adult content, realistic photo",
                "images": [avatar_base64]  # Avatar as base image
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "cfgScale": 7.0,  # Lower guidance to reduce filtering
                "seed": int(datetime.now().timestamp()) % 1000
            }
        })
        
        response = client.invoke_model(
            body=body,
            modelId="amazon.nova-canvas-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        
        # Extract image data
        images = response_body.get('images', [])
        if images:
            image_data = images[0]
            image_url = f"data:image/jpeg;base64,{image_data}"
            return True, image_url
        else:
            return False, "No image data in response"
    
    def generate_story_image_with_photo(self, scene_description: str, photo_base64: str, theme: str, child_age: int) -> Tuple[bool, str, str]:
        """Generate story illustration using user photo as reference with retry strategy"""
        try:
            start_time = datetime.now()
            
            logger.info(f"📸 Generating story image with photo reference")
            
            # Clean the base64 data
            if photo_base64.startswith('data:image'):
                clean_photo = photo_base64.split(',')[1]
            else:
                clean_photo = photo_base64
            
            client = self._get_bedrock_client()
            
            # Strategy 1: Try with story scene
            try:
                story_prompt = f"Magical {theme} scene, children's book illustration, colorful, happy, friendly"
                
                result = self._generate_image_variation_with_photo(client, story_prompt, clean_photo)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Story image with photo generated in {response_time:.2f}s")
                    return True, result[1], f"Story image with photo generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Story scene with photo blocked, trying simpler prompt...")
                else:
                    raise e
            
            # Strategy 2: Ultra-safe prompt
            try:
                safe_prompt = f"Colorful {theme} illustration, magical, bright, children's book art"
                
                result = self._generate_image_variation_with_photo(client, safe_prompt, clean_photo)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Safe story image with photo generated in {response_time:.2f}s")
                    return True, result[1], f"Safe story image with photo generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Safe prompt with photo also blocked, trying minimal...")
                else:
                    raise e
            
            # Strategy 3: Minimal prompt
            try:
                minimal_prompt = f"{theme} illustration, colorful, magical"
                
                result = self._generate_image_variation_with_photo(client, minimal_prompt, clean_photo)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Minimal story image with photo generated in {response_time:.2f}s")
                    return True, result[1], f"Minimal story image with photo generated in {response_time:.2f}s"
            except Exception as e:
                logger.error(f"All photo image generation strategies failed: {e}")
                return False, "", str(e)
            
            return False, "", "All generation strategies failed"
                
        except Exception as e:
            logger.error(f"Story image with photo generation failed: {e}")
            return False, "", str(e)
    
    def _generate_image_variation_with_photo(self, client, prompt: str, photo_base64: str) -> Tuple[bool, str]:
        """Helper method to generate image variation with photo"""
        body = json.dumps({
            "taskType": "IMAGE_VARIATION",
            "imageVariationParams": {
                "text": prompt,
                "negativeText": "scary, violent, inappropriate, adult content, realistic photo",
                "images": [photo_base64]  # Photo as base image
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "cfgScale": 7.0,  # Lower guidance to reduce filtering
                "seed": int(datetime.now().timestamp()) % 1000
            }
        })
        
        response = client.invoke_model(
            body=body,
            modelId="amazon.nova-canvas-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        
        # Extract image data
        images = response_body.get('images', [])
        if images:
            image_data = images[0]
            image_url = f"data:image/jpeg;base64,{image_data}"
            return True, image_url
        else:
            return False, "No image data in response"
    
    def test_titan_image(self) -> Dict[str, Any]:
        """Test Titan Image Generator"""
        try:
            start_time = datetime.now()
            
            # Test with a simple prompt
            test_prompt = "A happy cartoon rabbit in a magical forest, children's book illustration style"
            
            success, image_url, message = self.generate_image_with_titan(test_prompt, "illustration")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if success:
                return {
                    "success": True,
                    "service": "titan-image",
                    "response_time": response_time,
                    "model_used": "amazon.nova-canvas-v1:0",
                    "test_output": f"Image generated: {len(image_url)} bytes",
                    "message": message,
                    "timestamp": end_time.isoformat()
                }
            else:
                return {
                    "success": False,
                    "service": "titan-image",
                    "error": message,
                    "timestamp": end_time.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Titan image test failed: {e}")
            return {
                "success": False,
                "service": "titan-image",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_storybook_avatar(self, photo_base64: str) -> Tuple[bool, str, str]:
        """Generate a storybook-style avatar from user photo using AWS Titan IMAGE_VARIATION"""
        try:
            start_time = datetime.now()
            
            logger.info("🎨 Generating personalized storybook avatar with AWS Bedrock...")
            
            if photo_base64:
                # Use IMAGE_VARIATION with the user's photo directly
                logger.info("📸 Using user photo for IMAGE_VARIATION transformation")
                return self._generate_avatar_from_photo_variation(photo_base64, start_time)
            else:
                # No photo provided, generate generic avatar
                logger.info("🎭 No photo provided, generating generic storybook avatar")
                return self._generate_safe_cartoon_avatar(start_time)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Storybook avatar generation failed: {error_msg}")
            
            # Check for specific AWS content filtering error
            if self._is_content_filtering_error(error_msg):
                logger.warning("AWS content filtering detected, recommending fallback methods")
                return False, "", "CONTENT_FILTERED"
            
            return False, "", error_msg
    
    def _generate_avatar_from_photo_variation(self, photo_base64: str, start_time: datetime) -> Tuple[bool, str, str]:
        """Generate avatar using IMAGE_VARIATION with user photo as direct input"""
        try:
            client = self._get_bedrock_client()
            
            # Clean the base64 data
            if photo_base64.startswith('data:image'):
                clean_photo = photo_base64.split(',')[1]
            else:
                clean_photo = photo_base64
            
            # Resize image to meet AWS Bedrock requirements
            clean_photo = self._resize_image_for_bedrock(clean_photo)
            
            logger.info(f"📸 Using IMAGE_VARIATION with photo ({len(clean_photo)} chars)")
            
            # Simple, safe transformation prompt
            transformation_prompt = "Storybook illustration style, colorful, magical, children's book art"
            
            # Use IMAGE_VARIATION task to transform the user photo
            body = json.dumps({
                "taskType": "IMAGE_VARIATION",
                "imageVariationParams": {
                    "text": transformation_prompt,
                    "negativeText": "realistic photo, scary, violent, inappropriate, adult content",
                    "images": [clean_photo]  # User's photo as direct input
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 512,
                    "width": 512,
                    "cfgScale": 7.0,
                    "seed": int(datetime.now().timestamp()) % 1000  # Variable seed for variety
                }
            })
            
            response = client.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Extract image data
            images = response_body.get('images', [])
            if images:
                image_data = images[0]  # Get first image
                
                # Convert to base64 data URL
                image_url = f"data:image/jpeg;base64,{image_data}"
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                logger.info(f"✅ Photo-based avatar generated in {response_time:.2f}s using IMAGE_VARIATION")
                return True, image_url, f"Photo-based avatar generated in {response_time:.2f}s"
            else:
                return False, "", "No avatar data in response"
                
        except Exception as e:
            logger.error(f"Photo variation avatar generation failed: {e}")
            return False, "", str(e)
    
    def _extract_safe_characteristics(self, photo_base64: str) -> Dict[str, str]:
        """Extract safe characteristics from photo for avatar generation"""
        try:
            # Clean the base64 data
            if photo_base64.startswith('data:image'):
                clean_photo = photo_base64.split(',')[1]
            else:
                clean_photo = photo_base64
            
            image_bytes = base64.b64decode(clean_photo)
            
            # Use Rekognition to get basic characteristics
            rekognition_client = self._get_rekognition_client()
            response = rekognition_client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['AGE_RANGE']
            )
            
            characteristics = {
                'hair_description': 'brown hair',
                'clothing_description': 'colorful outfit',
                'age_group': 'child'
            }
            
            faces = response.get('FaceDetails', [])
            if faces:
                face = faces[0]
                age_range = face.get('AgeRange', {})
                estimated_age = (age_range.get('Low', 5) + age_range.get('High', 12)) // 2
                
                if estimated_age <= 5:
                    characteristics['hair_description'] = 'soft curly hair'
                    characteristics['clothing_description'] = 'cute colorful clothes'
                    characteristics['age_group'] = 'toddler'
                elif estimated_age <= 8:
                    characteristics['hair_description'] = 'playful hair'
                    characteristics['clothing_description'] = 'bright adventure outfit'
                    characteristics['age_group'] = 'young child'
                else:
                    characteristics['hair_description'] = 'stylish hair'
                    characteristics['clothing_description'] = 'cool adventure gear'
                    characteristics['age_group'] = 'older child'
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"Safe characteristics extraction failed: {e}")
            return {
                'hair_description': 'brown hair',
                'clothing_description': 'colorful outfit',
                'age_group': 'child'
            }
    
    def _resize_image_for_bedrock(self, photo_base64: str) -> str:
        """Resize image to meet AWS Bedrock requirements (height between 320 and 4096 pixels)"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(photo_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            logger.info(f"Original image size: {width}x{height}")
            
            # AWS Bedrock requirements: height between 320 and 4096
            min_height = 320
            max_height = 4096
            target_size = 1024  # Good balance between quality and size
            
            # Check if resizing is needed
            if height < min_height or height > max_height or width < min_height or width > max_height:
                # Calculate aspect ratio
                aspect_ratio = width / height
                
                # Determine new dimensions
                if height < min_height:
                    new_height = min_height
                    new_width = int(new_height * aspect_ratio)
                elif height > max_height:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    # Resize to target size for optimal quality
                    new_height = target_size
                    new_width = int(new_height * aspect_ratio)
                
                # Ensure width is also within bounds
                if new_width < min_height:
                    new_width = min_height
                    new_height = int(new_width / aspect_ratio)
                elif new_width > max_height:
                    new_width = max_height
                    new_height = int(new_width / aspect_ratio)
                
                # Resize image
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to: {new_width}x{new_height}")
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=90)
            resized_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return resized_base64
            
        except Exception as e:
            logger.error(f"Image resizing failed: {e}")
            # Return original if resizing fails
            return photo_base64

    def _generate_personalized_avatar_safe(self, photo_base64: str, start_time: datetime) -> Tuple[bool, str, str]:
        """Generate personalized avatar using safe prompts that reference the photo"""
        try:
            # Strategy 1: Safe cartoon character prompt inspired by photo
            try:
                # Analyze photo safely to get basic characteristics
                characteristics = self._extract_safe_characteristics(photo_base64)
                
                # Ultra-safe prompt that avoids trigger words
                safe_prompt = f"Colorful storybook illustration, magical fairy tale art, bright happy colors, {characteristics.get('hair_description', 'brown hair')}, {characteristics.get('clothing_description', 'colorful outfit')}, digital painting style, children's book art."
                
                result = self._generate_avatar_with_prompt(safe_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Cartoon character avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Cartoon character avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Cartoon character blocked, trying mascot...")
                else:
                    raise e
            
            # Strategy 2: Simple magical art
            try:
                magic_prompt = "Magical storybook art, bright colors, fairy tale illustration, digital painting, children's book style."
                
                result = self._generate_avatar_with_prompt(magic_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Magical art avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Magical art avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Magical art blocked, trying simple illustration...")
                else:
                    raise e
            
            # Strategy 3: Simple illustration
            try:
                simple_prompt = "Colorful illustration, storybook art, bright happy colors, digital painting."
                
                result = self._generate_avatar_with_prompt(simple_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Simple character avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Simple character avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Character blocked, falling back to generic...")
                else:
                    raise e
            
            # Fallback to generic safe generation
            return self._generate_safe_cartoon_avatar(start_time)
            
        except Exception as e:
            logger.error(f"Personalized avatar generation failed: {e}")
            return False, "", str(e)
    
    def _generate_safe_cartoon_avatar(self, start_time: datetime) -> Tuple[bool, str, str]:
        """Generate completely safe cartoon avatar without any photo analysis"""
        try:
            # Strategy 1: Test with known working prompts
            try:
                working_prompt = "flower"
                
                result = self._generate_avatar_with_prompt(working_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Flower avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Flower avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Flower blocked, trying cat...")
                else:
                    raise e
            
            # Strategy 2: Cat
            try:
                cat_prompt = "cat"
                
                result = self._generate_avatar_with_prompt(cat_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Cat avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Cat avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Cat blocked, trying tree...")
                else:
                    raise e
            
            # Strategy 3: Tree
            try:
                tree_prompt = "tree"
                
                result = self._generate_avatar_with_prompt(tree_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Tree avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Tree avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Tree blocked, trying sun...")
                else:
                    raise e
            
            # Strategy 4: Sun
            try:
                sun_prompt = "sun"
                
                result = self._generate_avatar_with_prompt(sun_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Sun avatar generated in {response_time:.2f}s")
                    return True, result[1], f"Sun avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.warning("Sun blocked, trying house...")
                else:
                    raise e
            
            # Strategy 5: House
            try:
                house_prompt = "house"
                
                result = self._generate_avatar_with_prompt(house_prompt)
                if result[0]:  # Success
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ House avatar generated in {response_time:.2f}s")
                    return True, result[1], f"House avatar generated in {response_time:.2f}s"
            except Exception as e:
                if self._is_content_filtering_error(str(e)):
                    logger.error("Even simple objects blocked by content filter")
                    return False, "", "CONTENT_FILTERED"
                else:
                    raise e
            
            return False, "", "All generation strategies failed"
            
        except Exception as e:
            logger.error(f"Safe avatar generation failed: {e}")
            return False, "", str(e)
    
    def _try_avatar_generation_with_fallbacks(self, base_prompt: str, age: int, start_time: datetime) -> Tuple[bool, str, str]:
        """Try avatar generation with multiple prompt strategies"""
        
        # Strategy 1: Enhanced safe prompt
        try:
            result = self._generate_avatar_with_prompt(base_prompt)
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Avatar generated successfully with enhanced prompt in {response_time:.2f}s")
                return True, result[1], f"Avatar generated in {response_time:.2f}s"
        except Exception as e:
            if self._is_content_filtering_error(str(e)):
                logger.warning("Strategy 1 blocked by content filter, trying strategy 2...")
            else:
                logger.error(f"Strategy 1 failed with non-filtering error: {e}")
                raise e
        
        # Strategy 2: Ultra-safe minimal prompt
        try:
            from services.aws_prompt_generator import aws_prompt_generator
            minimal_prompt = aws_prompt_generator.create_minimal_safe_prompt()
            
            result = self._generate_avatar_with_prompt(minimal_prompt)
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Avatar generated with minimal safe prompt in {response_time:.2f}s")
                return True, result[1], f"Avatar generated with minimal safe prompt in {response_time:.2f}s"
        except Exception as e:
            if self._is_content_filtering_error(str(e)):
                logger.warning("Strategy 2 also blocked, trying basic cartoon prompt...")
            else:
                logger.error(f"Strategy 2 failed: {e}")
                raise e
        
        # Strategy 3: Basic cartoon prompt (no age mention)
        try:
            basic_prompt = "Create a simple cartoon character illustration. Animated style, bright colors, friendly mascot, completely non-realistic cartoon art."
            
            result = self._generate_avatar_with_prompt(basic_prompt)
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Avatar generated with basic cartoon prompt in {response_time:.2f}s")
                return True, result[1], f"Avatar generated with basic cartoon prompt in {response_time:.2f}s"
        except Exception as e:
            if self._is_content_filtering_error(str(e)):
                logger.warning("Strategy 3 also blocked, trying absolute minimal prompt...")
            else:
                logger.error(f"Strategy 3 failed: {e}")
                raise e
        
        # Strategy 4: Absolute minimal prompt
        try:
            absolute_minimal = "Cartoon character, animated style, colorful, friendly."
            
            result = self._generate_avatar_with_prompt(absolute_minimal)
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Avatar generated with absolute minimal prompt in {response_time:.2f}s")
                return True, result[1], f"Avatar generated with absolute minimal prompt in {response_time:.2f}s"
        except Exception as e:
            if self._is_content_filtering_error(str(e)):
                logger.error("All AWS prompt strategies blocked by content filter")
                return False, "", "CONTENT_FILTERED"
            else:
                logger.error(f"Strategy 4 failed: {e}")
                raise e
            
            result = self._generate_avatar_with_prompt(minimal_prompt)
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Avatar generated with minimal prompt in {response_time:.2f}s")
                return True, result[1], f"Avatar generated with minimal safe prompt in {response_time:.2f}s"
        except Exception as e:
            if self._is_content_filtering_error(str(e)):
                logger.error("All AWS prompt strategies blocked by content filter")
                return False, "", "CONTENT_FILTERED"
            else:
                logger.error(f"Strategy 3 failed: {e}")
                raise e
        
        # If we get here, all strategies failed
        logger.error("All avatar generation strategies failed")
        return False, "", "All generation strategies failed"
    
    def _generate_avatar_with_prompt(self, prompt: str) -> Tuple[bool, str, str]:
        """Generate avatar with specific prompt using Bedrock Titan"""
        try:
            bedrock_client = self._get_bedrock_client()
            
            # Validate prompt safety before sending
            from services.aws_prompt_generator import aws_prompt_generator
            is_safe, issues = aws_prompt_generator.validate_prompt_safety(prompt)
            
            if not is_safe:
                logger.warning(f"Prompt safety issues detected: {issues}")
                # Use sanitized version
                prompt = aws_prompt_generator._sanitize_prompt(prompt)
            
            # Prepare request for Titan Image Generator (original working config)
            request_body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": "realistic, photorealistic, photograph, real person, human photo, detailed facial features, 3D render, lifelike",
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 512,
                    "width": 512,
                    "cfgScale": 7.0,
                    "seed": 42
                }
            }
            
            # Make request to Bedrock with v2 model
            response = bedrock_client.invoke_model(
                modelId="amazon.nova-canvas-v1:0",
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'images' in response_body and response_body['images']:
                image_data = response_body['images'][0]
                image_url = f"data:image/png;base64,{image_data}"
                return True, image_url, "Image generated successfully"
            else:
                logger.error("No images in Bedrock response")
                return False, "", "No images in response"
                
        except Exception as e:
            logger.error(f"Avatar generation with prompt failed: {e}")
            return False, "", str(e)
    
    def _is_content_filtering_error(self, error_message: str) -> bool:
        """Check if error is due to AWS content filtering"""
        content_filter_indicators = [
            "Content in the all of the generated image(s) has been blocked",
            "has been filtered from the response",
            "may conflict our AUP",
            "AWS Responsible AI Policy",
            "ValidationException",
            "content policy"
        ]
        
        error_lower = error_message.lower()
        return any(indicator.lower() in error_lower for indicator in content_filter_indicators)
    
    def get_content_filtering_guidance(self) -> Dict[str, str]:
        """Get guidance for handling content filtering issues"""
        return {
            "issue": "AWS content filtering detected",
            "cause": "Image generation request may have triggered AWS Responsible AI policies",
            "solutions": [
                "Use more cartoon/animated style descriptions",
                "Avoid realistic or photographic terms",
                "Emphasize storybook illustration style",
                "Use fallback local generation methods"
            ],
            "fallback_methods": [
                "Local avatar generation",
                "Stylized photo processing", 
                "Template-based avatars",
                "Enhanced SVG generation"
            ]
        }
    
    def _generate_avatar_with_prompt(self, prompt: str) -> Tuple[bool, str, str]:
        """Generate avatar with specific prompt"""
        bedrock_client = self._get_bedrock_client()
        
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "photorealistic, realistic photo, adult content, inappropriate, scary, dark, violent, blurry, low quality",
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 512,
                "width": 512,
                "cfgScale": 7.0,  # Slightly lower for more creative freedom
                "seed": 123  # Fixed seed for consistency
            }
        })
        
        response = bedrock_client.invoke_model(
            body=body,
            modelId="amazon.nova-canvas-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        
        # Extract image data
        images = response_body.get('images', [])
        if images:
            image_data = images[0]  # Get first image
            avatar_url = f"data:image/jpeg;base64,{image_data}"
            return True, avatar_url, "Image generated successfully"
        else:
            return False, "", "No images in response"
    
    def _is_content_filtering_error(self, error_message: str) -> bool:
        """Check if error is due to AWS content filtering"""
        content_filter_indicators = [
            "Content in the all of the generated image(s) has been blocked",
            "has been filtered from the response",
            "may conflict our AUP",
            "AWS Responsible AI Policy",
            "ValidationException"
        ]
        
        error_lower = error_message.lower()
        return any(indicator.lower() in error_lower for indicator in content_filter_indicators)
    
    def generate_safe_story_image(self, scene_description: str, age: int, theme: str = "fantasy", 
                                 has_avatar: bool = False) -> Tuple[bool, str, str]:
        """Generate story image with enhanced safety and avatar integration"""
        try:
            from services.aws_prompt_generator import aws_prompt_generator, SafePromptConfig
            
            start_time = datetime.now()
            
            # Create safe prompt configuration
            prompt_config = SafePromptConfig(
                age=age,
                style="storybook",
                theme=theme,
                emphasize_cartoon=True
            )
            
            # Generate safe story image prompt
            image_prompt = aws_prompt_generator.generate_safe_story_image_prompt(
                scene_description, prompt_config, has_avatar
            )
            
            logger.info(f"🎨 Generating story image with safe prompt...")
            
            # Try generation with fallback strategies
            result = self._generate_avatar_with_prompt(image_prompt)
            
            if result[0]:  # Success
                response_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Story image generated successfully in {response_time:.2f}s")
                return True, result[1], f"Story image generated in {response_time:.2f}s"
            else:
                return False, "", "Failed to generate story image"
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Story image generation failed: {error_msg}")
            
            if self._is_content_filtering_error(error_msg):
                logger.warning("Story image blocked by content filter")
                return False, "", "CONTENT_FILTERED"
            
            return False, "", error_msg
    
    def _get_rekognition_client(self):
        """Get Rekognition client"""
        if not self._rekognition_client:
            try:
                session = self._get_boto3_session()
                self._rekognition_client = session.client('rekognition', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to create Rekognition client: {e}")
                raise
        return self._rekognition_client
