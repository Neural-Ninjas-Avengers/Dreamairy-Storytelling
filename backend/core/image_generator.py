"""Image generation for story illustrations using AI."""

import logging
import json
import base64
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from app.models.core import StorySegment, ChildProfile
from app.services.aws_clients import bedrock_client

logger = logging.getLogger(__name__)


class StoryImageGenerator:
    """Generates illustrations for story segments using AI."""
    
    def __init__(self):
        self.style_templates = {
            "children_book": {
                "base_style": "children's book illustration, colorful, friendly, cartoon style, soft lighting",
                "art_style": "digital art, watercolor style, bright colors, whimsical",
                "mood": "cheerful, safe, magical, wonder"
            },
            "fairy_tale": {
                "base_style": "fairy tale illustration, enchanted, magical, storybook art",
                "art_style": "fantasy art, dreamy, soft pastels, ethereal lighting",
                "mood": "magical, mysterious, beautiful, enchanting"
            },
            "adventure": {
                "base_style": "adventure illustration, dynamic, exciting, colorful",
                "art_style": "cartoon adventure style, bold colors, action-oriented",
                "mood": "exciting, brave, fun, energetic"
            }
        }
        
        # Age-appropriate visual elements
        self.age_styles = {
            (3, 5): {
                "complexity": "simple shapes and forms",
                "colors": "bright primary colors",
                "characters": "round, soft, friendly faces",
                "details": "minimal details, clear simple scenes"
            },
            (6, 8): {
                "complexity": "moderate detail with clear focal points",
                "colors": "vibrant and varied colors",
                "characters": "expressive characters with personality",
                "details": "engaging details without overwhelming"
            },
            (9, 12): {
                "complexity": "rich detail and depth",
                "colors": "sophisticated color palettes",
                "characters": "detailed character expressions and poses",
                "details": "intricate backgrounds and environments"
            }
        }
        
        # Safety filters for image generation
        self.safety_keywords = [
            "safe for children", "family-friendly", "no violence", "no scary elements",
            "positive imagery", "wholesome", "appropriate for kids"
        ]
        
        # Mock image placeholders for offline mode
        self.placeholder_images = {
            "animals": "🐾 A friendly forest scene with cute animals playing together",
            "adventure": "🗺️ An exciting journey through a magical landscape",
            "friendship": "👫 Happy characters sharing a wonderful moment together",
            "magic": "✨ A sparkling magical scene full of wonder and joy",
            "family": "👨‍👩‍👧‍👦 A warm family scene with love and togetherness",
            "nature": "🌳 A beautiful natural setting with flowers and sunshine"
        }
    
    async def generate_story_illustration(
        self, 
        story_segment: StorySegment, 
        profile: ChildProfile,
        story_theme: str = "adventure"
    ) -> Dict[str, Any]:
        """Generate an illustration for a story segment."""
        try:
            # Extract visual elements from story text
            visual_prompt = self._create_image_prompt(story_segment, profile, story_theme)
            
            # Check if we're in offline/mock mode
            if self._should_use_mock_image():
                return self._generate_mock_illustration(story_segment, story_theme)
            
            # Generate image using AI service
            image_data = await self._generate_ai_image(visual_prompt)
            
            return {
                "type": "ai_generated",
                "image_data": image_data,
                "prompt": visual_prompt,
                "style": self._get_style_for_theme(story_theme),
                "alt_text": self._generate_alt_text(story_segment),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return self._generate_fallback_illustration(story_segment, story_theme)
    
    def _create_image_prompt(
        self, 
        story_segment: StorySegment, 
        profile: ChildProfile, 
        theme: str
    ) -> str:
        """Create a detailed prompt for image generation."""
        
        # Get age-appropriate style elements
        age_style = self._get_age_appropriate_style(profile.age)
        base_style = self.style_templates.get(theme, self.style_templates["children_book"])
        
        # Extract key visual elements from story text
        characters = self._extract_visual_characters(story_segment.text)
        setting = self._extract_setting(story_segment.text)
        actions = self._extract_actions(story_segment.text)
        mood = story_segment.emotional_tone or "cheerful"
        
        # Build the prompt
        prompt_parts = [
            # Base style and safety
            base_style["base_style"],
            ", ".join(self.safety_keywords),
            
            # Age-appropriate elements
            age_style["complexity"],
            age_style["colors"],
            age_style["characters"],
            
            # Story-specific elements
            f"Scene: {setting}" if setting else "magical storybook scene",
            f"Characters: {characters}" if characters else "friendly storybook characters",
            f"Action: {actions}" if actions else "peaceful, engaging scene",
            f"Mood: {mood}, {base_style['mood']}",
            
            # Technical specifications
            "high quality illustration",
            "suitable for children's book",
            "no text or words in image",
            "landscape orientation",
            "clear focal point"
        ]
        
        # Join and clean up the prompt
        full_prompt = ", ".join(filter(None, prompt_parts))
        
        # Add negative prompts for safety
        negative_prompts = [
            "scary", "frightening", "dark", "violent", "inappropriate",
            "text", "words", "letters", "adult themes", "complex emotions"
        ]
        
        final_prompt = f"{full_prompt}. Negative prompt: {', '.join(negative_prompts)}"
        
        logger.info(f"Generated image prompt: {final_prompt[:200]}...")
        return final_prompt
    
    def _extract_visual_characters(self, story_text: str) -> str:
        """Extract character descriptions for visual representation."""
        # Look for character names and descriptions
        character_patterns = [
            r'([A-Z][a-z]+)\s+the\s+(rabbit|bear|fox|owl|fairy|dragon|cat|dog|mouse|bird)',
            r'(little|small|big|friendly|wise|brave|curious)\s+([a-z]+)',
            r'([A-Z][a-z]+)\s+(?:was|is)\s+a\s+([^.]+)',
        ]
        
        characters = []
        for pattern in character_patterns:
            matches = re.findall(pattern, story_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    characters.append(" ".join(match))
                else:
                    characters.append(match)
        
        # Limit and clean up
        unique_characters = list(set(characters))[:3]  # Max 3 characters
        return ", ".join(unique_characters) if unique_characters else ""
    
    def _extract_setting(self, story_text: str) -> str:
        """Extract setting descriptions from story text."""
        setting_keywords = {
            "forest": ["forest", "trees", "woods", "woodland"],
            "meadow": ["meadow", "field", "grass", "flowers"],
            "house": ["house", "home", "cottage", "burrow"],
            "garden": ["garden", "yard", "plants", "flowers"],
            "playground": ["playground", "park", "swings", "slide"],
            "magical place": ["magical", "enchanted", "fairy", "sparkle", "glow"],
            "adventure": ["path", "journey", "explore", "adventure", "quest"]
        }
        
        story_lower = story_text.lower()
        for setting, keywords in setting_keywords.items():
            if any(keyword in story_lower for keyword in keywords):
                return setting
        
        return "peaceful storybook scene"
    
    def _extract_actions(self, story_text: str) -> str:
        """Extract main actions or activities from story text."""
        action_keywords = [
            "playing", "exploring", "walking", "running", "jumping",
            "talking", "laughing", "smiling", "hugging", "helping",
            "discovering", "finding", "looking", "searching", "meeting"
        ]
        
        story_lower = story_text.lower()
        found_actions = [action for action in action_keywords if action in story_lower]
        
        return ", ".join(found_actions[:3]) if found_actions else "peaceful interaction"
    
    def _get_age_appropriate_style(self, age: int) -> Dict[str, str]:
        """Get age-appropriate visual style elements."""
        for age_range, style in self.age_styles.items():
            if age_range[0] <= age <= age_range[1]:
                return style
        return self.age_styles[(6, 8)]  # Default to middle age group
    
    def _get_style_for_theme(self, theme: str) -> str:
        """Get the appropriate visual style for a theme."""
        theme_mapping = {
            "animals": "children_book",
            "friendship": "children_book", 
            "family": "children_book",
            "adventure": "adventure",
            "magic": "fairy_tale",
            "nature": "children_book"
        }
        return theme_mapping.get(theme, "children_book")
    
    def _should_use_mock_image(self) -> bool:
        """Determine if we should use mock images instead of AI generation."""
        # Check if we're in offline mode or if AI service is unavailable
        try:
            from backend.services.dynamic_client_selector import should_use_aws_services
            return not should_use_aws_services()
        except:
            return True  # Default to mock mode if settings unavailable
    
    async def _generate_ai_image(self, prompt: str) -> str:
        """Generate image using AI service (DALL-E or similar)."""
        try:
            # This would integrate with actual AI image generation service
            # For now, we'll simulate the API call
            
            # In production, this would call something like:
            # image_response = await bedrock_client.generate_image(prompt)
            # return image_response.image_data
            
            # Simulate API delay
            await asyncio.sleep(2)
            
            # Return mock base64 image data
            return self._create_mock_base64_image()
            
        except Exception as e:
            logger.error(f"AI image generation failed: {e}")
            raise
    
    def _generate_mock_illustration(self, story_segment: StorySegment, theme: str) -> Dict[str, Any]:
        """Generate a mock illustration for demo purposes."""
        
        # Determine the best placeholder based on story content
        story_lower = story_segment.text.lower()
        
        best_match = "adventure"  # default
        max_matches = 0
        
        for placeholder_theme, description in self.placeholder_images.items():
            # Count keyword matches
            theme_keywords = {
                "animals": ["animal", "rabbit", "bear", "fox", "cat", "dog", "bird"],
                "adventure": ["adventure", "journey", "explore", "path", "quest"],
                "friendship": ["friend", "together", "play", "share", "help"],
                "magic": ["magic", "fairy", "sparkle", "glow", "enchant"],
                "family": ["family", "home", "together", "love", "care"],
                "nature": ["forest", "tree", "flower", "garden", "meadow"]
            }
            
            keywords = theme_keywords.get(placeholder_theme, [])
            matches = sum(1 for keyword in keywords if keyword in story_lower)
            
            if matches > max_matches:
                max_matches = matches
                best_match = placeholder_theme
        
        return {
            "type": "mock_illustration",
            "placeholder_text": self.placeholder_images[best_match],
            "theme": best_match,
            "style": self._get_style_for_theme(theme),
            "alt_text": self._generate_alt_text(story_segment),
            "mock_image_data": self._create_mock_svg_image(best_match),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_fallback_illustration(self, story_segment: StorySegment, theme: str) -> Dict[str, Any]:
        """Generate a simple fallback illustration when all else fails."""
        return {
            "type": "fallback",
            "placeholder_text": "🎨 A beautiful illustration would appear here",
            "theme": theme,
            "alt_text": "Story illustration",
            "svg_data": self._create_simple_svg(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_alt_text(self, story_segment: StorySegment) -> str:
        """Generate descriptive alt text for accessibility."""
        # Extract key elements for alt text
        text_snippet = story_segment.text[:100] + "..." if len(story_segment.text) > 100 else story_segment.text
        
        # Create descriptive alt text
        alt_text = f"Illustration showing: {text_snippet}"
        
        # Add emotional context
        if story_segment.emotional_tone:
            alt_text += f" The scene has a {story_segment.emotional_tone} mood."
        
        return alt_text
    
    def _create_mock_base64_image(self) -> str:
        """Create a mock base64 encoded image for testing."""
        # This would be replaced with actual image data in production
        # For now, return a simple placeholder
        return "data:image/svg+xml;base64," + base64.b64encode(
            self._create_simple_svg().encode()
        ).decode()
    
    def _create_mock_svg_image(self, theme: str) -> str:
        """Create a themed SVG illustration for mock mode."""
        
        svg_templates = {
            "animals": '''
                <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#98FB98;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect width="400" height="300" fill="url(#skyGrad)"/>
                    <circle cx="100" cy="180" r="40" fill="#DEB887" stroke="#8B4513" stroke-width="2"/>
                    <circle cx="85" cy="170" r="3" fill="#000"/>
                    <circle cx="115" cy="170" r="3" fill="#000"/>
                    <ellipse cx="100" cy="185" rx="8" ry="5" fill="#000"/>
                    <text x="200" y="50" font-family="Arial" font-size="24" fill="#4169E1" text-anchor="middle">🌟 Story Illustration 🌟</text>
                    <text x="200" y="250" font-family="Arial" font-size="16" fill="#2F4F4F" text-anchor="middle">Friendly Forest Friends</text>
                </svg>
            ''',
            "adventure": '''
                <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="adventureGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#FF6347;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect width="400" height="300" fill="url(#adventureGrad)"/>
                    <polygon points="50,250 150,100 250,250" fill="#228B22" opacity="0.8"/>
                    <polygon points="200,250 300,120 350,250" fill="#32CD32" opacity="0.8"/>
                    <circle cx="80" cy="80" r="30" fill="#FFD700" opacity="0.9"/>
                    <text x="200" y="50" font-family="Arial" font-size="24" fill="#FFFFFF" text-anchor="middle">⭐ Adventure Awaits ⭐</text>
                    <text x="200" y="280" font-family="Arial" font-size="16" fill="#FFFFFF" text-anchor="middle">Magical Journey Begins</text>
                </svg>
            ''',
            "friendship": '''
                <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <rect width="400" height="300" fill="#F0E68C"/>
                    <circle cx="150" cy="150" r="30" fill="#FFB6C1"/>
                    <circle cx="250" cy="150" r="30" fill="#87CEFA"/>
                    <circle cx="135" cy="140" r="3" fill="#000"/>
                    <circle cx="165" cy="140" r="3" fill="#000"/>
                    <circle cx="235" cy="140" r="3" fill="#000"/>
                    <circle cx="265" cy="140" r="3" fill="#000"/>
                    <path d="M 140 160 Q 150 170 160 160" stroke="#000" stroke-width="2" fill="none"/>
                    <path d="M 240 160 Q 250 170 260 160" stroke="#000" stroke-width="2" fill="none"/>
                    <text x="200" y="50" font-family="Arial" font-size="24" fill="#4B0082" text-anchor="middle">💕 Best Friends 💕</text>
                    <text x="200" y="250" font-family="Arial" font-size="16" fill="#4B0082" text-anchor="middle">Friendship and Fun</text>
                </svg>
            ''',
            "magic": '''
                <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <radialGradient id="magicGrad" cx="50%" cy="50%" r="50%">
                            <stop offset="0%" style="stop-color:#9370DB;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#4B0082;stop-opacity:1" />
                        </radialGradient>
                    </defs>
                    <rect width="400" height="300" fill="url(#magicGrad)"/>
                    <circle cx="100" cy="100" r="3" fill="#FFD700" opacity="0.8">
                        <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="300" cy="80" r="2" fill="#FFFFFF" opacity="0.9">
                        <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="150" cy="200" r="4" fill="#FFD700" opacity="0.7">
                        <animate attributeName="opacity" values="0.2;1;0.2" dur="3s" repeatCount="indefinite"/>
                    </circle>
                    <text x="200" y="50" font-family="Arial" font-size="24" fill="#FFD700" text-anchor="middle">✨ Magical World ✨</text>
                    <text x="200" y="280" font-family="Arial" font-size="16" fill="#FFFFFF" text-anchor="middle">Where Dreams Come True</text>
                </svg>
            '''
        }
        
        return svg_templates.get(theme, svg_templates["adventure"])
    
    def _create_simple_svg(self) -> str:
        """Create a simple fallback SVG."""
        return '''
            <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="300" fill="#E6E6FA"/>
                <circle cx="200" cy="150" r="50" fill="#DDA0DD" opacity="0.8"/>
                <text x="200" y="100" font-family="Arial" font-size="20" fill="#4B0082" text-anchor="middle">🎨</text>
                <text x="200" y="200" font-family="Arial" font-size="16" fill="#4B0082" text-anchor="middle">Story Illustration</text>
            </svg>
        '''


class ImageStyleManager:
    """Manages different illustration styles and themes."""
    
    def __init__(self):
        self.style_presets = {
            "watercolor": {
                "description": "Soft watercolor style with gentle colors",
                "keywords": ["watercolor", "soft", "flowing", "gentle brushstrokes"]
            },
            "cartoon": {
                "description": "Bright cartoon style with bold colors",
                "keywords": ["cartoon", "bold colors", "clear lines", "playful"]
            },
            "storybook": {
                "description": "Classic children's book illustration style",
                "keywords": ["storybook art", "traditional", "warm colors", "detailed"]
            },
            "minimalist": {
                "description": "Simple, clean illustration style",
                "keywords": ["minimalist", "simple shapes", "clean", "uncluttered"]
            }
        }
    
    def get_style_prompt(self, style_name: str, age: int) -> str:
        """Get style-specific prompt additions."""
        style = self.style_presets.get(style_name, self.style_presets["storybook"])
        
        # Adjust complexity based on age
        if age <= 5:
            complexity = "simple and clear"
        elif age <= 8:
            complexity = "moderately detailed"
        else:
            complexity = "richly detailed"
        
        return f"{style['description']}, {complexity}, {', '.join(style['keywords'])}"


# Global instance
image_generator = StoryImageGenerator()