#!/usr/bin/env python3
"""
AI Info API - Provides information about which AI services are currently being used
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai-info", tags=["AI Info"])

@router.get("/current")
async def get_current_ai_info() -> Dict[str, Any]:
    """Get information about currently active AI services"""
    try:
        from app.config import get_settings
        from backend.admin.config_manager import ConfigManager
        
        settings = get_settings()
        admin_config_manager = ConfigManager()
        admin_config = admin_config_manager.load_config()
        
        # Determine current environment and AWS status
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        aws_region = admin_config.get('aws', {}).get('region', 'eu-west-1') if admin_config else 'eu-west-1'
        
        # Determine which services are being used
        using_aws = settings.is_aws_enabled()
        
        ai_info = {
            "environment": environment,
            "aws_enabled": aws_enabled,
            "aws_region": aws_region,
            "using_aws_services": using_aws,
            "services": {}
        }
        
        if using_aws and environment in ['staging', 'production']:
            # AWS Services
            ai_info["services"] = {
                "story_generation": {
                    "provider": "Amazon Bedrock",
                    "model": "amazon.titan-text-express-v1",
                    "type": "aws",
                    "cost": "paid",
                    "description": "AWS Bedrock with Titan Text Express"
                },
                "image_generation": {
                    "provider": "Amazon Bedrock",
                    "model": "amazon.titan-image-generator-v1", 
                    "type": "aws",
                    "cost": "paid",
                    "description": "AWS Bedrock with Titan Image Generator"
                },
                "text_to_speech": {
                    "provider": "Amazon Polly",
                    "model": "Neural TTS",
                    "type": "aws", 
                    "cost": "paid",
                    "description": "AWS Polly Neural Text-to-Speech"
                },
                "emotion_detection": {
                    "provider": "Amazon Rekognition",
                    "model": "Face Analysis",
                    "type": "aws",
                    "cost": "paid", 
                    "description": "AWS Rekognition Emotion Detection"
                }
            }
            ai_info["cost_warning"] = "AWS costs apply"
            ai_info["quality"] = "high"
            
        else:
            # Free/Mock Services
            ai_info["services"] = {
                "story_generation": {
                    "provider": "Local Generator",
                    "model": "Template-based",
                    "type": "local",
                    "cost": "free",
                    "description": "Local story templates and generation"
                },
                "image_generation": {
                    "provider": "Pollinations.ai / Hugging Face",
                    "model": "Stable Diffusion",
                    "type": "free_api",
                    "cost": "free",
                    "description": "Free AI image generation services"
                },
                "text_to_speech": {
                    "provider": "Browser TTS",
                    "model": "Web Speech API",
                    "type": "browser",
                    "cost": "free",
                    "description": "Browser-based text-to-speech"
                },
                "emotion_detection": {
                    "provider": "Mock Service",
                    "model": "Simulated",
                    "type": "mock",
                    "cost": "free",
                    "description": "Simulated emotion detection"
                }
            }
            ai_info["cost_warning"] = "No AWS costs"
            ai_info["quality"] = "basic"
        
        # Add environment-specific info
        ai_info["environment_info"] = {
            "demo": {
                "description": "Free services only, no AWS costs",
                "features": ["Basic story generation", "SVG illustrations", "Browser TTS"]
            },
            "staging": {
                "description": "AWS services with reduced capacity",
                "features": ["AWS Bedrock stories", "AWS Titan images", "AWS Polly TTS", "AWS Rekognition"]
            },
            "production": {
                "description": "Full AWS services and capabilities", 
                "features": ["Full AWS Bedrock", "High-quality images", "Neural TTS", "Advanced emotion detection"]
            }
        }
        
        return ai_info
        
    except Exception as e:
        logger.error(f"Failed to get AI info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI service information")

@router.get("/providers")
async def get_available_providers() -> Dict[str, Any]:
    """Get information about all available AI providers"""
    try:
        return {
            "aws_services": {
                "bedrock": {
                    "name": "Amazon Bedrock",
                    "description": "Managed AI service for text and image generation",
                    "models": {
                        "text": ["amazon.titan-text-express-v1"],
                        "image": ["amazon.titan-image-generator-v1"]
                    },
                    "cost": "paid",
                    "quality": "high"
                },
                "polly": {
                    "name": "Amazon Polly", 
                    "description": "Neural text-to-speech service",
                    "models": ["Neural TTS"],
                    "cost": "paid",
                    "quality": "high"
                },
                "rekognition": {
                    "name": "Amazon Rekognition",
                    "description": "Image and video analysis service",
                    "models": ["Face Analysis", "Emotion Detection"],
                    "cost": "paid",
                    "quality": "high"
                }
            },
            "free_services": {
                "pollinations": {
                    "name": "Pollinations.ai",
                    "description": "Free AI image generation",
                    "models": ["Stable Diffusion"],
                    "cost": "free",
                    "quality": "good"
                },
                "huggingface": {
                    "name": "Hugging Face",
                    "description": "Free AI model inference",
                    "models": ["Various open models"],
                    "cost": "free", 
                    "quality": "good"
                },
                "browser_tts": {
                    "name": "Web Speech API",
                    "description": "Browser-based text-to-speech",
                    "models": ["System TTS"],
                    "cost": "free",
                    "quality": "basic"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get provider info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider information")