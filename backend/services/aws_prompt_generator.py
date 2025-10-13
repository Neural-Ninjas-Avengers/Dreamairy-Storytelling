#!/usr/bin/env python3
"""
AWS-Compliant Prompt Generator for Child Avatar Creation
Generates safe, policy-compliant prompts for AWS Bedrock Titan image generation
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AWSPromptGenerator:
    """
    Generates AWS Bedrock-compliant prompts for child avatar creation
    Focuses on cartoon/storybook styles to avoid content policy violations
    """
    
    def __init__(self):
        self.safe_styles = {
            "cartoon": "animated cartoon style, Disney/Pixar inspired",
            "storybook": "children's book illustration, whimsical storybook art",
            "anime": "friendly anime style, Studio Ghibli inspired",
            "watercolor": "soft watercolor illustration, gentle children's art"
        }
        
        self.age_appropriate_descriptors = {
            "3-5": {
                "style": "very simple, rounded shapes, bright primary colors",
                "character": "adorable toddler character, chubby cheeks, big eyes",
                "mood": "innocent, playful, cheerful"
            },
            "6-8": {
                "style": "colorful cartoon style, friendly and approachable",
                "character": "young child character, expressive eyes, happy smile",
                "mood": "adventurous, curious, joyful"
            },
            "9-12": {
                "style": "detailed cartoon illustration, vibrant colors",
                "character": "pre-teen character, confident posture, bright expression",
                "mood": "brave, imaginative, enthusiastic"
            }
        }
        
        # Words and phrases to avoid (potential policy triggers)
        self.forbidden_words = [
            "realistic", "photorealistic", "photograph", "photo-like",
            "real person", "actual child", "human face", "portrait",
            "detailed facial features", "lifelike", "3D render"
        ]
        
        # Safe replacement words
        self.safe_replacements = {
            "realistic": "cartoon-style",
            "photorealistic": "stylized illustration",
            "photograph": "drawing",
            "photo-like": "illustration-style",
            "real person": "cartoon character",
            "actual child": "animated character",
            "human face": "cartoon face",
            "portrait": "character illustration",
            "detailed facial features": "expressive cartoon features",
            "lifelike": "animated",
            "3D render": "2D illustration"
        }

    def create_safe_avatar_prompt(self, age: int, style: str = "cartoon", 
                                theme: str = "fantasy", characteristics: Optional[Dict] = None) -> str:
        """
        Create ULTRA-SAFE AWS-compliant prompt for avatar generation
        
        Args:
            age: Child's age (3-12)
            style: Art style preference
            theme: Story theme (fantasy, adventure, etc.)
            characteristics: Optional characteristics dict
            
        Returns:
            Ultra-safe AWS-compliant prompt string
        """
        try:
            # Create ultra-minimal, safe prompt
            base_prompt = f"""Create a simple cartoon mascot character for children's stories.

STYLE: Animated cartoon style, like Disney or Pixar characters
ART: Digital illustration, completely non-realistic, stylized cartoon art
CHARACTER: Friendly cartoon mascot, suitable for children's books
COLORS: Bright, cheerful, family-friendly colors
BACKGROUND: Simple solid color or basic pattern

