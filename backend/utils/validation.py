"""Data validation and security utilities for the Adaptive Storytelling Agent."""

import logging
import re
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import base64
from PIL import Image
import io

from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration constants."""
    
    # File size limits (in bytes)
    MAX_AUDIO_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024   # 5MB
    
    # Content type restrictions
    ALLOWED_AUDIO_TYPES = [
        "audio/wav", "audio/wave", "audio/x-wav",
        "audio/mpeg", "audio/mp3", "audio/x-mp3",
        "audio/ogg", "audio/webm"
    ]
    
    ALLOWED_IMAGE_TYPES = [
        "image/jpeg", "image/jpg", "image/png",
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    # Text content limits
    MAX_TEXT_LENGTH = 10000
    MAX_PREFERENCE_ITEMS = 20
    MAX_SESSION_DURATION = 3600  # 1 hour in seconds
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_EMOTION_UPDATES_PER_MINUTE = 30
    
    # Content filtering
    INAPPROPRIATE_WORDS = [
        # This would be a comprehensive list in production
        "violence", "weapon", "kill", "death", "hate", "stupid"
    ]


class InputValidator:
    """Validates and sanitizes user inputs."""
    
    def __init__(self):
        self.config = SecurityConfig()
    
    def validate_child_age(self, age: int) -> bool:
        """Validate child age is within acceptable range."""
        return 3 <= age <= 12
    
    def validate_preferences(self, preferences: List[str]) -> List[str]:
        """Validate and sanitize preference list."""
        
        if len(preferences) > self.config.MAX_PREFERENCE_ITEMS:
            raise ValueError(f"Too many preferences. Maximum {self.config.MAX_PREFERENCE_ITEMS} allowed.")
        
        sanitized = []
        for pref in preferences:
            # Sanitize preference text
            clean_pref = self.sanitize_text(pref)
            if clean_pref and len(clean_pref) <= 50:  # Max 50 chars per preference
                sanitized.append(clean_pref)
        
        return sanitized
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input by removing potentially harmful content."""
        
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML/XML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script-like content
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Limit length
        if len(text) > self.config.MAX_TEXT_LENGTH:
            text = text[:self.config.MAX_TEXT_LENGTH]
        
        return text
    
    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format."""
        
        # Check if it's a valid UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))
    
    def validate_emotion_data(self, emotion_data: Dict[str, Any]) -> bool:
        """Validate emotion data structure and values."""
        
        required_fields = ["emotion", "confidence"]
        
        # Check required fields
        for field in required_fields:
            if field not in emotion_data:
                return False
        
        # Validate confidence range
        confidence = emotion_data.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            return False
        
        # Validate intensity if present
        if "intensity" in emotion_data:
            intensity = emotion_data["intensity"]
            if not isinstance(intensity, (int, float)) or not (0.0 <= intensity <= 1.0):
                return False
        
        return True


class FileValidator:
    """Validates uploaded files for security and format compliance."""
    
    def __init__(self):
        self.config = SecurityConfig()
    
    async def validate_audio_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate audio file upload."""
        
        validation_result = {
            "valid": False,
            "errors": [],
            "file_info": {}
        }
        
        try:
            # Check file size
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size == 0:
                validation_result["errors"].append("Empty file")
                return validation_result
            
            if file_size > self.config.MAX_AUDIO_FILE_SIZE:
                validation_result["errors"].append(
                    f"File too large. Maximum size: {self.config.MAX_AUDIO_FILE_SIZE / (1024*1024):.1f}MB"
                )
                return validation_result
            
            # Check content type
            if file.content_type not in self.config.ALLOWED_AUDIO_TYPES:
                validation_result["errors"].append(
                    f"Invalid audio format. Allowed: {', '.join(self.config.ALLOWED_AUDIO_TYPES)}"
                )
                return validation_result
            
            # Basic audio file validation
            if not self._is_valid_audio_content(file_content):
                validation_result["errors"].append("Invalid audio file content")
                return validation_result
            
            validation_result.update({
                "valid": True,
                "file_info": {
                    "size": file_size,
                    "content_type": file.content_type,
                    "filename": file.filename
                }
            })
            
            # Reset file position for later reading
            await file.seek(0)
            
        except Exception as e:
            validation_result["errors"].append(f"File validation error: {str(e)}")
        
        return validation_result
    
    async def validate_image_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate image file upload."""
        
        validation_result = {
            "valid": False,
            "errors": [],
            "file_info": {}
        }
        
        try:
            # Check file size
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size == 0:
                validation_result["errors"].append("Empty file")
                return validation_result
            
            if file_size > self.config.MAX_IMAGE_FILE_SIZE:
                validation_result["errors"].append(
                    f"File too large. Maximum size: {self.config.MAX_IMAGE_FILE_SIZE / (1024*1024):.1f}MB"
                )
                return validation_result
            
            # Check content type
            if file.content_type not in self.config.ALLOWED_IMAGE_TYPES:
                validation_result["errors"].append(
                    f"Invalid image format. Allowed: {', '.join(self.config.ALLOWED_IMAGE_TYPES)}"
                )
                return validation_result
            
            # Validate image content using PIL
            try:
                image = Image.open(io.BytesIO(file_content))
                image.verify()  # Verify it's a valid image
                
                # Check image dimensions
                image = Image.open(io.BytesIO(file_content))  # Reopen after verify
                width, height = image.size
                
                if width < 64 or height < 64:
                    validation_result["errors"].append("Image too small (minimum 64x64 pixels)")
                    return validation_result
                
                if width > 4096 or height > 4096:
                    validation_result["errors"].append("Image too large (maximum 4096x4096 pixels)")
                    return validation_result
                
                validation_result.update({
                    "valid": True,
                    "file_info": {
                        "size": file_size,
                        "content_type": file.content_type,
                        "filename": file.filename,
                        "dimensions": f"{width}x{height}",
                        "format": image.format
                    }
                })
                
            except Exception as e:
                validation_result["errors"].append(f"Invalid image file: {str(e)}")
                return validation_result
            
            # Reset file position for later reading
            await file.seek(0)
            
        except Exception as e:
            validation_result["errors"].append(f"File validation error: {str(e)}")
        
        return validation_result
    
    def _is_valid_audio_content(self, content: bytes) -> bool:
        """Basic audio content validation."""
        
        # Check for common audio file headers
        audio_signatures = [
            b'RIFF',  # WAV
            b'ID3',   # MP3
            b'\xff\xfb',  # MP3
            b'OggS',  # OGG
        ]
        
        return any(content.startswith(sig) for sig in audio_signatures)


class ContentFilter:
    """Filters content for appropriateness and safety."""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.inappropriate_patterns = self._compile_inappropriate_patterns()
    
    def _compile_inappropriate_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for inappropriate content detection."""
        
        patterns = []
        for word in self.config.INAPPROPRIATE_WORDS:
            # Create case-insensitive pattern with word boundaries
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            patterns.append(pattern)
        
        return patterns
    
    def filter_story_content(self, content: str, child_age: int) -> Dict[str, Any]:
        """Filter story content for appropriateness."""
        
        result = {
            "approved": True,
            "filtered_content": content,
            "issues": [],
            "age_appropriate": True
        }
        
        # Check for inappropriate words
        for pattern in self.inappropriate_patterns:
            if pattern.search(content):
                result["approved"] = False
                result["issues"].append(f"Contains inappropriate content")
                break
        
        # Age-specific content checks
        if child_age <= 5:
            # Very young children - extra strict filtering
            complex_words = ["complex", "difficult", "complicated", "sophisticated"]
            if any(word in content.lower() for word in complex_words):
                result["age_appropriate"] = False
                result["issues"].append("Content too complex for age group")
        
        # Check content length appropriateness
        word_count = len(content.split())
        max_words_by_age = {
            (3, 5): 100,
            (6, 8): 200,
            (9, 12): 300
        }
        
        for age_range, max_words in max_words_by_age.items():
            if age_range[0] <= child_age <= age_range[1]:
                if word_count > max_words:
                    result["issues"].append(f"Content too long for age group ({word_count} words)")
                break
        
        return result
    
    def validate_user_input(self, text: str) -> Dict[str, Any]:
        """Validate user input for safety."""
        
        result = {
            "safe": True,
            "sanitized_text": text,
            "issues": []
        }
        
        # Check for script injection attempts
        script_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'document\.',
            r'window\.'
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["safe"] = False
                result["issues"].append("Potential script injection detected")
                break
        
        # Sanitize the text
        result["sanitized_text"] = self._sanitize_input(text)
        
        return result
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove potential script content
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text


