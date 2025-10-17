"""Real AI image generation service using free APIs."""

import base64
import logging
import requests
import random
from typing import Optional

from ai_services import AIServiceConfig

logger = logging.getLogger(__name__)

class AIImageService:
    """Service for generating images using free AI APIs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
    
    def generate_image(self, prompt: str, style: str = "children_book") -> Optional[str]:
        """Generate image using AI services."""
        
        logger.info(f"🎨 Starting image generation with style: {style}")
        logger.info(f"📝 Original prompt length: {len(prompt)} chars")
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(prompt, style)
        logger.info(f"✨ Enhanced prompt length: {len(enhanced_prompt)} chars")
        logger.info(f"📋 Enhanced prompt: {enhanced_prompt[:200]}...")
        
        # Try AWS Bedrock first, then fallbacks
        logger.info("🔄 Attempting AWS Bedrock generation...")
        try:
            result = self._generate_with_bedrock(enhanced_prompt)
            if result:
                logger.info("✅ Image generated successfully with AWS Bedrock")
                return result
            else:
                logger.warning("⚠️ AWS Bedrock returned None")
        except Exception as e:
            logger.warning(f"❌ AWS Bedrock failed: {e}")
        
        # Fallback to other services
        services = [
            self._generate_with_pollinations,
            self._generate_fallback_image
        ]
        
        for service in services:
            try:
                result = service(enhanced_prompt)
                if result:
                    logger.info(f"Image generated successfully with {service.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Service {service.__name__} failed: {e}")
                continue
        
        logger.error("All image generation services failed")
        return None
    
    def generate_avatar(self, prompt: str, style: str = "children_book_avatar") -> Optional[str]:
        """Generate avatar using AI services."""
        
        # Build avatar-specific prompt
        avatar_prompt = self._build_avatar_prompt(prompt, style)
        
        return self.generate_image(avatar_prompt, style)
    
    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        """Build enhanced prompt for better results."""
        
        logger.info(f"🔍 _build_enhanced_prompt received: {prompt[:200]}...")
        
        # CRITICAL: Preserve the original prompt which contains gender and character info
        # Only add quality enhancements, don't replace the prompt
        
        # Check if this is for professional landscape/background (no character)
        if style == "professional_landscape":
            import random
            professional_prompts = [
                "Ultra cinematic ancient forest, towering old-growth trees, dappled golden sunlight filtering through dense canopy",
                "Photorealistic misty forest landscape, ethereal fog weaving between massive tree trunks, soft natural lighting",
                "Professional nature photography style forest, moss-covered ground, ferns, atmospheric depth, 8K quality",
                "Majestic woodland scene, cathedral-like tree formations, rays of sunlight piercing through leaves",
                "Pristine temperate rainforest, lush green vegetation, crystal clear stream, natural documentary style",
                "Serene forest clearing, wildflowers, butterflies, peaceful natural environment, National Geographic quality",
                "Deep forest interior, ancient oak and pine trees, natural forest floor, professional landscape photography",
                "Enchanted old-growth forest, natural beauty, wildlife habitat, conservation photography style",
                "Breathtaking forest vista, layered canopy, natural lighting, environmental photography masterpiece",
                "Tranquil woodland sanctuary, biodiversity showcase, nature's cathedral, award-winning photography"
            ]
            
            base_prompt = random.choice(professional_prompts)
            return f"{base_prompt}, ultra high definition, professional photography, cinematic lighting, nature documentary quality, 8K resolution, realistic textures, depth of field, natural colors"
        
        # For story illustrations: KEEP the original prompt and just add quality enhancements
        enhanced = f"{prompt}, children's book illustration style, vibrant colors, high quality, detailed artwork, safe for children, appropriate content"
        
        logger.info(f"✨ Enhanced prompt: {enhanced[:200]}...")
        return enhanced
    
    def _build_avatar_prompt(self, base_prompt: str, style: str) -> str:
        """Build avatar-specific prompt."""
        
        avatar_styles = {
            "children_book_avatar": "cute child character portrait, children's book style, friendly face, big eyes, colorful, cartoon avatar",
            "cartoon_avatar": "cartoon child avatar, animated style, bright colors, happy expression",
            "fantasy_avatar": "fantasy child character avatar, magical elements, sparkles, dreamy",
            "watercolor_avatar": "watercolor child avatar, soft colors, artistic, gentle expression"
        }
        
        style_prompt = avatar_styles.get(style, avatar_styles["children_book_avatar"])
        
        return f"{style_prompt}, portrait, circular frame, {base_prompt}, high quality, safe for children"
    
    def _generate_with_pollinations(self, prompt: str) -> Optional[str]:
        """Generate image using Pollinations AI (free, no auth required)."""
        
        # Pollinations API - simple and fast
        url = f"{AIServiceConfig.POLLINATIONS_API_URL}/{prompt}"
        
        # Add parameters for better results
        params = {
            "width": 1920,
            "height": 1080,
            "seed": random.randint(1, 1000000),
            "enhance": "true",
            "model": "flux",
            "nologo": "true",
            "quality": "ultra"
        }
        
        response = self.session.get(url, params=params, timeout=10)
        if response.status_code == 200:
            # Pollinations returns the image directly
            image_data = response.content
            
            # Convert to base64 data URL
            base64_data = base64.b64encode(image_data).decode()
            return f"data:image/jpeg;base64,{base64_data}"
        
        return None
    

    
    def _generate_with_bedrock(self, prompt: str) -> Optional[str]:
        """Generate image using AWS Bedrock Titan."""
        try:
            logger.info("🔧 Loading ConfigManager...")
            from admin.config_manager import ConfigManager
            
            config_manager = ConfigManager()
            
            # Get AWS credentials
            logger.info("🔑 Getting AWS credentials...")
            aws_config = config_manager.get_aws_credentials()
            if not aws_config:
                logger.warning("⚠️ No AWS config available - skipping Bedrock")
                return None
            
            logger.info(f"✅ AWS config found: region={aws_config.get('region', 'N/A')}")
            
            logger.info("🔌 Initializing AWSConnector...")
            from admin.aws_connector import AWSConnector
            aws_connector = AWSConnector(aws_config)
            
            # Generate image with Titan
            logger.info(f"🚀 Calling Titan with prompt length: {len(prompt)}")
            success, image_url, message = aws_connector.generate_image_with_titan(prompt)
            
            if success:
                logger.info(f"✅ Titan success! Image URL length: {len(image_url) if image_url else 0}")
                return image_url
            else:
                logger.warning(f"❌ Bedrock image generation failed: {message}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Bedrock image generation error: {e}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_fallback_image(self, prompt: str) -> Optional[str]:
        """Generate fallback SVG image."""
        
        try:
            # Generate simple SVG instead of using external service
            svg_content = f'''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <radialGradient id="bg" cx="50%" cy="30%" r="70%">
                        <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#4682B4;stop-opacity:1" />
                    </radialGradient>
                </defs>
                <rect width="512" height="512" fill="url(#bg)"/>
                <circle cx="450" cy="80" r="30" fill="#FFD700" opacity="0.8"/>
                <rect y="400" width="512" height="112" fill="#228B22" opacity="0.7"/>
                <text x="256" y="280" font-family="Arial" font-size="24" text-anchor="middle" fill="white">AI Generated</text>
                <text x="256" y="320" font-family="Arial" font-size="16" text-anchor="middle" fill="white" opacity="0.8">{prompt[:40]}...</text>
            </svg>'''
            
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            return f"data:image/svg+xml;base64,{svg_base64}"
            
        except Exception as e:
            logger.error(f"SVG fallback failed: {e}")
            return None

# Global instance
ai_image_service = AIImageService()

def generate_image_sync(prompt: str, style: str = "children_book") -> Optional[str]:
    """Synchronous image generation"""
    try:
        return ai_image_service.generate_image(prompt, style)
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        # Return simple SVG fallback
        svg_content = f'''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <rect width="512" height="512" fill="#87CEEB"/>
            <text x="256" y="256" font-family="Arial" font-size="20" text-anchor="middle" fill="white">Image Generation Failed</text>
        </svg>'''
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"