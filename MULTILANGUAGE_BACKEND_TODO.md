# Multilanguage Backend Implementation - TODO

## Critical: Story Generation in Selected Language

### Current Status
- ✅ Frontend has language selector
- ✅ Frontend translations working
- ❌ Backend generates stories always in English
- ❌ Language not passed from frontend to backend

### Required Changes

#### 1. Frontend - Pass Language to Backend
**File**: `frontend/src/components/ChildFriendlyStoryArea.js`

Add language to story generation request:
```javascript
const { language } = useLanguage(); // Already imported

const requestData = {
  theme: selectedTheme,
  segments_so_far: storySegments.length,
  child_age: selectedAge,
  child_gender: selectedGender || 'niño',
  emotional_goal: 'entertain',
  language: language, // ✅ ADD THIS
  story_context: storyContext,
  last_segment: lastSegment,
  is_finale: isFinale
};
```

#### 2. Backend - Update Story Prompt with Language
**File**: `backend/core/story_generator.py`

Modify `create_initial_story_prompt` to use language:
```python
def create_initial_story_prompt(self, profile: ChildProfile, theme: str, language: str = 'en') -> str:
    """Create initial story generation prompt."""
    
    # Language-specific instructions
    language_instruction = {
        'en': "Write the story in English.",
        'es': "Escribe la historia en español."
    }.get(language, "Write the story in English.")
    
    prompt = f"""Create a children's story beginning for a {profile.age}-year-old child.

LANGUAGE: {language_instruction}

CHARACTER NAME: ...
CHARACTER GENDER: ...
...
```

#### 3. Backend - Pass Language Through Context
**File**: `backend/models/core.py`

Add language to StoryContext:
```python
class StoryContext(BaseModel):
    # ... existing fields ...
    target_language: Optional[str] = Field(default='en', description="Target language for story")
```

#### 4. Backend - Update Endpoint
**File**: `backend/api/demo_endpoints.py`

Extract language from request:
```python
story_context = StoryContext(
    session_id=session_uuid,
    theme=context_data.get("theme", ...),
    target_age=session.child_profile.age,
    target_gender=session.child_profile.gender,
    target_language=context_data.get("language", "en"),  # ✅ ADD THIS
    ...
)
```

### Implementation Priority

1. **HIGH**: Add language to frontend story request
2. **HIGH**: Add language to StoryContext model
3. **HIGH**: Update story prompts to use language
4. **MEDIUM**: Add language to image generation prompts
5. **LOW**: Translate all remaining UI text

### Testing

After implementation:
1. Select English → Story should be in English
2. Select Spanish → Story should be in Spanish
3. Switch language mid-story → New chapters in new language
4. Image descriptions should match story language

### Estimated Time
- Frontend changes: 10 minutes
- Backend model: 5 minutes
- Backend prompts: 15 minutes
- Testing: 10 minutes
**Total: ~40 minutes**
