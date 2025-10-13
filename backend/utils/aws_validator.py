"""AWS configuration validation utilities."""

import boto3
import logging
from typing import Dict, List, Tuple
from botocore.exceptions import ClientError, NoCredentialsError

from app.config import get_settings

logger = logging.getLogger(__name__)

class AWSValidator:
    """Validates AWS configuration and service access."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def validate_all_services(self) -> Dict[str, bool]:
        """Validate access to all required AWS services."""
        services = {
            "bedrock": self._validate_bedrock,
            "rekognition": self._validate_rekognition,
            "polly": self._validate_polly,
            "s3": self._validate_s3
        }
        
        results = {}
        for service_name, validator in services.items():
            try:
                results[service_name] = await validator()
            except Exception as e:
                logger.error(f"Error validating {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    async def _validate_bedrock(self) -> bool:
        """Validate Bedrock access and model availability."""
        try:
            client = boto3.client(
                'bedrock',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_session_token=self.settings.aws_session_token
            )
            
            # Try to list foundation models
            response = client.list_foundation_models()
            
            # Check if our target model is available
            available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
            model_available = self.settings.bedrock_model_id in available_models
            
            if not model_available:
                logger.warning(f"Target model {self.settings.bedrock_model_id} not found in available models")
            
            return True  # Service is accessible even if specific model isn't available
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Bedrock validation failed: {e}")
            return False
    
        try:
            client = boto3.client(
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_session_token=self.settings.aws_session_token
            )
            
            # Try to list transcription jobs (should work even if empty)
            client.list_transcription_jobs(MaxResults=1)
            return True
            
        except (ClientError, NoCredentialsError) as e:
            return False
    
    async def _validate_rekognition(self) -> bool:
        """Validate Rekognition access."""
        try:
            client = boto3.client(
                'rekognition',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_session_token=self.settings.aws_session_token
            )
            
            # Try to list collections (should work even if empty)
            client.list_collections()
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Rekognition validation failed: {e}")
            return False
    
    async def _validate_polly(self) -> bool:
        """Validate Polly access and voice availability."""
        try:
            client = boto3.client(
                'polly',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_session_token=self.settings.aws_session_token
            )
            
            # Try to list voices
            response = client.describe_voices()
            
            # Check if our target voice is available
            available_voices = [voice['Id'] for voice in response.get('Voices', [])]
            voice_available = self.settings.polly_voice_id in available_voices
            
            if not voice_available:
                logger.warning(f"Target voice {self.settings.polly_voice_id} not found in available voices")
            
            return True  # Service is accessible even if specific voice isn't available
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Polly validation failed: {e}")
            return False
    
    async def _validate_s3(self) -> bool:
        """Validate S3 access."""
        try:
            client = boto3.client(
                's3',
                region_name=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_session_token=self.settings.aws_session_token
            )
            
            # Try to list buckets
            client.list_buckets()
            
            # If specific bucket is configured, check if it exists
            if self.settings.s3_bucket_name:
                try:
                    client.head_bucket(Bucket=self.settings.s3_bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        logger.warning(f"S3 bucket {self.settings.s3_bucket_name} not found")
                    else:
                        raise
            
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 validation failed: {e}")
            return False
    
    def get_validation_summary(self, results: Dict[str, bool]) -> Tuple[bool, List[str]]:
        """Get validation summary with recommendations."""
        all_valid = all(results.values())
        issues = []
        
        if not results.get("bedrock", False):
            issues.append("Bedrock access failed - story generation will not work")

        if not results.get("rekognition", False):
            issues.append("Rekognition access failed - visual emotion detection will not work")
        
        if not results.get("polly", False):
            issues.append("Polly access failed - voice narration will not work")
        
        if not results.get("s3", False):
            issues.append("S3 access failed - story templates and preferences storage will not work")
        
        return all_valid, issues