"""Error handling and resilience utilities for the Adaptive Storytelling Agent."""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from enum import Enum
import random

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of services for circuit breaker management."""
    BEDROCK = "bedrock"
    REKOGNITION = "rekognition"
    POLLY = "polly"
    S3 = "s3"

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Service is failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service is back

class CircuitBreaker:
    """Circuit breaker pattern implementation for AWS services."""
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def __call__(self, func):
        """Decorator to wrap functions with circuit breaker."""
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._call(func, *args, **kwargs)
        
        return wrapper
    
    async def _call(self, func, *args, **kwargs):
        """Execute function with circuit breaker logic."""
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker for {self.service_name} entering HALF_OPEN state")
            else:
                raise ServiceUnavailableError(
                    f"Circuit breaker OPEN for {self.service_name}. "
                    f"Service unavailable for {self.recovery_timeout} seconds."
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info(f"Circuit breaker for {self.service_name} reset to CLOSED state")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker for {self.service_name} opened after "
                f"{self.failure_count} failures"
            )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold
        }

class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def __call__(self, func):
        """Decorator to add retry logic to functions."""
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._retry_call(func, *args, **kwargs)
        
        return wrapper
    
    async def _retry_call(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(
                        f"Function {func.__name__} failed after {self.max_retries + 1} attempts: {e}"
                    )
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Function {func.__name__} failed (attempt {attempt + 1}), "
                    f"retrying in {delay:.2f} seconds: {e}"
                )
                
                await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)

class FallbackManager:
    """Manages fallback mechanisms when services fail."""
    
    def __init__(self):
        self.fallback_handlers: Dict[str, Callable] = {}
        self.fallback_data: Dict[str, Any] = {}
        
        # Initialize default fallback data
        self._initialize_fallback_data()
    
    def register_fallback(self, service_name: str, handler: Callable):
        """Register a fallback handler for a service."""
        self.fallback_handlers[service_name] = handler
        logger.info(f"Registered fallback handler for {service_name}")
    
    async def execute_fallback(self, service_name: str, *args, **kwargs):
        """Execute fallback for a service."""
        
        if service_name in self.fallback_handlers:
            try:
                return await self.fallback_handlers[service_name](*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback handler for {service_name} failed: {e}")
                return self._get_default_fallback(service_name)
        
        return self._get_default_fallback(service_name)
    
    def _initialize_fallback_data(self):
        """Initialize default fallback data."""
        
        self.fallback_data = {
            ServiceType.BEDROCK.value: {
                "default_story": "Once upon a time, in a magical land far away, there lived a kind and brave little character who was about to embark on the most wonderful adventure. What do you think happens next?",
                "continuation": "The adventure continued with new friends and exciting discoveries around every corner.",
                "conclusion": "And so our brave friend learned that with kindness and courage, any adventure can have a happy ending. The end."
            },
            
                "default_transcript": "",
                "default_sentiment": {
                    "Sentiment": "NEUTRAL",
                    "Confidence": 0.5,
                    "SentimentScore": {
                        "Positive": 0.33,
                        "Negative": 0.33,
                        "Neutral": 0.34
                    }
                }
            },
            
            ServiceType.REKOGNITION.value: {
                "default_emotion": {
                    "FaceDetails": [{
                        "Emotions": [{
                            "Type": "CALM",
                            "Confidence": 50.0
                        }]
                    }]
                }
            },
            
            ServiceType.POLLY.value: {
                "silence_audio": b"",  # Empty audio as fallback
                "error_message": "Audio generation temporarily unavailable"
            },
            
            ServiceType.S3.value: {
                "default_preferences": {
                    "preferred_themes": ["friendship", "animals"],
                    "character_preferences": [],
                    "emotional_responses": []
                }
            }
        }
    
    def _get_default_fallback(self, service_name: str):
        """Get default fallback data for a service."""
        
        return self.fallback_data.get(service_name, {})

class GracefulDegradationManager:
    """Manages graceful degradation when services are unavailable."""
    
    def __init__(self):
        self.service_status: Dict[str, bool] = {}
        self.degradation_strategies: Dict[str, Callable] = {}
        
        # Initialize service status
        for service in ServiceType:
            self.service_status[service.value] = True
    
    def mark_service_unavailable(self, service_name: str):
        """Mark a service as unavailable."""
        self.service_status[service_name] = False
        logger.warning(f"Service {service_name} marked as unavailable")
    
    def mark_service_available(self, service_name: str):
        """Mark a service as available."""
        self.service_status[service_name] = True
        logger.info(f"Service {service_name} marked as available")
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a service is available."""
        return self.service_status.get(service_name, False)
    
    def get_available_services(self) -> List[str]:
        """Get list of available services."""
        return [
            service for service, available in self.service_status.items()
            if available
        ]
    
    def can_provide_basic_functionality(self) -> bool:
        """Check if basic functionality can be provided."""
        # Basic functionality requires at least story generation (Bedrock)
        return self.is_service_available(ServiceType.BEDROCK.value)
    
    def can_provide_emotion_detection(self) -> bool:
        """Check if emotion detection is available."""
        return (
            self.is_service_available(ServiceType.REKOGNITION.value)
        )
    
    def can_provide_voice_narration(self) -> bool:
        """Check if voice narration is available."""
        return self.is_service_available(ServiceType.POLLY.value)
    
    def get_degradation_level(self) -> str:
        """Get current degradation level."""
        
        available_services = len(self.get_available_services())
        total_services = len(ServiceType)
        
        if available_services == total_services:
            return "full_functionality"
        elif available_services >= total_services * 0.8:
            return "minor_degradation"
        elif available_services >= total_services * 0.6:
            return "moderate_degradation"
        elif self.can_provide_basic_functionality():
            return "basic_functionality"
        else:
            return "severe_degradation"