This should be a basic cartoon character illustration, similar to animated movie characters or children's book illustrations. Completely stylized and cartoon-like, never photographic or realistic."""

            # Only add very safe theme elements
            if theme == "fantasy":
                base_prompt += "\nTHEME: Add simple magical elements like stars or sparkles"
            elif theme == "adventure":
                base_prompt += "\nTHEME: Add simple adventure elements like a hat or compass"
            elif theme == "animals":
                base_prompt += "\nTHEME: Make it an animal-inspired cartoon character"
            
            # Final safety check and sanitization
            safe_prompt = self._sanitize_prompt(base_prompt)
            
            logger.info(f"Generated ULTRA-SAFE AWS prompt for age {age}, style {style}")
            return safe_prompt
            
        except Exception as e:
            logger.error(f"Error generating AWS prompt: {e}")
            return self._get_fallback_prompt(age, style)

    def create_story_image_prompt(self, scene_description: str, age: int, 
                                has_avatar: bool = False, theme: str = "fantasy") -> str:
        """
        Create AWS-compliant prompt for story image generation with avatar
        
        Args:
            scene_description: Description of the scene
            age: Child's age
            has_avatar: Whether to include avatar character
            theme: Story theme
            
        Returns:
            AWS-compliant story image prompt
        """
        try:
            age_group = self._get_age_group(age)
            age_descriptors = self.age_appropriate_descriptors[age_group]
            
            prompt = f"""Create a beautiful children's storybook illustration showing: {scene_description}

ARTISTIC REQUIREMENTS:
- Style: Children's book illustration, completely non-photorealistic
- Art medium: Digital painting, cartoon/animated style
- Color palette: Warm, inviting, magical colors appropriate for age {age}
- Mood: {age_descriptors['mood']}, enchanting, child-friendly

SCENE SPECIFICATIONS:
- Setting: Magical {theme} themed environment
- Atmosphere: Whimsical, safe, adventurous but not scary
- Lighting: Soft, warm, storybook lighting
- Composition: Engaging for {age}-year-old children"""

            if has_avatar:
                prompt += f"""

CHARACTER INTEGRATION:
- Include a cartoon {age_descriptors['character']} as the main character
- Character style: Completely stylized, animated cartoon appearance
- Character role: Friendly protagonist integrated naturally into the scene
- Character design: {age_descriptors['style']}"""

            prompt += f"""

FINAL REQUIREMENTS:
- This MUST be a storybook illustration, never photorealistic
- Perfect for children aged {age}
- Magical, engaging, and completely safe content
- Art style similar to popular children's book illustrations"""

            return self._sanitize_prompt(prompt)
            
        except Exception as e:
            logger.error(f"Error generating story image prompt: {e}")
            return self._get_fallback_story_prompt(scene_description, age)

    def _get_age_group(self, age: int) -> str:
        """Determine age group for appropriate descriptors"""
        if age <= 5:
            return "3-5"
        elif age <= 8:
            return "6-8"
        else:
            return "9-12"

    def _get_theme_elements(self, theme: str) -> str:
        """Get theme-specific elements for prompts"""
        theme_elements = {
            "fantasy": "Magical elements like sparkles, castles, friendly dragons, unicorns",
            "adventure": "Treasure chests, maps, friendly pirates, exploration elements",
            "animals": "Cute forest animals, trees, flowers, natural magical elements",
            "friendship": "Multiple characters interacting, hearts, rainbow elements",
            "space": "Friendly aliens, colorful planets, stars, spaceships",
            "underwater": "Friendly sea creatures, coral, bubbles, mermaids"
        }
        return theme_elements.get(theme, "Magical, whimsical elements appropriate for children")

    def _create_safe_characteristics(self, characteristics: Dict, age: int) -> str:
        """Create safe characteristic descriptions"""
        safe_chars = []
        
        # Hair color (safe)
        if "hair_color" in characteristics:
            hair_color = characteristics["hair_color"]
            safe_chars.append(f"Hair: {hair_color} colored hair in a cartoon style")
        
        # Clothing style (safe)
        if "clothing_style" in characteristics:
            clothing = characteristics["clothing_style"]
            safe_chars.append(f"Outfit: {clothing} in bright, cartoon colors")
        
        # Personality traits (safe)
        if "personality" in characteristics:
            personality = characteristics["personality"]
            safe_chars.append(f"Expression: {personality} cartoon expression")
        
        # Age-appropriate accessories
        age_group = self._get_age_group(age)
        if age_group == "3-5":
            safe_chars.append("Accessories: Simple, colorful cartoon accessories")
        elif age_group == "6-8":
            safe_chars.append("Accessories: Fun, adventurous cartoon accessories")
        else:
            safe_chars.append("Accessories: Cool, imaginative cartoon accessories")
        
        return "\n".join(safe_chars) if safe_chars else ""

    def _sanitize_prompt(self, prompt: str) -> str:
        """Remove potentially problematic words and phrases"""
        sanitized = prompt
        
        # Replace forbidden words
        for forbidden, replacement in self.safe_replacements.items():
            sanitized = re.sub(r'\b' + re.escape(forbidden) + r'\b', 
                             replacement, sanitized, flags=re.IGNORECASE)
        
        # Additional safety checks
        sanitized = re.sub(r'\b(real|actual|photographic|photo)\s+(child|person|face)\b', 
                          'cartoon character', sanitized, flags=re.IGNORECASE)
        
        # Ensure cartoon/animated emphasis
        if "cartoon" not in sanitized.lower() and "animated" not in sanitized.lower():
            sanitized = "Cartoon-style " + sanitized
        
        return sanitized

    def _get_fallback_prompt(self, age: int, style: str) -> str:
        """Get ultra-safe fallback prompt"""
        return f"""Create a simple cartoon mascot character.
        
Art style: Basic cartoon illustration, animated style
Character: Friendly cartoon mascot
Style: Bright colors, simple shapes, child-friendly
Mood: Happy and cheerful

This should be a simple cartoon character, like an animated movie mascot."""
    
    def create_minimal_safe_prompt(self) -> str:
        """Create the most minimal safe prompt possible"""
        return """Create a simple cartoon character illustration.

Style: Animated cartoon, like Disney characters
Art: Digital cartoon illustration, non-realistic
Character: Friendly cartoon mascot
Colors: Bright and cheerful
Background: Simple solid color

This should be a basic cartoon character, completely stylized and animated-looking."""

    def _get_fallback_story_prompt(self, scene: str, age: int) -> str:
        """Get ultra-safe fallback story prompt"""
        return f"""Create a simple children's book illustration.
        
Scene: {scene[:100]}...
Style: Basic cartoon illustration, completely non-realistic
Colors: Bright and cheerful
Mood: Safe and appropriate for age {age}

This should be a simple cartoon drawing suitable for children."""

    def validate_prompt_safety(self, prompt: str) -> tuple[bool, List[str]]:
        """
        Validate prompt for AWS compliance
        
        Returns:
            (is_safe, list_of_issues)
        """
        issues = []
        prompt_lower = prompt.lower()
        
        # Check for forbidden words
        for word in self.forbidden_words:
            if word in prompt_lower:
                issues.append(f"Contains potentially problematic word: {word}")
        
        # Check for required safety elements
        safety_indicators = ["cartoon", "animated", "illustration", "stylized", "non-realistic"]
        if not any(indicator in prompt_lower for indicator in safety_indicators):
            issues.append("Missing clear cartoon/animated style indicators")
        
        # Check for child-appropriate content
        if "child" in prompt_lower and "cartoon" not in prompt_lower:
            issues.append("References child without clear cartoon context")
        
        is_safe = len(issues) == 0
        return is_safe, issues

# Global instance for easy access
aws_prompt_generator = AWSPromptGenerator()