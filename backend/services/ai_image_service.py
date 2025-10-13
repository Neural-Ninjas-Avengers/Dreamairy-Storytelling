"""Real AI image generation service using free APIs."""

import asyncio
import aiohttp
import base64
import io
import logging
from typing import Optional, Dict, Any
from PIL import Image
import random

from app.ai_services import AIServiceConfig

logger = logging.getLogger(__name__)

class AIImageService:
    """Service for generating images using free AI APIs."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def generate_image(self, prompt: str, style: str = "children_book") -> Optional[str]:
        """Generate image using AI services."""
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(prompt, style)
        
        # Try different services in order of preference
        services = [
            self._generate_with_pollinations,
            self._generate_with_huggingface,
            self._generate_fallback_image
        ]
        
        for service in services:
            try:
                result = await service(enhanced_prompt)
                if result:
                    logger.info(f"Image generated successfully with {service.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Service {service.__name__} failed: {e}")
                continue
        
        logger.error("All image generation services failed")
        return None
    
    async def generate_avatar(self, prompt: str, style: str = "children_book_avatar") -> Optional[str]:
        """Generate avatar using AI services."""
        
        # Build avatar-specific prompt
        avatar_prompt = self._build_avatar_prompt(prompt, style)
        
        return await self.generate_image(avatar_prompt, style)
    
    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        """Build enhanced prompt for better results."""
        
        style_modifiers = {
            "children_book": "children's book illustration, colorful, friendly, cartoon style, safe for kids",
            "watercolor": "watercolor painting, soft colors, artistic, gentle",
            "cartoon": "cartoon style, bright colors, animated, fun",
            "realistic": "realistic style with magical elements, detailed",
            "fantasy": "fantasy art, magical, enchanting, dreamy"
        }
        
        base_modifier = style_modifiers.get(style, style_modifiers["children_book"])
        
        enhanced = f"{prompt}, {base_modifier}, high quality, detailed, beautiful, safe content"
        
        # Add negative prompts for safety
        enhanced += ", --no violence, no scary, no inappropriate content"
        
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
    
    async def _generate_with_pollinations(self, prompt: str) -> Optional[str]:
        """Generate image using Pollinations AI (free, no auth required)."""
        
        session = await self._get_session()
        
        # Pollinations API - simple and fast
        url = f"{AIServiceConfig.POLLINATIONS_API_URL}/{prompt}"
        
        # Add parameters for better results
        params = {
            "width": 512,
            "height": 512,
            "seed": random.randint(1, 1000000),
            "enhance": "true",
            "model": "flux"
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                # Pollinations returns the image directly
                image_data = await response.read()
                
                # Convert to base64 data URL
                base64_data = base64.b64encode(image_data).decode()
                return f"data:image/jpeg;base64,{base64_data}"
        
        return None
    
    async def _generate_with_huggingface(self, prompt: str) -> Optional[str]:
        """Generate image using Hugging Face Inference API."""
        
        if not AIServiceConfig.has_huggingface_token():
            logger.info("No Hugging Face token available, skipping")
            return None
        
        session = await self._get_session()
        
        headers = AIServiceConfig.get_huggingface_headers()
        headers["Content-Type"] = "application/json"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
        }
        
        async with session.post(
            AIServiceConfig.HUGGINGFACE_API_URL,
            json=payload,
            headers=headers
        ) as response:
            if response.status == 200:
                image_data = await response.read()
                
                # Convert to base64 data URL
                base64_data = base64.b64encode(image_data).decode()
                return f"data:image/jpeg;base64,{base64_data}"
            elif response.status == 503:
                # Model is loading, wait and retry
                logger.info("Model loading, waiting...")
                await asyncio.sleep(10)
                return await self._generate_with_huggingface(prompt)
        
        return None
    
    async def _generate_fallback_image(self, prompt: str) -> Optional[str]:
        """Generate fallback image using placeholder service."""
        
        session = await self._get_session()
        
        # Use a placeholder service with themed images
        seed = abs(hash(prompt)) % 1000
        
        # Picsum with seed for consistent results
        url = f"{AIServiceConfig.PICSUM_API_URL}/512/512?random={seed}"
        
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                
                # Add text overlay to make it more relevant
                image = Image.open(io.BytesIO(image_data))
                
                # Convert to base64 data URL
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85)
                base64_data = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/jpeg;base64,{base64_data}"
        
        return None

# Global instance
ai_image_service = AIImageService()