class PrivacyManager:
    """Manages privacy and data protection compliance."""
    
    def __init__(self):
        self.data_retention_hours = 24
        self.anonymization_salt = secrets.token_hex(32)
    
    def anonymize_identifier(self, identifier: str) -> str:
        """Create anonymous identifier from user data."""
        
        # Create hash with salt for anonymization
        combined = f"{identifier}{self.anonymization_salt}"
        hash_object = hashlib.sha256(combined.encode())
        return hash_object.hexdigest()[:16]  # Use first 16 characters
    
    def validate_data_retention(self, timestamp: datetime) -> bool:
        """Check if data is within retention period."""
        
        retention_limit = datetime.utcnow() - timedelta(hours=self.data_retention_hours)
        return timestamp > retention_limit
    
    def should_delete_data(self, timestamp: datetime) -> bool:
        """Check if data should be deleted for privacy compliance."""
        
        return not self.validate_data_retention(timestamp)
    
    def sanitize_logs(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize log data to remove sensitive information."""
        
        sanitized = log_data.copy()
        
        # Remove or mask sensitive fields
        sensitive_fields = [
            "session_id", "user_id", "anonymous_id", 
            "audio_data", "image_data", "personal_info"
        ]
        
        for field in sensitive_fields:
            if field in sanitized:
                if field.endswith("_id"):
                    # Mask IDs but keep format
                    sanitized[field] = "***masked***"
                elif field.endswith("_data"):
                    # Remove data content
                    sanitized[field] = f"<{field}_removed>"
                else:
                    sanitized[field] = "***removed***"
        
        return sanitized
    
    def validate_parental_consent(self, consent_data: Dict[str, Any]) -> bool:
        """Validate parental consent for data processing."""
        
        required_fields = ["parent_email", "child_age", "consent_given", "timestamp"]
        
        # Check all required fields are present
        for field in required_fields:
            if field not in consent_data:
                return False
        
        # Validate consent is explicitly given
        if not consent_data.get("consent_given", False):
            return False
        
        # Validate child age requires parental consent
        child_age = consent_data.get("child_age", 0)
        if child_age < 13:  # COPPA compliance
            return True
        
        return False


class RateLimiter:
    """Implements rate limiting for API endpoints."""
    
    def __init__(self):
        self.request_counts: Dict[str, Dict[str, int]] = {}
        self.config = SecurityConfig()
    
    def check_rate_limit(self, identifier: str, endpoint: str) -> Dict[str, Any]:
        """Check if request is within rate limits."""
        
        current_minute = int(datetime.utcnow().timestamp() // 60)
        
        if identifier not in self.request_counts:
            self.request_counts[identifier] = {}
        
        if endpoint not in self.request_counts[identifier]:
            self.request_counts[identifier][endpoint] = {}
        
        # Clean old entries (older than 2 minutes)
        old_minutes = [
            minute for minute in self.request_counts[identifier][endpoint].keys()
            if minute < current_minute - 1
        ]
        for old_minute in old_minutes:
            del self.request_counts[identifier][endpoint][old_minute]
        
        # Count requests in current minute
        current_count = self.request_counts[identifier][endpoint].get(current_minute, 0)
        
        # Determine rate limit based on endpoint
        if "emotion" in endpoint:
            limit = self.config.MAX_EMOTION_UPDATES_PER_MINUTE
        else:
            limit = self.config.MAX_REQUESTS_PER_MINUTE
        
        if current_count >= limit:
            return {
                "allowed": False,
                "limit": limit,
                "current_count": current_count,
                "reset_time": (current_minute + 1) * 60
            }
        
        # Increment counter
        self.request_counts[identifier][endpoint][current_minute] = current_count + 1
        
        return {
            "allowed": True,
            "limit": limit,
            "current_count": current_count + 1,
            "remaining": limit - current_count - 1
        }


# Global instances
input_validator = InputValidator()
file_validator = FileValidator()
content_filter = ContentFilter()
privacy_manager = PrivacyManager()
rate_limiter = RateLimiter()


# Validation decorators and utilities
def validate_session_access(session_id: str) -> bool:
    """Validate session access permissions."""
    
    if not input_validator.validate_session_id(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    return True


def validate_file_upload(file: UploadFile, file_type: str) -> Dict[str, Any]:
    """Validate file upload based on type."""
    
    if file_type == "audio":
        return file_validator.validate_audio_file(file)
    elif file_type == "image":
        return file_validator.validate_image_file(file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def check_content_safety(content: str, child_age: int) -> bool:
    """Check if content is safe for the specified age."""
    
    filter_result = content_filter.filter_story_content(content, child_age)
    return filter_result["approved"] and filter_result["age_appropriate"]


def sanitize_user_input(text: str) -> str:
    """Sanitize user input for safety."""
    
    validation_result = content_filter.validate_user_input(text)
    
    if not validation_result["safe"]:
        raise HTTPException(status_code=400, detail="Invalid input detected")
    
    return validation_result["sanitized_text"]