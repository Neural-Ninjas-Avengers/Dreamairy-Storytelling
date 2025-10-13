import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

const translations = {
  en: {
    // Welcome Screen
    appTitle: 'DreamAIry',
    appSubtitle: 'Stories that adapt to your emotions',
    yourMagicalStory: 'Your Magical Story!',
    starringYou: 'Starring you',
    takePhoto: '📸 Take a photo to be the protagonist!',
    howOldAreYou: 'How old are you?',
    whatStoryType: 'What type of story do you prefer?',
    startMagicalStory: '✨ Start my magical story',
    
    // Emotions
    emotions: {
      entertain: 'Fun',
      calm: 'Calm',
      stimulate_play: 'Energy'
    },
    
    // Themes
    themes: {
      animals: 'Animals',
      adventure: 'Adventures',
      fantasy: 'Fantasy',
      friendship: 'Friendship'
    },
    
    // Story Area
    yourStory: 'Your Magical Story',
    generating: 'Generating your story...',
    newChapter: 'Continue Story',
    backToWelcome: 'End Session',
    storyWillBeginHere: 'Your story will begin here...',
    clickToStart: 'Click "Start Magical Story" to begin your adventure',
    
    // Photo Capture
    takePhotoButton: 'Take Photo',
    retakePhoto: 'Change Photo',
    usePhoto: 'Photo ready for AI!',
    cameraNotAvailable: 'Camera not available',
    optionalPhotoText: 'Optional: You will appear as a character in the illustrations',
    
    // Language Selector
    selectLanguage: 'Select Language',
    
    // Common
    loading: 'Loading...',
    error: 'Error',
    retry: 'Retry',
    
    // Auto Image Generation
    autoImageGenerated: '🎨 Image generated automatically',
    generatedAutomatically: '🤖 Generated automatically',
    generatedImages: 'Generated Images',
    segment: 'Segment',
    auto: 'Auto',
    localImageGenerated: '🎨 Illustration generated locally'
  },
  es: {
    // Welcome Screen
    appTitle: 'DreamAIry',
    appSubtitle: 'Cuentos que se adaptan a tus emociones',
    yourMagicalStory: '¡Tu Historia Mágica!',
    starringYou: 'Protagonizada por ti',
    takePhoto: '📸 ¡Toma una foto para ser el protagonista!',
    howOldAreYou: '¿Cuántos años tienes?',
    whatStoryType: '¿Qué tipo de historia prefieres?',
    startMagicalStory: '✨ Comenzar mi historia mágica',
    
    // Emotions
    emotions: {
      entertain: 'Diversión',
      calm: 'Calma',
      stimulate_play: 'Energía'
    },
    
    // Themes
    themes: {
      animals: 'Animales',
      adventure: 'Aventuras',
      fantasy: 'Fantasía',
      friendship: 'Amistad'
    },
    
    // Story Area
    yourStory: 'Tu Historia Mágica',
    generating: 'Generando tu historia...',
    newChapter: 'Continuar Historia',
    backToWelcome: 'Terminar Sesión',
    storyWillBeginHere: 'Tu historia comenzará aquí...',
    clickToStart: 'Haz clic en "Comenzar Historia Mágica" para empezar tu aventura',
    
    // Photo Capture
    takePhotoButton: 'Tomar Foto',
    retakePhoto: 'Cambiar Foto',
    usePhoto: '¡Foto lista para IA!',
    cameraNotAvailable: 'Cámara no disponible',
    optionalPhotoText: 'Opcional: Aparecerás como personaje en las ilustraciones',
    
    // Language Selector
    selectLanguage: 'Seleccionar Idioma',
    
    // Common
    loading: 'Cargando...',
    error: 'Error',
    retry: 'Reintentar',
    
    // Auto Image Generation
    autoImageGenerated: '🎨 Imagen generada automáticamente',
    generatedAutomatically: '🤖 Generada automáticamente',
    generatedImages: 'Ilustraciones Generadas',
    segment: 'Segmento',
    auto: 'Auto',
    localImageGenerated: '🎨 Ilustración generada localmente'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Try to get language from localStorage first
    const savedLanguage = localStorage.getItem('dreamairy-language');
    if (savedLanguage && translations[savedLanguage]) {
      return savedLanguage;
    }
    
    // Detect browser language
    const browserLang = navigator.language.split('-')[0];
    return translations[browserLang] ? browserLang : 'en';
  });

  useEffect(() => {
    // Save language preference to localStorage
    localStorage.setItem('dreamairy-language', language);
  }, [language]);

  const t = (key) => {
    const keys = key.split('.');
    let value = translations[language];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };

  const changeLanguage = (newLanguage) => {
    if (translations[newLanguage]) {
      setLanguage(newLanguage);
    }
  };

  const value = {
    language,
    changeLanguage,
    t,
    availableLanguages: Object.keys(translations)
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};