# Custom Exceptions
class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable due to circuit breaker."""
    pass

class EmotionDetectionError(Exception):
    """Raised when emotion detection fails."""
    pass

class StoryGenerationError(Exception):
    """Raised when story generation fails."""
    pass

class VoiceNarrationError(Exception):
    """Raised when voice narration fails."""
    pass

# Global instances
circuit_breakers: Dict[str, CircuitBreaker] = {}
fallback_manager = FallbackManager()
degradation_manager = GracefulDegradationManager()

def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for a service."""
    
    if service_name not in circuit_breakers:
        circuit_breakers[service_name] = CircuitBreaker(
            service_name=service_name,
            failure_threshold=3,
            recovery_timeout=30
        )
    
    return circuit_breakers[service_name]

def with_circuit_breaker(service_name: str):
    """Decorator to add circuit breaker to a function."""
    
    def decorator(func):
        circuit_breaker = get_circuit_breaker(service_name)
        return circuit_breaker(func)
    
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator to add retry logic to a function."""
    
    retry_handler = RetryHandler(max_retries=max_retries, base_delay=base_delay)
    return retry_handler

def with_fallback(service_name: str, fallback_func: Optional[Callable] = None):
    """Decorator to add fallback logic to a function."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                else:
                    return await fallback_manager.execute_fallback(service_name, *args, **kwargs)
        
        return wrapper
    
    return decorator

async def handle_service_error(
    service_name: str,
    error: Exception,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Handle service errors with appropriate fallback."""
    
    logger.error(f"Service error in {service_name}: {error}")
    
    # Mark service as unavailable
    degradation_manager.mark_service_unavailable(service_name)
    
    # Get fallback response
    fallback_response = await fallback_manager.execute_fallback(service_name, context)
    
    return {
        "success": False,
        "error": str(error),
        "service": service_name,
        "fallback_used": True,
        "fallback_data": fallback_response,
        "degradation_level": degradation_manager.get_degradation_level()
    }

def get_system_resilience_status() -> Dict[str, Any]:
    """Get comprehensive system resilience status."""
    
    circuit_breaker_status = {}
    for service_name, cb in circuit_breakers.items():
        circuit_breaker_status[service_name] = cb.get_state()
    
    return {
        "circuit_breakers": circuit_breaker_status,
        "service_availability": degradation_manager.service_status,
        "degradation_level": degradation_manager.get_degradation_level(),
        "available_services": degradation_manager.get_available_services(),
        "can_provide_basic_functionality": degradation_manager.can_provide_basic_functionality(),
        "can_provide_emotion_detection": degradation_manager.can_provide_emotion_detection(),
        "can_provide_voice_narration": degradation_manager.can_provide_voice_narration()
    }