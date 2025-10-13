"""Configuration for AI services."""

import os
from typing import Optional

class AIServiceConfig:
    """Configuration for AI image generation services."""
    
    # Hugging Face (Free tier)
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Alternative free services
    POLLINATIONS_API_URL = "https://image.pollinations.ai/prompt"
    
    # Fallback service (no auth required)
    PICSUM_API_URL = "https://picsum.photos"
    
    @classmethod
    def get_huggingface_headers(cls) -> dict:
        """Get headers for Hugging Face API."""
        if cls.HUGGINGFACE_TOKEN:
            return {"Authorization": f"Bearer {cls.HUGGINGFACE_TOKEN}"}
        return {}
    
    @classmethod
    def has_huggingface_token(cls) -> bool:
        """Check if Hugging Face token is available."""
        return bool(cls.HUGGINGFACE_TOKEN)