# Fix: Story Language Issue

## Problem
Stories were being generated in Spanish even when English was selected.

## Root Cause
The English prompt in `backend/prompts/story_prompts.py` did NOT explicitly instruct the AI to write in English. The AI was inferring the language from context, which sometimes defaulted to Spanish.

## Current Implementation Status

### ✅ Frontend (Correct)
1. **LanguageContext** - Properly manages language state
2. **ChildFriendlyStoryArea** - Uses `useLanguage()` hook correctly (line 50)
3. **StorytellingService** - Sends language in request (line 120)
   ```javascript
   language: String(storyData.language || 'es')
   ```

### ✅ Backend (Correct)
1. **app.py** - Receives language parameter (line 381)
   ```python
   language = data.get("language", "es")
   ```
2. **story_prompts.py** - Has separate English and Spanish prompts
   - `get_story_prompt(language, **kwargs)` routes to correct language
   - `get_english_prompt()` for English
   - `get_spanish_prompt()` for Spanish

## Debug Steps Added

Added logging in `backend/app.py` line 382:
```python
logger.info(f"🌍 Language received from frontend: {language}")
```

## Next Steps to Verify

1. **Check browser console** - Verify language is being sent:
   - Open DevTools → Network tab
   - Filter for `/story` requests
   - Check request payload for `language` field

2. **Check backend logs** - Look for:
   ```
   🌍 Language received from frontend: en
   ```

3. **Verify prompt selection** - The backend should call:
   - `get_english_prompt()` when language='en'
   - `get_spanish_prompt()` when language='es'

## Solution Applied

### Modified `backend/prompts/story_prompts.py`

**English Prompt** - Added explicit language instruction:
```python
⚠️ CRITICAL: Write the ENTIRE story in ENGLISH. Every word must be in English.
```

**Spanish Prompt** - Added explicit language instruction:
```python
⚠️ CRÍTICO: Escribe TODA la historia en ESPAÑOL. Cada palabra debe estar en español.
```

This ensures AWS Bedrock clearly understands which language to use, regardless of other context.

## Testing Instructions

1. **Restart the backend server** to load the new prompts
2. **Clear browser cache** or hard refresh (Ctrl+Shift+R)
3. **Select English language** in the app
4. **Start a new story**
5. **Verify** the story is generated in English
6. **Continue the story** and verify subsequent chapters are also in English

## Files Modified

1. `backend/prompts/story_prompts.py` - Added explicit language instructions to both English and Spanish prompts
2. `backend/app.py` - Added language logging for debugging
3. `STORY_LANGUAGE_DEBUG.md` - This documentation

## Expected Behavior

- When `language='en'` → Story generated in English
- When `language='es'` → Story generated in Spanish
- Language persists across all story chapters
- No language mixing within a story
