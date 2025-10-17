# Remaining Translations TODO

## Issue
When selecting English, some text still appears in Spanish in the Welcome Screen.

## Hardcoded Spanish Text to Replace

### In `frontend/src/components/ChildFriendlyWelcomeScreen.js`

Replace these hardcoded strings with translation calls:

1. **Line ~224**: `← Atrás` → `{t('back')}`
2. **Line ~284**: `← Atrás` → `{t('back')}`
3. **Line ~295**: `Continuar →` → `{t('continue')}`
4. **Line ~322**: `✓ ¡Correcto!` → `{t('correct')}`
5. **Line ~353**: `← Atrás` → `{t('back')}`
6. **Line ~364**: `Continuar →` → `{t('continue')}`
7. **Line ~379**: `🎭 ¿Qué historia quieres vivir?` → `{t('whatStoryToLive')}`
8. **Line ~428**: `← Atrás` → `{t('back')}`
9. **Line ~439**: `✨ ¡Crear Historia!` → `{t('createStory')}`

## Quick Fix Command

Run this in PowerShell from project root:

```powershell
$file = "frontend/src/components/ChildFriendlyWelcomeScreen.js"
$content = Get-Content $file -Raw
$content = $content -replace '← Atrás', "{t('back')}"
$content = $content -replace 'Continuar →', "{t('continue')}"
$content = $content -replace '✓ ¡Correcto!', "{t('correct')}"
$content = $content -replace '✨ ¡Crear Historia!', "{t('createStory')}"
$content = $content -replace '🎭 ¿Qué historia quieres vivir\?', "{t('whatStoryToLive')}"
$content | Set-Content $file
```

## Translations Already Added

These translations are already in `LanguageContext.js`:

```javascript
// English
back: '← Back',
next: 'Next →',
continue: 'Continue',
correct: '✓ Correct!',
createStory: '✨ Create Story!',
whatStoryToLive: '🎭 What story do you want to live?',

// Spanish
back: '← Atrás',
next: 'Siguiente →',
continue: 'Continuar',
correct: '✓ ¡Correcto!',
createStory: '✨ ¡Crear Historia!',
whatStoryToLive: '🎭 ¿Qué historia quieres vivir?',
```

## After Fix

1. Restart frontend: `npm start`
2. Clear browser cache
3. Test:
   - Select English → All text in English
   - Select Spanish → All text in Spanish
