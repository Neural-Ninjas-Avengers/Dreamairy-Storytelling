"""Story generation and adaptation engine using Amazon Bedrock."""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from app.core.interfaces import StoryGeneratorInterface
from app.models.core import (
    ChildProfile, StorySegment, StoryContext, EmotionState, 
    EmotionalGoal, EmotionType, Character
)
from backend.services.dynamic_client_selector import get_current_bedrock_client
from app.core.image_generator import image_generator

logger = logging.getLogger(__name__)


class StoryTemplateManager:
    """Manages story templates and prompts for different scenarios."""
    
    def __init__(self):
        # Age-appropriate story themes and elements
        self.age_themes = {
            (3, 5): {
                "themes": ["animals", "friendship", "family", "simple adventures", "colors", "shapes"],
                "vocabulary_level": "simple",
                "sentence_length": "short",
                "concepts": ["sharing", "kindness", "helping", "basic emotions"]
            },
            (6, 8): {
                "themes": ["adventure", "magic", "school", "pets", "nature", "problem-solving"],
                "vocabulary_level": "elementary",
                "sentence_length": "medium",
                "concepts": ["teamwork", "courage", "friendship", "learning", "creativity"]
            },
            (9, 12): {
                "themes": ["mystery", "fantasy", "science", "friendship challenges", "growing up"],
                "vocabulary_level": "intermediate",
                "sentence_length": "varied",
                "concepts": ["responsibility", "perseverance", "empathy", "decision-making"]
            }
        }
        
        # Story structure templates
        self.story_structures = {
            "simple_adventure": {
                "opening": "character introduction and setting",
                "challenge": "simple problem or goal",
                "journey": "steps to solve the problem",
                "resolution": "happy ending with lesson"
            },
            "friendship_story": {
                "opening": "characters meeting or playing",
                "conflict": "misunderstanding or disagreement",
                "learning": "characters learn about each other",
                "resolution": "friendship strengthened"
            },
            "magical_journey": {
                "opening": "discovery of magical element",
                "adventure": "magical world exploration",
                "challenge": "magical problem to solve",
                "return": "return with new wisdom"
            }
        }
        
        # Emotional goal-specific elements
        self.emotional_elements = {
            EmotionalGoal.CALM: {
                "tone": "gentle and soothing",
                "pace": "slow and peaceful",
                "settings": ["quiet forest", "cozy bedroom", "peaceful garden", "starry night"],
                "activities": ["sleeping", "dreaming", "gentle walks", "quiet conversations"],
                "characters": ["wise owl", "gentle bear", "sleepy bunny", "kind fairy"]
            },
            EmotionalGoal.ENTERTAIN: {
                "tone": "playful and engaging",
                "pace": "varied with exciting moments",
                "settings": ["playground", "circus", "magical kingdom", "adventure island"],
                "activities": ["playing games", "solving puzzles", "funny mishaps", "celebrations"],
                "characters": ["funny monkey", "clever fox", "playful puppy", "silly dragon"]
            },
            EmotionalGoal.STIMULATE_PLAY: {
                "tone": "interactive and energetic",
                "pace": "dynamic with participation cues",
                "settings": ["treasure hunt", "obstacle course", "mystery house", "game world"],
                "activities": ["searching", "jumping", "clapping", "singing", "dancing"],
                "characters": ["brave explorer", "energetic rabbit", "curious cat", "adventure guide"]
            }
        }
    
    def get_age_appropriate_elements(self, age: int) -> Dict[str, Any]:
        """Get age-appropriate story elements."""
        for age_range, elements in self.age_themes.items():
            if age_range[0] <= age <= age_range[1]:
                return elements
        
        # Default to middle age group
        return self.age_themes[(6, 8)]
    
    def create_initial_story_prompt(self, profile: ChildProfile, theme: str, language: str = 'en') -> str:
        """Create initial story generation prompt."""
        age_elements = self.get_age_appropriate_elements(profile.age)
        emotional_elements = self.emotional_elements.get(profile.emotional_goal, {})
        
        # Language-specific instructions
        language_instructions = {
            'en': "CRITICAL: Write the ENTIRE story in ENGLISH. Every word must be in English.",
            'es': "CRÍTICO: Escribe TODA la historia en ESPAÑOL. Cada palabra debe estar en español."
        }
        language_instruction = language_instructions.get(language, language_instructions['en'])
        
        # Build character preferences
        character_prefs = ""
        if profile.preferences:
            character_prefs = f"The child loves: {', '.join(profile.preferences)}. "
        
        # Build character name
        character_name = ""
        if profile.name:
            character_name = f"The main character should be named {profile.name}. "
        
        # Build gender specification
        gender_spec = ""
        if profile.gender:
            logger.info(f"🎭 Profile gender received: '{profile.gender}'")
            if profile.gender.lower() in ['niña', 'girl', 'female']:
                gender_spec = "The main character MUST be a GIRL (una niña). "
                logger.info("✅ Gender set to GIRL")
            elif profile.gender.lower() in ['niño', 'boy', 'male']:
                gender_spec = "The main character MUST be a BOY (un niño). "
                logger.info("✅ Gender set to BOY")
            else:
                logger.warning(f"⚠️ Unknown gender value: '{profile.gender}'")
        else:
            logger.warning("⚠️ No gender provided in profile")
        
        # Create gender-specific language
        gender_pronoun = ""
        gender_article = ""
        if profile.gender:
            if profile.gender.lower() in ['niña', 'girl', 'female']:
                gender_pronoun = "she/her"
                gender_article = "a girl"
            elif profile.gender.lower() in ['niño', 'boy', 'male']:
                gender_pronoun = "he/him"
                gender_article = "a boy"
        
        prompt = f"""Create a children's story beginning for a {profile.age}-year-old child.

{language_instruction}

CRITICAL REQUIREMENTS - MUST FOLLOW:
1. CHARACTER NAME: {f"The main character MUST be named {profile.name}" if profile.name else "Create a main character"}
2. CHARACTER GENDER: {gender_spec if gender_spec else "Choose an appropriate gender"}
   {f"- Use pronouns: {gender_pronoun}" if gender_pronoun else ""}
   {f"- The protagonist is {gender_article}" if gender_article else ""}
   - DO NOT use the opposite gender under any circumstances

Theme: {theme}
Tone: {emotional_elements.get('tone', 'engaging')}
{character_prefs}

Include:
- A {age_elements['vocabulary_level']} vocabulary level
- {age_elements['sentence_length']} sentences
- Setting from: {emotional_elements.get('settings', ['magical place'])}
- Main character{f" named {profile.name}" if profile.name else ""} who is {gender_article if gender_article else "a child, animal, or magical being"}
- 1-2 supporting characters
- A gentle challenge or adventure beginning

Style: Vivid but simple, include dialogue, create emotional connection, end with anticipation.

IMPORTANT: Write a SHORT but COMPLETE chapter for a children's story. The chapter should have a natural beginning and end with a complete sentence (ending with a period). Do NOT cut off mid-sentence. Approximately 3-5 complete sentences.

REMEMBER: The main character is {gender_article if gender_article else "the protagonist"}{f" named {profile.name}" if profile.name else ""}.

Write the story chapter now (short but complete):"""

        return prompt
    
    def create_adaptation_prompt(
        self, 
        current_context: StoryContext, 
        emotion: EmotionState, 
        goal: EmotionalGoal
    ) -> str:
        """Create prompt for story adaptation based on detected emotion."""
        
        # Language-specific instructions
        language = current_context.target_language or 'en'
        language_instructions = {
            'en': "CRITICAL: Write the ENTIRE continuation in ENGLISH. Every word must be in English.",
            'es': "CRÍTICO: Escribe TODA la continuación en ESPAÑOL. Cada palabra debe estar en español."
        }
        language_instruction = language_instructions.get(language, language_instructions['en'])
        logger.info(f"🌍 Generating continuation in language: {language}")
        
        # Analyze current emotional state
        emotion_description = self._describe_emotion_state(emotion)
        adaptation_strategy = self._get_adaptation_strategy(emotion, goal)
        
        # Get current story elements
        current_segment = current_context.current_segment[-500:] if current_context.current_segment else ""
        characters = [char.name for char in current_context.characters]
        
        # Build gender specification for continuity
        gender_spec = ""
        gender_pronoun = ""
        gender_article = ""
        if current_context.target_gender:
            logger.info(f"🎭 Continuation - using gender: '{current_context.target_gender}'")
            if current_context.target_gender.lower() in ['niña', 'girl', 'female']:
                gender_spec = "The main character is a GIRL (una niña). "
                gender_pronoun = "she/her"
                gender_article = "a girl"
                logger.info("✅ Continuation gender set to GIRL")
            elif current_context.target_gender.lower() in ['niño', 'boy', 'male']:
                gender_spec = "The main character is a BOY (un niño). "
                gender_pronoun = "he/him"
                gender_article = "a boy"
                logger.info("✅ Continuation gender set to BOY")
        else:
            logger.warning("⚠️ No gender in story context for continuation")
        
        prompt = f"""Continue this story. Previous: "{current_segment}"

{language_instruction}

Context:
- Age: {current_context.target_age}, Theme: {current_context.theme}
- Characters: {', '.join(characters) if characters else 'TBD'}
- Setting: {current_context.setting}
- Emotion: {emotion_description}
- Strategy: {adaptation_strategy}

CRITICAL - CHARACTER CONSISTENCY:
{gender_spec if gender_spec else ""}
{f"- Use pronouns: {gender_pronoun}" if gender_pronoun else ""}
{f"- The protagonist is {gender_article}" if gender_article else ""}
- DO NOT change the character's gender from the previous segment
- Maintain ALL character traits from previous segments

Requirements:
- Maintain continuity and character consistency
- Adapt tone/pace based on emotional state
- Include dialogue
- Natural progression
- Gentle transition

{self._get_specific_adaptation_instructions(emotion, goal)}

IMPORTANT: Write a SHORT but COMPLETE chapter continuation. The chapter should flow naturally from the previous segment and end with a complete sentence (ending with a period). Do NOT cut off mid-sentence. Approximately 3-5 complete sentences.

REMEMBER: Keep the same character gender as in the previous segment{f" ({gender_article})" if gender_article else ""}.

Write continuation (short but complete):"""

        return prompt
    
    def _describe_emotion_state(self, emotion: EmotionState) -> str:
        """Describe the child's emotional state for the AI."""
        descriptions = {
            EmotionType.JOY: f"The child is feeling happy and joyful (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.EXCITEMENT: f"The child is excited and energetic (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.CALM: f"The child is calm and peaceful (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.SADNESS: f"The child seems sad or disappointed (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.FEAR: f"The child appears worried or scared (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.BOREDOM: f"The child seems bored or disengaged (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.ANXIETY: f"The child appears anxious or restless (confidence: {emotion.confidence:.1f}, intensity: {emotion.intensity:.1f})",
            EmotionType.NEUTRAL: f"The child has a neutral emotional state (confidence: {emotion.confidence:.1f})"
        }
        
        return descriptions.get(emotion.primary_emotion, f"The child's emotional state is {emotion.primary_emotion.value}")
    
    def _get_adaptation_strategy(self, emotion: EmotionState, goal: EmotionalGoal) -> str:
        """Get adaptation strategy based on emotion and goal."""
        
        strategies = {
            (EmotionType.BOREDOM, EmotionalGoal.ENTERTAIN): "Introduce exciting new elements, unexpected twists, or interactive moments to recapture attention",
            (EmotionType.FEAR, EmotionalGoal.CALM): "Introduce comforting characters, reassuring dialogue, and gentle resolution of scary elements",
            (EmotionType.EXCITEMENT, EmotionalGoal.CALM): "Gradually slow the pace, introduce peaceful settings, and use soothing language",
            (EmotionType.SADNESS, EmotionalGoal.ENTERTAIN): "Introduce uplifting characters, gentle humor, and positive story developments",
            (EmotionType.JOY, EmotionalGoal.ENTERTAIN): "Maintain the positive energy with fun adventures and celebratory moments",
            (EmotionType.CALM, EmotionalGoal.STIMULATE_PLAY): "Gradually introduce more interactive elements and engaging activities"
        }
        
        key = (emotion.primary_emotion, goal)
        return strategies.get(key, "Continue the story naturally while being mindful of the child's emotional state")
    
    def _get_specific_adaptation_instructions(self, emotion: EmotionState, goal: EmotionalGoal) -> str:
        """Get specific instructions for story adaptation."""
        
        if emotion.primary_emotion == EmotionType.BOREDOM:
            return """
Specific Instructions for Boredom:
- Introduce a surprising new character or magical element
- Add interactive questions like "What would you do?" or "Can you help [character]?"
- Include sound effects or actions the child can mimic
- Create a mini-mystery or puzzle within the story
"""
        
        elif emotion.primary_emotion == EmotionType.FEAR:
            return """
Specific Instructions for Fear:
- Introduce a brave, protective character
- Use reassuring language and gentle explanations
- Transform scary elements into friendly or silly ones
- Include comforting dialogue from characters
"""
        
        elif emotion.primary_emotion == EmotionType.EXCITEMENT:
            if goal == EmotionalGoal.CALM:
                return """
Specific Instructions for High Excitement (Calming Goal):
- Slow down the narrative pace
- Introduce peaceful, quiet activities
- Use softer, more soothing language
- Guide characters toward restful or contemplative moments
"""
            else:
                return """
Specific Instructions for Excitement:
- Match the energy with dynamic story elements
- Include celebratory moments and achievements
- Add interactive elements that channel the excitement
"""
        
        elif emotion.primary_emotion == EmotionType.SADNESS:
            return """
Specific Instructions for Sadness:
- Introduce empathetic characters who understand feelings
- Include gentle problem-solving and support
- Add hopeful elements and positive outcomes
- Use warm, comforting language
"""
        
        return "Continue naturally while being responsive to the child's emotional needs."


class StoryGenerator(StoryGeneratorInterface):
    """Main story generator using Bedrock AI."""
    
    def __init__(self):
        self.template_manager = StoryTemplateManager()
        self.content_filter = ContentFilter()
        
        # Story generation parameters
        self.max_tokens = 800
        self.temperature = 0.7
        
    async def generate_initial_story(self, profile: ChildProfile, theme: str, language: str = 'en') -> StorySegment:
        """Generate the initial story segment."""
        try:
            # Create the prompt with language
            logger.info(f"🌍 Generating initial story in language: {language}")
            prompt = self.template_manager.create_initial_story_prompt(profile, theme, language)
            
            # Generate story using appropriate client (AWS or mock)
            bedrock_client = get_current_bedrock_client()
            story_text = await bedrock_client.generate_story(prompt, self.max_tokens)
            
            # Log word count for monitoring
            word_count = len(story_text.split())
            logger.info(f"Story generated with {word_count} words (target: 80)")
            
            # Validate content appropriateness
            if not self.validate_content_appropriateness(story_text, profile.age):
                logger.warning("Generated content failed appropriateness check, regenerating...")
                # Try again with more restrictive prompt
                safer_prompt = prompt + "\n\nIMPORTANT: Ensure all content is completely appropriate for young children."
                story_text = await bedrock_client.generate_story(safer_prompt, self.max_tokens)
            
            # Extract characters from the story
            characters = self._extract_characters(story_text)
            
            # Create story segment
            story_segment = StorySegment(
                text=story_text.strip(),
                emotional_tone="neutral",
                pacing="normal",
                characters_involved=[char.name for char in characters],
                sequence_number=1
            )
            
            # Generate illustration for the story segment
            try:
                illustration = await image_generator.generate_story_illustration(
                    story_segment, profile, theme
                )
                story_segment.illustration = illustration
                logger.info("Generated illustration for initial story segment")
            except Exception as e:
                logger.warning(f"Failed to generate illustration: {e}")
                # Continue without illustration
            
            return story_segment
            
        except Exception as e:
            logger.error(f"Initial story generation failed: {e}")
            return self._create_fallback_story(profile, theme)
    
    async def adapt_story_segment(
        self, 
        current_context: StoryContext, 
        emotion: EmotionState, 
        goal: EmotionalGoal
    ) -> StorySegment:
        """Adapt story based on current emotion and goal."""
        try:
            # Create adaptation prompt
            prompt = self.template_manager.create_adaptation_prompt(current_context, emotion, goal)
            
            # Generate adapted story segment using appropriate client
            bedrock_client = get_current_bedrock_client()
            story_text = await bedrock_client.generate_story(prompt, self.max_tokens)
            
            # Log word count for monitoring
            word_count = len(story_text.split())
            logger.info(f"Adapted story generated with {word_count} words (target: 80)")
            
            # Validate content
            if not self.validate_content_appropriateness(story_text, current_context.target_age):
                logger.warning("Adapted content failed appropriateness check")
                story_text = self._create_safe_adaptation(current_context, emotion)
            
            # Determine emotional tone and pacing based on adaptation
            emotional_tone, pacing = self._determine_story_characteristics(emotion, goal)
            
            # Create story segment
            story_segment = StorySegment(
                text=story_text.strip(),
                emotional_tone=emotional_tone,
                pacing=pacing,
                characters_involved=[char.name for char in current_context.characters],
                adaptation_reason=f"Adapted for {emotion.primary_emotion.value} emotion",
                sequence_number=len(current_context.plot_points) + 1
            )
            
            # Generate illustration for the adapted segment
            try:
                # Create a temporary profile for image generation
                temp_profile = ChildProfile(age=current_context.target_age)
                illustration = await image_generator.generate_story_illustration(
                    story_segment, temp_profile, current_context.theme
                )
                story_segment.illustration = illustration
                logger.info("Generated illustration for adapted story segment")
            except Exception as e:
                logger.warning(f"Failed to generate illustration for adaptation: {e}")
                # Continue without illustration
            
            return story_segment
            
        except Exception as e:
            logger.error(f"Story adaptation failed: {e}")
            return self._create_fallback_adaptation(current_context, emotion)
    
    async def generate_story_conclusion(self, story_context: StoryContext) -> StorySegment:
        """Generate an appropriate story conclusion."""
        try:
            prompt = f"""Create a satisfying conclusion for this children's story.

Story Context:
- Child's Age: {story_context.target_age}
- Theme: {story_context.theme}
- Characters: {', '.join([char.name for char in story_context.characters])}
- Setting: {story_context.setting}
- Recent Story: "{story_context.current_segment[-300:] if story_context.current_segment else ''}"

Conclusion Requirements:
- Provide a satisfying, happy ending
- Reinforce positive themes and lessons
- Include all main characters in the resolution
- Use age-appropriate language and concepts
- End with a warm, comforting note
- Include a gentle moral or lesson learned

IMPORTANT: Write a SHORT but COMPLETE conclusion chapter. The chapter should provide a satisfying ending and finish with a complete sentence (ending with a period). Do NOT cut off mid-sentence. Approximately 3-5 complete sentences.

Write the conclusion now (short but complete):"""

            story_text = await bedrock_client.generate_story(prompt, self.max_tokens)
            
            if not self.validate_content_appropriateness(story_text, story_context.target_age):
                story_text = self._create_safe_conclusion(story_context)
            
            return StorySegment(
                text=story_text.strip(),
                emotional_tone="warm",
                pacing="gentle",
                characters_involved=[char.name for char in story_context.characters],
                adaptation_reason="Story conclusion",
                sequence_number=len(story_context.plot_points) + 1
            )
            
        except Exception as e:
            logger.error(f"Story conclusion generation failed: {e}")
            return self._create_fallback_conclusion(story_context)
    
    def validate_content_appropriateness(self, content: str, age: int) -> bool:
        """Validate that content is appropriate for the target age."""
        return self.content_filter.is_appropriate(content, age)
    
    def _extract_characters(self, story_text: str) -> List[Character]:
        """Extract character information from story text."""
        characters = []
        
        # Simple character extraction based on common patterns
        # In production, this could be more sophisticated
        character_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|is|said|asked|smiled|laughed|walked)',
            r'"[^"]*,"\s+said\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s+the\s+(?:rabbit|bear|fox|owl|fairy|dragon|cat|dog|mouse)'
        ]
        
        found_names = set()
        for pattern in character_patterns:
            matches = re.findall(pattern, story_text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if len(match) > 2 and len(match) < 20:  # Reasonable name length
                    found_names.add(match)
        
        # Create character objects
        for name in found_names:
            # Infer character type from name or context
            personality_traits = self._infer_character_traits(name, story_text)
            
            character = Character(
                name=name,
                description=f"A character in the story",
                personality_traits=personality_traits
            )
            characters.append(character)
        
        return characters[:5]  # Limit to 5 characters max
    
    def _infer_character_traits(self, name: str, story_text: str) -> List[str]:
        """Infer character traits from name and story context."""
        traits = []
        
        # Simple trait inference based on common patterns
        name_lower = name.lower()
        story_lower = story_text.lower()
        
        trait_keywords = {
            "brave": ["brave", "courageous", "bold"],
            "kind": ["kind", "gentle", "caring", "helpful"],
            "wise": ["wise", "smart", "clever", "thoughtful"],
            "playful": ["playful", "fun", "silly", "energetic"],
            "curious": ["curious", "wondering", "exploring", "asking"]
        }
        
        for trait, keywords in trait_keywords.items():
            for keyword in keywords:
                if keyword in story_lower and name_lower in story_lower:
                    # Check if the keyword appears near the character name
                    name_positions = [m.start() for m in re.finditer(name_lower, story_lower)]
                    keyword_positions = [m.start() for m in re.finditer(keyword, story_lower)]
                    
                    for name_pos in name_positions:
                        for keyword_pos in keyword_positions:
                            if abs(name_pos - keyword_pos) < 100:  # Within 100 characters
                                traits.append(trait)
                                break
                        if trait in traits:
                            break
        
        return traits[:3]  # Limit to 3 traits
    
    def _determine_story_characteristics(self, emotion: EmotionState, goal: EmotionalGoal) -> tuple:
        """Determine emotional tone and pacing based on emotion and goal."""
        
        # Emotional tone mapping
        tone_mapping = {
            EmotionType.JOY: "joyful",
            EmotionType.EXCITEMENT: "energetic",
            EmotionType.CALM: "peaceful",
            EmotionType.SADNESS: "gentle",
            EmotionType.FEAR: "reassuring",
            EmotionType.BOREDOM: "engaging",
            EmotionType.NEUTRAL: "balanced"
        }
        
        # Pacing mapping
        pace_mapping = {
            (EmotionType.EXCITEMENT, EmotionalGoal.ENTERTAIN): "fast",
            (EmotionType.BOREDOM, EmotionalGoal.ENTERTAIN): "varied",
            (EmotionType.FEAR, EmotionalGoal.CALM): "slow",
            (EmotionType.CALM, EmotionalGoal.STIMULATE_PLAY): "building"
        }
        
        emotional_tone = tone_mapping.get(emotion.primary_emotion, "balanced")
        pacing = pace_mapping.get((emotion.primary_emotion, goal), "normal")
        
        return emotional_tone, pacing
    
    def _truncate_to_word_limit(self, text: str, word_limit: int) -> str:
        """Truncate text to exact word limit, trying to end at sentence boundary."""
        words = text.split()
        
        if len(words) <= word_limit:
            return text
        
        # Truncate to word limit
        truncated_words = words[:word_limit]
        truncated_text = ' '.join(truncated_words)
        
        # Try to end at a sentence boundary
        last_period = truncated_text.rfind('.')
        last_exclamation = truncated_text.rfind('!')
        last_question = truncated_text.rfind('?')
        
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        # If we found a sentence ending in the last 20% of the text, use it
        if last_sentence_end > len(truncated_text) * 0.8:
            return truncated_text[:last_sentence_end + 1]
        
        # Otherwise, just add ellipsis
        return truncated_text + '...'
    
    def _create_fallback_story(self, profile: ChildProfile, theme: str) -> StorySegment:
        """Create a simple fallback story when AI generation fails."""
        
        fallback_stories = {
            "animals": f"Once upon a time, there was a friendly little rabbit named Rosie. Rosie lived in a cozy burrow under a big oak tree. Every morning, she would hop out to explore the meadow and make new friends. Today felt like a special day for an adventure!",
            
            "friendship": f"In a sunny playground, there lived a kind little bear named Benny. Benny loved to play and share his toys with everyone. One day, he met a shy little fox who was sitting alone. 'Would you like to play with me?' asked Benny with a warm smile.",
            
            "adventure": f"Deep in an enchanted forest, there was a magical path that sparkled in the sunlight. A curious little explorer named Alex discovered this path while picking flowers. 'I wonder where this leads?' Alex thought, taking the first step on an amazing journey."
        }
        
        story_text = fallback_stories.get(theme, fallback_stories["animals"])
        
        return StorySegment(
            text=story_text,
            emotional_tone="warm",
            pacing="gentle",
            characters_involved=["Main Character"],
            sequence_number=1
        )
    
    def _create_fallback_adaptation(self, context: StoryContext, emotion: EmotionState) -> StorySegment:
        """Create a simple adaptation when AI generation fails."""
        
        adaptations = {
            EmotionType.BOREDOM: "Suddenly, something magical happened! A colorful butterfly landed nearby and began to glow with a soft, beautiful light. 'Follow me!' it seemed to say with its gentle flutter.",
            
            EmotionType.FEAR: "Just then, a wise and gentle character appeared. 'Don't worry,' they said with a kind smile. 'Everything is going to be just fine. Let me show you something wonderful.'",
            
            EmotionType.SADNESS: "At that moment, all the characters gathered around with warm hugs and encouraging words. 'We're here for you,' they said. 'Together, we can make everything better.'",
            
            EmotionType.EXCITEMENT: "The adventure continued with even more amazing discoveries! Everyone was laughing and having the most wonderful time together."
        }
        
        story_text = adaptations.get(emotion.primary_emotion, "The story continued in the most delightful way, with everyone feeling happy and safe.")
        
        return StorySegment(
            text=story_text,
            emotional_tone="adaptive",
            pacing="responsive",
            adaptation_reason=f"Fallback adaptation for {emotion.primary_emotion.value}",
            sequence_number=len(context.plot_points) + 1
        )
    
    def _create_safe_adaptation(self, context: StoryContext, emotion: EmotionState) -> str:
        """Create a safe story adaptation when content filtering fails."""
        return f"The characters in our story noticed that someone might need a little extra care and kindness. They gathered together to share warm hugs and gentle words, making sure everyone felt safe and loved."
    
    def _create_safe_conclusion(self, context: StoryContext) -> str:
        """Create a safe story conclusion."""
        return f"And so, all the characters lived happily together, having learned that friendship, kindness, and caring for each other are the most important things of all. They knew that tomorrow would bring new adventures and joy. The end."
    
    def _create_fallback_conclusion(self, context: StoryContext) -> StorySegment:
        """Create a fallback conclusion when generation fails."""
        return StorySegment(
            text=self._create_safe_conclusion(context),
            emotional_tone="warm",
            pacing="gentle",
            adaptation_reason="Fallback conclusion",
            sequence_number=len(context.plot_points) + 1
        )


class ContentFilter:
    """Filters content for age appropriateness and safety."""
    
    def __init__(self):
        # Words and concepts to avoid for different age groups
        self.inappropriate_content = {
            "all_ages": [
                "violence", "scary", "frightening", "dangerous", "hurt", "pain",
                "death", "dying", "kill", "weapon", "fight", "angry", "hate",
                "stupid", "dumb", "ugly", "bad words"
            ],
            "young_children": [
                "complex emotions", "adult themes", "romantic", "dating",
                "money problems", "work stress", "politics", "religion"
            ]
        }
        
        # Positive content indicators
        self.positive_indicators = [
            "friend", "kind", "help", "share", "care", "love", "happy",
            "fun", "play", "learn", "discover", "adventure", "magic",
            "wonder", "joy", "smile", "laugh", "hug", "together"
        ]
    
    def is_appropriate(self, content: str, age: int) -> bool:
        """Check if content is appropriate for the given age."""
        content_lower = content.lower()
        
        # Check for inappropriate content
        inappropriate_words = self.inappropriate_content["all_ages"]
        if age < 8:
            inappropriate_words.extend(self.inappropriate_content["young_children"])
        
        for word in inappropriate_words:
            if word in content_lower:
                logger.warning(f"Inappropriate content detected: {word}")
                return False
        
        # Check for positive content (should have some positive elements)
        positive_count = sum(1 for word in self.positive_indicators if word in content_lower)
        if positive_count == 0 and len(content) > 100:
            logger.warning("Content lacks positive elements")
            return False
        
        # Check length appropriateness
        if len(content) > 1000 and age < 6:
            logger.warning("Content too long for age group")
            return False
        
        return True


class EmotionAdaptationEngine:
    """Handles real-time story adaptation based on emotional feedback."""
    
    def __init__(self):
        self.adaptation_rules = self._initialize_adaptation_rules()
        self.adaptation_history = {}  # Track adaptations per session
        self.cooldown_period = 15  # Minimum seconds between major adaptations
        
    def _initialize_adaptation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotion-to-adaptation mapping rules."""
        return {
            # Boredom Detection Rules
            "boredom_high": {
                "triggers": {
                    "emotion": EmotionType.BOREDOM,
                    "confidence": 0.7,
                    "duration": 10  # seconds
                },
                "adaptations": [
                    "introduce_surprise_character",
                    "add_interactive_element", 
                    "create_mystery",
                    "add_sound_effects",
                    "change_setting_dramatically"
                ],
                "priority": "high"
            },
            
            "boredom_medium": {
                "triggers": {
                    "emotion": EmotionType.BOREDOM,
                    "confidence": 0.5,
                    "duration": 20
                },
                "adaptations": [
                    "introduce_new_character",
                    "add_gentle_excitement",
                    "ask_interactive_question"
                ],
                "priority": "medium"
            },
            
            # Fear/Anxiety Management
            "fear_high": {
                "triggers": {
                    "emotion": EmotionType.FEAR,
                    "confidence": 0.6,
                    "intensity": 0.7
                },
                "adaptations": [
                    "introduce_protective_character",
                    "transform_scary_to_friendly",
                    "add_comforting_dialogue",
                    "shift_to_safe_setting",
                    "use_reassuring_tone"
                ],
                "priority": "urgent"
            },
            
            "anxiety_building": {
                "triggers": {
                    "emotion": EmotionType.ANXIETY,
                    "confidence": 0.5,
                    "trend": "increasing"
                },
                "adaptations": [
                    "slow_down_pace",
                    "add_calming_elements",
                    "introduce_wise_character",
                    "use_soothing_language"
                ],
                "priority": "high"
            },
            
            # Excitement Management
            "excitement_overwhelming": {
                "triggers": {
                    "emotion": EmotionType.EXCITEMENT,
                    "intensity": 0.9,
                    "goal_mismatch": EmotionalGoal.CALM
                },
                "adaptations": [
                    "gradually_slow_pace",
                    "introduce_calming_activity",
                    "shift_to_peaceful_setting",
                    "use_gentle_transitions"
                ],
                "priority": "medium"
            },
            
            "excitement_positive": {
                "triggers": {
                    "emotion": EmotionType.EXCITEMENT,
                    "confidence": 0.7,
                    "goal_match": EmotionalGoal.ENTERTAIN
                },
                "adaptations": [
                    "amplify_adventure",
                    "add_celebration_moments",
                    "increase_character_enthusiasm",
                    "add_dynamic_elements"
                ],
                "priority": "low"  # Maintain good state
            },
            
            # Sadness Support
            "sadness_detected": {
                "triggers": {
                    "emotion": EmotionType.SADNESS,
                    "confidence": 0.6
                },
                "adaptations": [
                    "introduce_empathetic_character",
                    "add_hopeful_elements",
                    "create_supportive_community",
                    "gentle_problem_resolution",
                    "warm_encouraging_dialogue"
                ],
                "priority": "high"
            },
            
            # Joy Enhancement
            "joy_amplification": {
                "triggers": {
                    "emotion": EmotionType.JOY,
                    "confidence": 0.7,
                    "goal_match": EmotionalGoal.ENTERTAIN
                },
                "adaptations": [
                    "celebrate_achievements",
                    "add_fun_activities",
                    "increase_positive_interactions",
                    "create_joyful_moments"
                ],
                "priority": "low"
            }
        }
    
    def analyze_adaptation_need(
        self, 
        session_id: str,
        current_emotion: EmotionState,
        emotion_trend: Dict[str, Any],
        target_goal: EmotionalGoal,
        story_context: StoryContext
    ) -> Optional[Dict[str, Any]]:
        """Analyze if story adaptation is needed and what type."""
        
        # Check cooldown period
        if self._is_in_cooldown(session_id):
            return None
        
        # Evaluate each adaptation rule
        for rule_name, rule in self.adaptation_rules.items():
            if self._evaluate_adaptation_rule(
                rule, current_emotion, emotion_trend, target_goal, story_context
            ):
                adaptation_plan = self._create_adaptation_plan(
                    rule_name, rule, current_emotion, story_context
                )
                
                # Record adaptation
                self._record_adaptation(session_id, adaptation_plan)
                
                return adaptation_plan
        
        return None
    
    def _evaluate_adaptation_rule(
        self,
        rule: Dict[str, Any],
        emotion: EmotionState,
        trend: Dict[str, Any],
        goal: EmotionalGoal,
        context: StoryContext
    ) -> bool:
        """Evaluate if an adaptation rule should trigger."""
        
        triggers = rule["triggers"]
        
        # Check emotion match
        if "emotion" in triggers and emotion.primary_emotion != triggers["emotion"]:
            return False
        
        # Check confidence threshold
        if "confidence" in triggers and emotion.confidence < triggers["confidence"]:
            return False
        
        # Check intensity threshold
        if "intensity" in triggers and emotion.intensity < triggers["intensity"]:
            return False
        
        # Check trend requirements
        if "trend" in triggers:
            required_trend = triggers["trend"]
            actual_trend = trend.get("intensity_trend", "stable")
            if actual_trend != required_trend:
                return False
        
        # Check goal matching/mismatching
        if "goal_match" in triggers and goal != triggers["goal_match"]:
            return False
        
        if "goal_mismatch" in triggers and goal == triggers["goal_mismatch"]:
            return True  # Mismatch detected, adaptation needed
        
        # Check duration (if emotion has been persistent)
        if "duration" in triggers:
            # This would require emotion history analysis
            # For now, assume duration is met if other conditions are satisfied
            pass
        
        return True
    
    def _create_adaptation_plan(
        self,
        rule_name: str,
        rule: Dict[str, Any],
        emotion: EmotionState,
        context: StoryContext
    ) -> Dict[str, Any]:
        """Create a specific adaptation plan based on the triggered rule."""
        
        adaptations = rule["adaptations"]
        priority = rule["priority"]
        
        # Select the most appropriate adaptation technique
        selected_adaptation = self._select_best_adaptation(
            adaptations, emotion, context
        )
        
        return {
            "rule_triggered": rule_name,
            "priority": priority,
            "adaptation_type": selected_adaptation,
            "emotion_context": {
                "emotion": emotion.primary_emotion.value,
                "confidence": emotion.confidence,
                "intensity": emotion.intensity
            },
            "implementation_details": self._get_implementation_details(
                selected_adaptation, emotion, context
            )
        }
    
    def _select_best_adaptation(
        self,
        available_adaptations: List[str],
        emotion: EmotionState,
        context: StoryContext
    ) -> str:
        """Select the most appropriate adaptation from available options."""
        
        # Prioritize adaptations based on context and emotion intensity
        adaptation_scores = {}
        
        for adaptation in available_adaptations:
            score = self._score_adaptation(adaptation, emotion, context)
            adaptation_scores[adaptation] = score
        
        # Return the highest scoring adaptation
        return max(adaptation_scores, key=adaptation_scores.get)
    
    def _score_adaptation(
        self,
        adaptation: str,
        emotion: EmotionState,
        context: StoryContext
    ) -> float:
        """Score an adaptation technique based on appropriateness."""
        
        base_score = 1.0
        
        # Intensity-based scoring
        if emotion.intensity > 0.8:
            # High intensity emotions need stronger interventions
            strong_adaptations = [
                "introduce_surprise_character", "change_setting_dramatically",
                "introduce_protective_character", "transform_scary_to_friendly"
            ]
            if adaptation in strong_adaptations:
                base_score += 0.5
        
        # Age-appropriate scoring
        age = context.target_age
        if age <= 5:
            gentle_adaptations = [
                "add_comforting_dialogue", "introduce_gentle_character",
                "use_soothing_language", "add_calming_elements"
            ]
            if adaptation in gentle_adaptations:
                base_score += 0.3
        
        # Story continuity scoring
        if len(context.characters) >= 3:
            # Too many characters, avoid adding more
            if "introduce" in adaptation and "character" in adaptation:
                base_score -= 0.3
        
        # Recent adaptation history (avoid repetition)
        # This would check recent adaptations to avoid overuse
        
        return base_score
    
    def _get_implementation_details(
        self,
        adaptation_type: str,
        emotion: EmotionState,
        context: StoryContext
    ) -> Dict[str, Any]:
        """Get specific implementation details for an adaptation."""
        
        implementations = {
            "introduce_surprise_character": {
                "action": "add_character",
                "character_type": "surprising_helper",
                "introduction_style": "sudden_appearance",
                "dialogue_tone": "exciting"
            },
            
            "add_interactive_element": {
                "action": "insert_interaction",
                "interaction_type": "question_to_child",
                "examples": [
                    "What do you think [character] should do?",
                    "Can you help [character] solve this puzzle?",
                    "What would you do in this situation?"
                ]
            },
            
            "introduce_protective_character": {
                "action": "add_character",
                "character_type": "wise_protector",
                "introduction_style": "gentle_arrival",
                "dialogue_tone": "reassuring"
            },
            
            "transform_scary_to_friendly": {
                "action": "reframe_element",
                "transformation_type": "scary_to_silly",
                "method": "reveal_friendly_nature"
            },
            
            "gradually_slow_pace": {
                "action": "adjust_pacing",
                "pace_change": "decelerate",
                "method": "longer_descriptions",
                "tone_shift": "calming"
            },
            
            "add_comforting_dialogue": {
                "action": "insert_dialogue",
                "speaker": "supportive_character",
                "tone": "warm_and_reassuring",
                "content_type": "emotional_support"
            }
        }
        
        return implementations.get(adaptation_type, {
            "action": "general_adaptation",
            "method": "contextual_adjustment"
        })
    
    def _is_in_cooldown(self, session_id: str) -> bool:
        """Check if session is in adaptation cooldown period."""
        if session_id not in self.adaptation_history:
            return False
        
        last_adaptation = self.adaptation_history[session_id][-1]
        time_since_last = (datetime.utcnow() - last_adaptation["timestamp"]).total_seconds()
        
        return time_since_last < self.cooldown_period
    
    def _record_adaptation(self, session_id: str, adaptation_plan: Dict[str, Any]) -> None:
        """Record an adaptation for history tracking."""
        if session_id not in self.adaptation_history:
            self.adaptation_history[session_id] = []
        
        adaptation_record = {
            "timestamp": datetime.utcnow(),
            "plan": adaptation_plan
        }
        
        self.adaptation_history[session_id].append(adaptation_record)
        
        # Keep only recent adaptations (last 10)
        if len(self.adaptation_history[session_id]) > 10:
            self.adaptation_history[session_id] = self.adaptation_history[session_id][-10:]
    
    def get_adaptation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get adaptation history for a session."""
        return self.adaptation_history.get(session_id, [])
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up adaptation history for a session."""
        self.adaptation_history.pop(session_id, None)


class StoryCoherenceManager:
    """Ensures story continuity and coherence during adaptations."""
    
    def __init__(self):
        self.coherence_rules = {
            "character_consistency": True,
            "setting_continuity": True,
            "plot_logic": True,
            "tone_transitions": True
        }
    
    def validate_story_coherence(
        self,
        current_context: StoryContext,
        proposed_segment: StorySegment,
        adaptation_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate that a story segment maintains coherence."""
        
        issues = []
        suggestions = []
        
        # Check character consistency
        character_issues = self._check_character_consistency(current_context, proposed_segment)
        if character_issues:
            issues.extend(character_issues)
        
        # Check setting continuity
        setting_issues = self._check_setting_continuity(current_context, proposed_segment)
        if setting_issues:
            issues.extend(setting_issues)
        
        # Check tone transitions
        tone_issues = self._check_tone_transitions(current_context, proposed_segment)
        if tone_issues:
            issues.extend(tone_issues)
        
        # Generate suggestions for improvements
        if issues:
            suggestions = self._generate_coherence_suggestions(issues, adaptation_plan)
        
        return {
            "is_coherent": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "coherence_score": max(0.0, 1.0 - (len(issues) * 0.2))
        }
    
    def _check_character_consistency(
        self,
        context: StoryContext,
        segment: StorySegment
    ) -> List[str]:
        """Check for character consistency issues."""
        issues = []
        
        # Check if characters mentioned in segment exist in context
        existing_characters = {char.name.lower() for char in context.characters}
        mentioned_characters = {name.lower() for name in segment.characters_involved}
        
        for char_name in mentioned_characters:
            if char_name not in existing_characters and char_name != "narrator":
                issues.append(f"New character '{char_name}' introduced without proper setup")
        
        return issues
    
    def _check_setting_continuity(
        self,
        context: StoryContext,
        segment: StorySegment
    ) -> List[str]:
        """Check for setting continuity issues."""
        issues = []
        
        # Simple setting consistency check
        # In production, this would be more sophisticated
        if context.setting and len(context.setting) > 0:
            # Check for abrupt setting changes without transition
            setting_keywords = context.setting.lower().split()
            segment_text = segment.text.lower()
            
            # If no setting keywords appear in new segment, might be a setting change
            if not any(keyword in segment_text for keyword in setting_keywords):
                # Check if there's a transition phrase
                transition_phrases = ["meanwhile", "later", "then", "suddenly", "next"]
                if not any(phrase in segment_text for phrase in transition_phrases):
                    issues.append("Potential abrupt setting change without transition")
        
        return issues
    
    def _check_tone_transitions(
        self,
        context: StoryContext,
        segment: StorySegment
    ) -> List[str]:
        """Check for appropriate tone transitions."""
        issues = []
        
        # Get the last emotional arc entry
        if context.emotional_arc:
            last_emotion = context.emotional_arc[-1]
            
            # Check for jarring tone shifts
            tone_compatibility = {
                "peaceful": ["gentle", "warm", "calm"],
                "exciting": ["energetic", "joyful", "adventurous"],
                "scary": ["reassuring", "gentle", "protective"],
                "sad": ["hopeful", "supportive", "warm"]
            }
            
            # This is a simplified check - in production would be more nuanced
            
        return issues
    
    def _generate_coherence_suggestions(
        self,
        issues: List[str],
        adaptation_plan: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggestions to improve story coherence."""
        suggestions = []
        
        for issue in issues:
            if "character" in issue.lower():
                suggestions.append("Add a brief character introduction or explanation")
            elif "setting" in issue.lower():
                suggestions.append("Include a transition phrase to explain setting change")
            elif "tone" in issue.lower():
                suggestions.append("Add a gradual transition to ease tone changes")
        
        return suggestions
    
    def suggest_coherence_improvements(
        self,
        context: StoryContext,
        segment: StorySegment
    ) -> StorySegment:
        """Suggest improvements to maintain story coherence."""
        
        # Simple coherence improvements
        improved_text = segment.text
        
        # Add character context if new characters appear
        new_characters = []
        for char_name in segment.characters_involved:
            if not any(char.name.lower() == char_name.lower() for char in context.characters):
                new_characters.append(char_name)
        
        if new_characters and not any(word in improved_text.lower() for word in ["meet", "appeared", "came", "arrived"]):
            # Add a gentle introduction
            improved_text = f"Just then, someone new appeared. {improved_text}"
        
        return StorySegment(
            text=improved_text,
            emotional_tone=segment.emotional_tone,
            pacing=segment.pacing,
            characters_involved=segment.characters_involved,
            adaptation_reason=segment.adaptation_reason,
            sequence_number=segment.sequence_number
        )


class StoryContextManager:
    """Manages story state, context, and progression throughout a session."""
    
    def __init__(self):
        self.session_contexts: Dict[str, StoryContext] = {}
        self.max_story_length = 2000  # Maximum words per story
        self.max_segments = 15  # Maximum story segments
        
    def create_story_context(
        self,
        session_id: str,
        child_profile: ChildProfile,
        theme: str,
        initial_segment: StorySegment
    ) -> StoryContext:
        """Create initial story context for a new session."""
        
        # Extract characters from initial segment
        characters = self._extract_characters_from_segment(initial_segment)
        
        # Infer setting from initial segment
        setting = self._extract_setting_from_segment(initial_segment)
        
        context = StoryContext(
            session_id=session_id,
            current_segment=initial_segment.text,
            characters=characters,
            setting=setting,
            plot_points=[f"Story begins: {initial_segment.text[:100]}..."],
            emotional_arc=[],
            theme=theme,
            target_age=child_profile.age,
            target_gender=child_profile.gender  # ✅ CRITICAL: Include gender for story continuity
        )
        
        self.session_contexts[session_id] = context
        return context
    
    def update_story_context(
        self,
        session_id: str,
        new_segment: StorySegment,
        emotion_state: Optional[EmotionState] = None
    ) -> StoryContext:
        """Update story context with new segment and emotion state."""
        
        if session_id not in self.session_contexts:
            raise ValueError(f"No story context found for session {session_id}")
        
        context = self.session_contexts[session_id]
        
        # Update current segment
        context.current_segment = new_segment.text
        
        # Add to plot points
        plot_summary = self._summarize_segment_for_plot(new_segment)
        context.plot_points.append(plot_summary)
        
        # Update characters
        new_characters = self._extract_characters_from_segment(new_segment)
        self._merge_characters(context, new_characters)
        
        # Update setting if changed
        new_setting = self._extract_setting_from_segment(new_segment)
        if new_setting and new_setting != context.setting:
            context.setting = new_setting
        
        # Add emotion state to emotional arc
        if emotion_state:
            context.emotional_arc.append(emotion_state)
            
            # Keep emotional arc manageable (last 20 states)
            if len(context.emotional_arc) > 20:
                context.emotional_arc = context.emotional_arc[-20:]
        
        # Trim plot points if too many
        if len(context.plot_points) > self.max_segments:
            context.plot_points = context.plot_points[-self.max_segments:]
        
        return context
    
    def get_story_context(self, session_id: str) -> Optional[StoryContext]:
        """Get story context for a session."""
        return self.session_contexts.get(session_id)
    
    def get_story_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the story progress."""
        context = self.session_contexts.get(session_id)
        if not context:
            return {}
        
        # Calculate story statistics
        total_words = len(context.current_segment.split())
        total_segments = len(context.plot_points)
        
        # Analyze emotional journey
        emotion_summary = self._analyze_emotional_journey(context.emotional_arc)
        
        # Character development
        character_summary = {
            "main_characters": [char.name for char in context.characters[:3]],
            "total_characters": len(context.characters),
            "character_traits": self._get_character_trait_summary(context.characters)
        }
        
        return {
            "session_id": session_id,
            "theme": context.theme,
            "setting": context.setting,
            "total_words": total_words,
            "total_segments": total_segments,
            "characters": character_summary,
            "emotional_journey": emotion_summary,
            "story_progression": self._assess_story_progression(context),
            "readiness_for_conclusion": self._assess_conclusion_readiness(context)
        }
    
    def should_conclude_story(self, session_id: str) -> bool:
        """Determine if the story should be concluded."""
        context = self.session_contexts.get(session_id)
        if not context:
            return True
        
        # Check story length
        word_count = len(context.current_segment.split())
        if word_count > self.max_story_length:
            return True
        
        # Check number of segments
        if len(context.plot_points) >= self.max_segments:
            return True
        
        # Check emotional arc completion
        if len(context.emotional_arc) > 5:
            recent_emotions = context.emotional_arc[-5:]
            # If emotions have been stable and positive, good time to conclude
            stable_positive = all(
                emotion.primary_emotion in [EmotionType.JOY, EmotionType.CALM, EmotionType.NEUTRAL]
                for emotion in recent_emotions
            )
            if stable_positive and len(context.plot_points) >= 5:
                return True
        
        return False
    
    def get_story_continuation_context(self, session_id: str) -> Dict[str, Any]:
        """Get context needed for story continuation."""
        context = self.session_contexts.get(session_id)
        if not context:
            return {}
        
        # Recent plot development
        recent_plot = context.plot_points[-3:] if len(context.plot_points) >= 3 else context.plot_points
        
        # Current emotional state
        current_emotion = context.emotional_arc[-1] if context.emotional_arc else None
        
        # Character status
        active_characters = [char for char in context.characters if char.name in context.current_segment]
        
        return {
            "recent_plot": recent_plot,
            "current_emotion": current_emotion,
            "active_characters": active_characters,
            "setting": context.setting,
            "theme": context.theme,
            "story_length": len(context.plot_points),
            "word_count": len(context.current_segment.split())
        }
    
    def _extract_characters_from_segment(self, segment: StorySegment) -> List[Character]:
        """Extract character information from a story segment."""
        characters = []
        
        # Use the characters_involved list if available
        if segment.characters_involved:
            for char_name in segment.characters_involved:
                if char_name.lower() != "narrator":
                    character = Character(
                        name=char_name,
                        description=f"Character in the story",
                        personality_traits=self._infer_traits_from_text(char_name, segment.text)
                    )
                    characters.append(character)
        
        return characters
    
    def _extract_setting_from_segment(self, segment: StorySegment) -> str:
        """Extract setting information from a story segment."""
        text = segment.text.lower()
        
        # Common setting indicators
        setting_patterns = {
            "forest": ["forest", "trees", "woods", "woodland"],
            "home": ["house", "home", "bedroom", "kitchen", "living room"],
            "school": ["school", "classroom", "playground", "library"],
            "garden": ["garden", "flowers", "plants", "yard"],
            "magical place": ["magical", "enchanted", "fairy", "castle", "kingdom"],
            "adventure location": ["mountain", "cave", "island", "treasure", "journey"]
        }
        
        for setting_name, keywords in setting_patterns.items():
            if any(keyword in text for keyword in keywords):
                return setting_name
        
        return "story world"  # Default setting
    
    def _summarize_segment_for_plot(self, segment: StorySegment) -> str:
        """Create a brief plot summary for a segment."""
        # Simple summarization - in production, could use more sophisticated NLP
        text = segment.text
        
        # Take first sentence and key elements
        sentences = text.split('.')
        first_sentence = sentences[0] if sentences else text[:100]
        
        # Add adaptation context if available
        summary = first_sentence[:100]
        if segment.adaptation_reason:
            summary += f" (adapted for {segment.adaptation_reason})"
        
        return summary
    
    def _merge_characters(self, context: StoryContext, new_characters: List[Character]) -> None:
        """Merge new characters into existing context."""
        existing_names = {char.name.lower() for char in context.characters}
        
        for new_char in new_characters:
            if new_char.name.lower() not in existing_names:
                context.characters.append(new_char)
            else:
                # Update existing character with new traits
                for existing_char in context.characters:
                    if existing_char.name.lower() == new_char.name.lower():
                        # Merge personality traits
                        existing_traits = set(existing_char.personality_traits)
                        new_traits = set(new_char.personality_traits)
                        existing_char.personality_traits = list(existing_traits.union(new_traits))
                        break
    
    def _infer_traits_from_text(self, character_name: str, text: str) -> List[str]:
        """Infer character traits from story text."""
        traits = []
        text_lower = text.lower()
        name_lower = character_name.lower()
        
        # Simple trait inference
        trait_indicators = {
            "brave": ["brave", "courageous", "fearless", "bold"],
            "kind": ["kind", "gentle", "caring", "helpful", "nice"],
            "wise": ["wise", "smart", "clever", "thoughtful"],
            "playful": ["playful", "fun", "silly", "energetic", "bouncy"],
            "curious": ["curious", "wondering", "exploring", "asking", "interested"]
        }
        
        for trait, indicators in trait_indicators.items():
            for indicator in indicators:
                if indicator in text_lower and name_lower in text_lower:
                    # Check proximity
                    name_pos = text_lower.find(name_lower)
                    indicator_pos = text_lower.find(indicator)
                    if abs(name_pos - indicator_pos) < 100:  # Within 100 characters
                        traits.append(trait)
                        break
        
        return traits[:3]  # Limit to 3 traits
    
    def _analyze_emotional_journey(self, emotional_arc: List[EmotionState]) -> Dict[str, Any]:
        """Analyze the emotional journey throughout the story."""
        if not emotional_arc:
            return {"status": "no_emotions_recorded"}
        
        # Count emotion types
        emotion_counts = {}
        total_confidence = 0
        total_intensity = 0
        
        for emotion in emotional_arc:
            emotion_type = emotion.primary_emotion.value
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            total_confidence += emotion.confidence
            total_intensity += emotion.intensity
        
        # Find dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Analyze trend
        if len(emotional_arc) >= 3:
            recent_emotions = [e.primary_emotion.value for e in emotional_arc[-3:]]
            trend = "stable" if len(set(recent_emotions)) <= 1 else "changing"
        else:
            trend = "developing"
        
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotion_counts,
            "average_confidence": total_confidence / len(emotional_arc),
            "average_intensity": total_intensity / len(emotional_arc),
            "trend": trend,
            "total_states": len(emotional_arc)
        }
    
    def _get_character_trait_summary(self, characters: List[Character]) -> Dict[str, int]:
        """Get summary of character traits across all characters."""
        trait_counts = {}
        
        for character in characters:
            for trait in character.personality_traits:
                trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        return trait_counts
    
    def _assess_story_progression(self, context: StoryContext) -> str:
        """Assess the current progression stage of the story."""
        segment_count = len(context.plot_points)
        
        if segment_count <= 2:
            return "beginning"
        elif segment_count <= 8:
            return "development"
        elif segment_count <= 12:
            return "climax_approach"
        else:
            return "resolution_ready"
    
    def _assess_conclusion_readiness(self, context: StoryContext) -> Dict[str, Any]:
        """Assess if the story is ready for conclusion."""
        
        # Check various readiness factors
        factors = {
            "length_appropriate": len(context.plot_points) >= 5,
            "characters_developed": len(context.characters) > 0,
            "emotional_stability": False,
            "plot_development": len(context.plot_points) >= 3
        }
        
        # Check emotional stability
        if len(context.emotional_arc) >= 3:
            recent_emotions = context.emotional_arc[-3:]
            positive_emotions = [EmotionType.JOY, EmotionType.CALM, EmotionType.NEUTRAL]
            factors["emotional_stability"] = all(
                emotion.primary_emotion in positive_emotions 
                for emotion in recent_emotions
            )
        
        readiness_score = sum(factors.values()) / len(factors)
        
        return {
            "ready": readiness_score >= 0.75,
            "readiness_score": readiness_score,
            "factors": factors,
            "recommendation": "ready_for_conclusion" if readiness_score >= 0.75 else "continue_development"
        }
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up story context for a session."""
        self.session_contexts.pop(session_id, None)
    
    def get_user_preference_insights(self, session_id: str) -> Dict[str, Any]:
        """Extract insights about user preferences from story interaction."""
        context = self.session_contexts.get(session_id)
        if not context:
            return {}
        
        insights = {
            "preferred_themes": [context.theme],
            "character_preferences": [],
            "emotional_responses": {},
            "engagement_patterns": {}
        }
        
        # Analyze character preferences
        if context.characters:
            character_traits = {}
            for char in context.characters:
                for trait in char.personality_traits:
                    character_traits[trait] = character_traits.get(trait, 0) + 1
            
            insights["character_preferences"] = list(character_traits.keys())
        
        # Analyze emotional responses
        if context.emotional_arc:
            emotion_timeline = []
            for i, emotion in enumerate(context.emotional_arc):
                emotion_timeline.append({
                    "sequence": i,
                    "emotion": emotion.primary_emotion.value,
                    "confidence": emotion.confidence,
                    "intensity": emotion.intensity
                })
            
            insights["emotional_responses"] = {
                "timeline": emotion_timeline,
                "most_engaged": max(context.emotional_arc, key=lambda x: x.intensity).primary_emotion.value,
                "average_engagement": sum(e.intensity for e in context.emotional_arc) / len(context.emotional_arc)
            }
        
        return insights