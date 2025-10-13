#!/usr/bin/env python3
"""
Avatar Fallback Controller
Manages progressive fallback strategy for avatar generation
Coordinates between AWS, local, and template-based generation methods
"""

import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AvatarGenerationMethod(Enum):
    """Available avatar generation methods"""
    AWS_BEDROCK = "aws_bedrock"
    LOCAL_AI = "local_ai"
    STYLIZED_PHOTO = "stylized_photo"
    TEMPLATE_BASED = "template_based"
    SIMPLE_SVG = "simple_svg"

@dataclass
class AvatarGenerationResult:
    """Result of avatar generation attempt"""
    success: bool
    avatar_url: Optional[str]
    method_used: AvatarGenerationMethod
    quality_score: int  # 1-5, where 5 is highest quality
    generation_time: float
    message: str
    error_type: Optional[str] = None
    fallback_used: bool = False

@dataclass
class AvatarRequest:
    """Avatar generation request parameters"""
    photo_base64: Optional[str]
    age: int
    theme: str = "fantasy"
    style: str = "cartoon"
    characteristics: Optional[Dict] = None
    preferences: Optional[Dict] = None

class AvatarFallbackController:
    """
    Controls progressive fallback strategy for avatar generation
    Ensures users always get the best possible avatar regardless of service availability
    """
    
    def __init__(self):
        self.generation_methods = [
            AvatarGenerationMethod.AWS_BEDROCK,
            AvatarGenerationMethod.LOCAL_AI,
            AvatarGenerationMethod.STYLIZED_PHOTO,
            AvatarGenerationMethod.TEMPLATE_BASED,
            AvatarGenerationMethod.SIMPLE_SVG
        ]
        
        # Quality scores for each method
        self.method_quality_scores = {
            AvatarGenerationMethod.AWS_BEDROCK: 5,
            AvatarGenerationMethod.LOCAL_AI: 4,
            AvatarGenerationMethod.STYLIZED_PHOTO: 3,
            AvatarGenerationMethod.TEMPLATE_BASED: 4,
            AvatarGenerationMethod.SIMPLE_SVG: 2
        }
        
        # Method availability cache
        self.method_availability = {}
        self.last_availability_check = {}
        self.availability_cache_duration = 300  # 5 minutes
        
        # Performance tracking
        self.method_performance = {
            method: {"success_count": 0, "failure_count": 0, "avg_time": 0.0}
            for method in self.generation_methods
        }
    
    def generate_avatar(self, request: AvatarRequest) -> AvatarGenerationResult:
        """
        Generate avatar using progressive fallback strategy
        
        Args:
            request: Avatar generation request
            
        Returns:
            AvatarGenerationResult with best available avatar
        """
        start_time = time.time()
        
        logger.info(f"🎭 Starting avatar generation for age {request.age}, theme {request.theme}")
        
        # Determine optimal method order based on request
        method_order = self._determine_method_order(request)
        
        last_error = None
        attempts = []
        
        for method in method_order:
            try:
                logger.info(f"🔄 Attempting avatar generation with {method.value}")
                
                # Check method availability
                if not self._is_method_available(method):
                    logger.warning(f"⚠️ Method {method.value} not available, skipping")
                    continue
                
                # Attempt generation
                result = self._generate_with_method(method, request)
                
                # Track performance
                self._update_performance_metrics(method, result)
                
                if result.success:
                    total_time = time.time() - start_time
                    result.generation_time = total_time
                    result.fallback_used = len(attempts) > 0
                    
                    logger.info(f"✅ Avatar generated successfully with {method.value} in {total_time:.2f}s")
                    return result
                else:
                    attempts.append((method, result.message))
                    last_error = result.message
                    logger.warning(f"❌ Method {method.value} failed: {result.message}")
                    
            except Exception as e:
                error_msg = str(e)
                attempts.append((method, error_msg))
                last_error = error_msg
                logger.error(f"❌ Method {method.value} threw exception: {error_msg}")
                
                # Update availability if this looks like a service issue
                if self._is_service_unavailable_error(error_msg):
                    self._mark_method_unavailable(method)
        
        # All methods failed
        total_time = time.time() - start_time
        logger.error(f"❌ All avatar generation methods failed after {total_time:.2f}s")
        
        return AvatarGenerationResult(
            success=False,
            avatar_url=None,
            method_used=AvatarGenerationMethod.SIMPLE_SVG,
            quality_score=0,
            generation_time=total_time,
            message=f"All generation methods failed. Last error: {last_error}",
            error_type="all_methods_failed",
            fallback_used=True
        )
    
    def _determine_method_order(self, request: AvatarRequest) -> List[AvatarGenerationMethod]:
        """Determine optimal method order based on request characteristics"""
        
        # Start with default order
        method_order = self.generation_methods.copy()
        
        # Adjust based on photo availability
        if not request.photo_base64:
            # No photo - prioritize template-based generation
            method_order.remove(AvatarGenerationMethod.STYLIZED_PHOTO)
            method_order.insert(1, AvatarGenerationMethod.TEMPLATE_BASED)
        
        # Adjust based on age (younger children might benefit from simpler methods)
        if request.age <= 5:
            # For very young children, prioritize template-based for consistency
            if AvatarGenerationMethod.TEMPLATE_BASED in method_order:
                method_order.remove(AvatarGenerationMethod.TEMPLATE_BASED)
                method_order.insert(1, AvatarGenerationMethod.TEMPLATE_BASED)
        
        # Adjust based on performance history
        method_order.sort(key=lambda m: (
            -self._get_method_success_rate(m),  # Higher success rate first
            -self.method_quality_scores[m],     # Higher quality first
            self._get_method_avg_time(m)        # Faster methods first
        ))
        
        logger.info(f"📋 Method order determined: {[m.value for m in method_order]}")
        return method_order
    
    def _generate_with_method(self, method: AvatarGenerationMethod, 
                            request: AvatarRequest) -> AvatarGenerationResult:
        """Generate avatar using specific method"""
        
        method_start_time = time.time()
        
        try:
            if method == AvatarGenerationMethod.AWS_BEDROCK:
                return self._generate_with_aws(request, method_start_time)
            
            elif method == AvatarGenerationMethod.LOCAL_AI:
                return self._generate_with_local_ai(request, method_start_time)
            
            elif method == AvatarGenerationMethod.STYLIZED_PHOTO:
                return self._generate_with_stylized_photo(request, method_start_time)
            
            elif method == AvatarGenerationMethod.TEMPLATE_BASED:
                return self._generate_with_template(request, method_start_time)
            
            elif method == AvatarGenerationMethod.SIMPLE_SVG:
                return self._generate_with_simple_svg(request, method_start_time)
            
            else:
                raise ValueError(f"Unknown generation method: {method}")
                
        except Exception as e:
            generation_time = time.time() - method_start_time
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=method,
                quality_score=0,
                generation_time=generation_time,
                message=str(e),
                error_type="method_exception"
            )
    
    def _generate_with_aws(self, request: AvatarRequest, start_time: float) -> AvatarGenerationResult:
        """Generate avatar using AWS Bedrock"""
        try:
            from admin.config_manager import ConfigManager
            from admin.aws_connector import AWSConnector
            from services.photo_content_filter import photo_content_filter
            
            # Check AWS availability
            config_manager = ConfigManager()
            admin_config = config_manager.load_config()
            environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
            aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
            
            if not aws_enabled:
                return AvatarGenerationResult(
                    success=False,
                    avatar_url=None,
                    method_used=AvatarGenerationMethod.AWS_BEDROCK,
                    quality_score=0,
                    generation_time=time.time() - start_time,
                    message="AWS not enabled in configuration",
                    error_type="aws_not_available"
                )
            
            # Get credentials
            credentials = config_manager.get_aws_credentials()
            if not credentials:
                return AvatarGenerationResult(
                    success=False,
                    avatar_url=None,
                    method_used=AvatarGenerationMethod.AWS_BEDROCK,
                    quality_score=0,
                    generation_time=time.time() - start_time,
                    message="AWS credentials not available",
                    error_type="aws_credentials_missing"
                )
            
            # Pre-process photo if available
            processed_photo = request.photo_base64
            logger.info(f"🔍 AWS Avatar Generation Debug:")
            logger.info(f"   - Photo provided: {bool(processed_photo)}")
            logger.info(f"   - Photo length: {len(processed_photo) if processed_photo else 0}")
            logger.info(f"   - Age: {request.age}")
            logger.info(f"   - Theme: {request.theme}")
            
            if processed_photo:
                success, processed_photo, metadata = photo_content_filter.process_photo_for_avatar(
                    processed_photo, request.age
                )
                if not success:
                    logger.warning("Photo pre-processing failed, using original")
                    processed_photo = request.photo_base64
                else:
                    logger.info(f"   - Photo processed successfully: {len(processed_photo)} chars")
            
            # Initialize AWS connector and generate avatar
            aws_connector = AWSConnector(credentials)
            
            # Only pass photo if we actually have one
            if processed_photo:
                success, avatar_url, message = aws_connector.generate_storybook_avatar(processed_photo)
                logger.info(f"🎭 Using user photo for personalized avatar generation")
            else:
                success, avatar_url, message = aws_connector.generate_storybook_avatar("")
                logger.info(f"🎭 No user photo provided, generating generic avatar")
            
            generation_time = time.time() - start_time
            
            if success:
                return AvatarGenerationResult(
                    success=True,
                    avatar_url=avatar_url,
                    method_used=AvatarGenerationMethod.AWS_BEDROCK,
                    quality_score=self.method_quality_scores[AvatarGenerationMethod.AWS_BEDROCK],
                    generation_time=generation_time,
                    message="Avatar generated with AWS Bedrock Titan"
                )
            else:
                # Check if this is a content filtering error
                error_type = "aws_content_filtered" if message == "CONTENT_FILTERED" else "aws_generation_failed"
                
                return AvatarGenerationResult(
                    success=False,
                    avatar_url=None,
                    method_used=AvatarGenerationMethod.AWS_BEDROCK,
                    quality_score=0,
                    generation_time=generation_time,
                    message=message,
                    error_type=error_type
                )
                
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=AvatarGenerationMethod.AWS_BEDROCK,
                quality_score=0,
                generation_time=time.time() - start_time,
                message=str(e),
                error_type="aws_exception"
            )
    
    def _generate_with_local_ai(self, request: AvatarRequest, start_time: float) -> AvatarGenerationResult:
        """Generate avatar using local AI"""
        try:
            from services.local_avatar_generator import local_avatar_generator
            
            if request.photo_base64:
                # Generate from photo
                success, avatar_url, message = local_avatar_generator.generate_avatar_from_photo(
                    request.photo_base64, request.age, request.style
                )
            else:
                # Generate hybrid avatar
                success, avatar_url, message = local_avatar_generator.create_hybrid_avatar(
                    "", request.age, request.theme
                )
            
            generation_time = time.time() - start_time
            
            return AvatarGenerationResult(
                success=success,
                avatar_url=avatar_url if success else None,
                method_used=AvatarGenerationMethod.LOCAL_AI,
                quality_score=self.method_quality_scores[AvatarGenerationMethod.LOCAL_AI] if success else 0,
                generation_time=generation_time,
                message=message
            )
            
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=AvatarGenerationMethod.LOCAL_AI,
                quality_score=0,
                generation_time=time.time() - start_time,
                message=str(e),
                error_type="local_ai_exception"
            )
    
    def _generate_with_stylized_photo(self, request: AvatarRequest, start_time: float) -> AvatarGenerationResult:
        """Generate avatar using stylized photo processing"""
        try:
            if not request.photo_base64:
                return AvatarGenerationResult(
                    success=False,
                    avatar_url=None,
                    method_used=AvatarGenerationMethod.STYLIZED_PHOTO,
                    quality_score=0,
                    generation_time=time.time() - start_time,
                    message="No photo provided for stylized photo generation",
                    error_type="no_photo_provided"
                )
            
            from services.local_avatar_generator import local_avatar_generator
            
            success, avatar_url, message = local_avatar_generator.create_stylized_photo_avatar(
                request.photo_base64, request.age, request.style
            )
            
            generation_time = time.time() - start_time
            
            return AvatarGenerationResult(
                success=success,
                avatar_url=avatar_url if success else None,
                method_used=AvatarGenerationMethod.STYLIZED_PHOTO,
                quality_score=self.method_quality_scores[AvatarGenerationMethod.STYLIZED_PHOTO] if success else 0,
                generation_time=generation_time,
                message=message
            )
            
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=AvatarGenerationMethod.STYLIZED_PHOTO,
                quality_score=0,
                generation_time=time.time() - start_time,
                message=str(e),
                error_type="stylized_photo_exception"
            )
    
    def _generate_with_template(self, request: AvatarRequest, start_time: float) -> AvatarGenerationResult:
        """Generate avatar using template-based system"""
        try:
            from services.template_avatar_generator import template_avatar_generator
            
            success, avatar_url, message = template_avatar_generator.generate_template_avatar(
                request.age, request.characteristics, request.theme
            )
            
            generation_time = time.time() - start_time
            
            return AvatarGenerationResult(
                success=success,
                avatar_url=avatar_url if success else None,
                method_used=AvatarGenerationMethod.TEMPLATE_BASED,
                quality_score=self.method_quality_scores[AvatarGenerationMethod.TEMPLATE_BASED] if success else 0,
                generation_time=generation_time,
                message=message
            )
            
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=AvatarGenerationMethod.TEMPLATE_BASED,
                quality_score=0,
                generation_time=time.time() - start_time,
                message=str(e),
                error_type="template_exception"
            )
    
    def _generate_with_simple_svg(self, request: AvatarRequest, start_time: float) -> AvatarGenerationResult:
        """Generate simple SVG avatar as final fallback"""
        try:
            # Create very simple SVG avatar
            svg_content = self._create_simple_fallback_svg(request.age, request.theme)
            
            import base64
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            avatar_url = f"data:image/svg+xml;base64,{svg_base64}"
            
            generation_time = time.time() - start_time
            
            return AvatarGenerationResult(
                success=True,
                avatar_url=avatar_url,
                method_used=AvatarGenerationMethod.SIMPLE_SVG,
                quality_score=self.method_quality_scores[AvatarGenerationMethod.SIMPLE_SVG],
                generation_time=generation_time,
                message="Simple SVG avatar created as fallback"
            )
            
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                avatar_url=None,
                method_used=AvatarGenerationMethod.SIMPLE_SVG,
                quality_score=0,
                generation_time=time.time() - start_time,
                message=str(e),
                error_type="simple_svg_exception"
            )
    
    def _create_simple_fallback_svg(self, age: int, theme: str) -> str:
        """Create very simple SVG as ultimate fallback"""
        theme_colors = {
            "fantasy": "#A29BFE",
            "adventure": "#FDCB6E", 
            "animals": "#4ECDC4",
            "space": "#6C5CE7"
        }
        
        bg_color = theme_colors.get(theme, "#87CEEB")
        
        return f'''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <rect width="512" height="512" fill="{bg_color}"/>
            <circle cx="256" cy="200" r="80" fill="#FDBCB4" stroke="#000" stroke-width="3"/>
            <circle cx="236" cy="180" r="8" fill="#000"/>
            <circle cx="276" cy="180" r="8" fill="#000"/>
            <path d="M 236 210 Q 256 225 276 210" stroke="#000" stroke-width="3" fill="none"/>
            <ellipse cx="256" cy="120" rx="90" ry="40" fill="#8B4513"/>
            <rect x="206" y="280" width="100" height="120" rx="10" fill="#4ECDC4" stroke="#000" stroke-width="2"/>
            <text x="256" y="450" font-family="Arial" font-size="14" text-anchor="middle" fill="#000">
                {theme.title()} Avatar (Age {age})
            </text>
        </svg>'''
    
    def _is_method_available(self, method: AvatarGenerationMethod) -> bool:
        """Check if generation method is currently available"""
        current_time = time.time()
        
        # Check cache
        if method in self.last_availability_check:
            time_since_check = current_time - self.last_availability_check[method]
            if time_since_check < self.availability_cache_duration:
                return self.method_availability.get(method, True)
        
        # Update availability check
        self.last_availability_check[method] = current_time
        
        # Simple availability checks
        if method == AvatarGenerationMethod.AWS_BEDROCK:
            try:
                from admin.config_manager import ConfigManager
                config_manager = ConfigManager()
                admin_config = config_manager.load_config()
                environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
                aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
                available = environment in ['staging', 'production'] and aws_enabled
            except:
                available = False
        else:
            # Local methods are generally always available
            available = True
        
        self.method_availability[method] = available
        return available
    
    def _mark_method_unavailable(self, method: AvatarGenerationMethod, duration: int = 300):
        """Mark method as temporarily unavailable"""
        self.method_availability[method] = False
        self.last_availability_check[method] = time.time()
        logger.warning(f"⚠️ Marked {method.value} as unavailable for {duration} seconds")
    
    def _is_service_unavailable_error(self, error_message: str) -> bool:
        """Check if error indicates service unavailability"""
        unavailable_indicators = [
            "connection", "timeout", "service unavailable", 
            "network", "dns", "unreachable"
        ]
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in unavailable_indicators)
    
    def _update_performance_metrics(self, method: AvatarGenerationMethod, 
                                  result: AvatarGenerationResult):
        """Update performance metrics for method"""
        metrics = self.method_performance[method]
        
        if result.success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1
        
        # Update average time
        total_attempts = metrics["success_count"] + metrics["failure_count"]
        if total_attempts > 1:
            metrics["avg_time"] = (
                (metrics["avg_time"] * (total_attempts - 1) + result.generation_time) / total_attempts
            )
        else:
            metrics["avg_time"] = result.generation_time
    
    def _get_method_success_rate(self, method: AvatarGenerationMethod) -> float:
        """Get success rate for method"""
        metrics = self.method_performance[method]
        total = metrics["success_count"] + metrics["failure_count"]
        return metrics["success_count"] / max(total, 1)
    
    def _get_method_avg_time(self, method: AvatarGenerationMethod) -> float:
        """Get average generation time for method"""
        return self.method_performance[method]["avg_time"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all methods"""
        report = {}
        
        for method in self.generation_methods:
            metrics = self.method_performance[method]
            total_attempts = metrics["success_count"] + metrics["failure_count"]
            
            report[method.value] = {
                "total_attempts": total_attempts,
                "success_count": metrics["success_count"],
                "failure_count": metrics["failure_count"],
                "success_rate": self._get_method_success_rate(method),
                "average_time": metrics["avg_time"],
                "quality_score": self.method_quality_scores[method],
                "currently_available": self._is_method_available(method)
            }
        
        return report

# Global instance for easy access
avatar_fallback_controller = AvatarFallbackController()