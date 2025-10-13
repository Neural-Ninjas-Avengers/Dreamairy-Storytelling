# 🌍 Internationalization Guide

## Overview
The Kiro storytelling app now supports multiple languages with a beautiful flag-based language selector. Currently supports English and Spanish with easy extensibility for additional languages.

## Features Implemented

### 🎯 Language Selector
- **Location**: Top-right corner of welcome screen
- **Design**: Elegant dropdown with country flags
- **Flags**: 🇺🇸 English, 🇪🇸 Spanish
- **Animations**: Smooth transitions with Framer Motion
- **Persistence**: Language preference saved to localStorage

### 🔄 Translation System
- **Context-based**: Uses React Context for global state
- **Hook-based**: `useLanguage()` hook for easy access
- **Automatic detection**: Detects browser language on first visit
- **Fallback**: Defaults to English if language not supported

### 📱 Responsive Design
- **Mobile**: Shows flag only on small screens
- **Desktop**: Shows flag + language name
- **Backdrop**: Click outside to close dropdown
- **Accessibility**: Keyboard navigation support

## Supported Languages

### English (en) 🇺🇸
- **Code**: `en`
- **Flag**: 🇺🇸
- **Name**: English
- **Status**: ✅ Complete

### Spanish (es) 🇪🇸
- **Code**: `es`
- **Flag**: 🇪🇸
- **Name**: Español
- **Status**: ✅ Complete

## Translation Coverage

### ✅ Welcome Screen
- App title and subtitle
- Photo capture instructions
- Age selection prompt
- Theme selection prompt
- Start button text
- All emotion labels
- All theme labels

### ✅ Story Area
- Story title
- Loading states
- Button labels
- Navigation text

### ✅ Photo Capture
- Button texts
- Status messages
- Optional instructions

## Technical Implementation

### File Structure
```
src/
├── contexts/
│   └── LanguageContext.js     # Translation context & data
├── components/
│   ├── LanguageSelector.js    # Flag dropdown component
│   ├── ModernWelcomeScreen.js # Updated with translations
│   ├── ModernStoryArea.js     # Updated with translations
│   └── PhotoCapture.js        # Updated with translations
└── App.js                     # Wrapped with LanguageProvider
```

### Usage Example
```javascript
import { useLanguage } from '../contexts/LanguageContext';

const MyComponent = () => {
  const { t, language, changeLanguage } = useLanguage();
  
  return (
    <div>
      <h1>{t('appTitle')}</h1>
      <p>{t('themes.animals')}</p>
      <button onClick={() => changeLanguage('es')}>
        Switch to Spanish
      </button>
    </div>
  );
};
```

### Translation Keys Structure
```javascript
{
  // Welcome Screen
  appTitle: 'Kiro',
  appSubtitle: 'Stories that adapt to your emotions',
  
  // Nested objects for organization
  emotions: {
    entertain: 'Fun',
    calm: 'Calm',
    stimulate_play: 'Energy'
  },
  
  themes: {
    animals: 'Animals',
    adventure: 'Adventures',
    fantasy: 'Fantasy',
    friendship: 'Friendship'
  }
}
```

## Adding New Languages

### Step 1: Add Translation Data
```javascript
// In LanguageContext.js
const translations = {
  en: { /* existing */ },
  es: { /* existing */ },
  fr: {  // New French translations
    appTitle: 'Kiro',
    appSubtitle: 'Histoires qui s\'adaptent à vos émotions',
    // ... add all translation keys
  }
};
```

### Step 2: Add Language Option
```javascript
// In LanguageSelector.js
const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' }  // New
];
```

### Step 3: Test Implementation
1. Switch to new language
2. Verify all text updates
3. Check localStorage persistence
4. Test browser detection

## Browser Language Detection

The app automatically detects the user's browser language:

```javascript
// Detects browser language
const browserLang = navigator.language.split('-')[0];
// Falls back to English if not supported
return translations[browserLang] ? browserLang : 'en';
```

## Persistence

Language preferences are automatically saved:

```javascript
// Saves to localStorage on change
localStorage.setItem('kiro-language', language);

// Loads on app start
const savedLanguage = localStorage.getItem('kiro-language');
```

## Styling & Animation

### Language Selector Styles
- **Background**: Semi-transparent white with backdrop blur
- **Hover Effects**: Scale and opacity transitions
- **Active State**: Gradient background for selected language
- **Animations**: Smooth dropdown with scale and fade effects

### Flag Display
- **Size**: Large enough to be easily recognizable
- **Spacing**: Proper gap between flag and text
- **Responsive**: Adapts to screen size

## Best Practices

### Translation Keys
- Use descriptive, hierarchical keys
- Group related translations
- Keep keys consistent across languages
- Use camelCase for key names

### Component Integration
- Import `useLanguage` hook
- Use `t()` function for all user-facing text
- Avoid hardcoded strings
- Test with both languages

### Performance
- Translations loaded once at app start
- No network requests for language switching
- Minimal re-renders with React Context
- Efficient localStorage usage

## Future Enhancements

### Potential Languages
- 🇫🇷 French (Français)
- 🇩🇪 German (Deutsch)
- 🇮🇹 Italian (Italiano)
- 🇵🇹 Portuguese (Português)
- 🇯🇵 Japanese (日本語)

### Advanced Features
- **RTL Support**: For Arabic, Hebrew
- **Pluralization**: Smart plural forms
- **Date/Time Formatting**: Locale-specific formats
- **Number Formatting**: Currency, decimals
- **Voice Narration**: Multi-language TTS

## Testing Checklist

### ✅ Language Switching
- [ ] Dropdown opens/closes correctly
- [ ] Language changes immediately
- [ ] All text updates properly
- [ ] Preference persists on reload

### ✅ Browser Detection
- [ ] Detects Spanish browser → Spanish app
- [ ] Detects English browser → English app
- [ ] Unsupported language → English fallback

### ✅ Responsive Design
- [ ] Mobile: Flag only visible
- [ ] Desktop: Flag + name visible
- [ ] Dropdown positions correctly
- [ ] Touch interactions work

### ✅ Translation Coverage
- [ ] Welcome screen fully translated
- [ ] Story area fully translated
- [ ] Photo capture fully translated
- [ ] No hardcoded strings remain

## Troubleshooting

### Common Issues

**Language not changing**
- Check if translation key exists
- Verify `useLanguage` hook is used
- Ensure component is wrapped in `LanguageProvider`

**Dropdown not appearing**
- Check z-index values
- Verify AnimatePresence is working
- Test click handlers

**Translations missing**
- Add missing keys to translation object
- Use fallback text for development
- Check console for missing key warnings

---

🎉 **The app now provides a seamless multilingual experience with beautiful flag-based language selection!**