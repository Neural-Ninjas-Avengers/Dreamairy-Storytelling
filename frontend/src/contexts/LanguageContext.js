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
    
    // Emotion Descriptions
    emotionDescriptions: {
      entertain: 'Stories full of adventure and laughter',
      calm: 'Relaxing and peaceful tales',
      stimulate_play: 'Exciting and dynamic adventures'
    },
    
    // Detected Emotions (from face recognition)
    detectedEmotions: {
      happy: 'Happy',
      sad: 'Sad',
      angry: 'Angry',
      surprised: 'Surprised',
      neutral: 'Neutral',
      excited: 'Excited',
      scared: 'Scared',
      calm: 'Calm',
      confused: 'Confused',
      disgusted: 'Disgusted',
      fear: 'Fear'
    },
    
    // Themes
    themes: {
      animals: 'Animals',
      space: 'Space',
      pirates: 'Pirates',
      dinosaurs: 'Dinosaurs',
      magic: 'Magic',
      dragons: 'Dragons',
      superheroes: 'Superheroes',
      ocean: 'Ocean',
      adventure: 'Adventures',
      fantasy: 'Fantasy',
      friendship: 'Friendship'
    },
    
    // Theme subtitles
    themeSubtitles: {
      animals: 'Adventures with furry friends',
      space: 'Journeys among the stars',
      pirates: 'Treasures and sea adventures',
      dinosaurs: 'Journey to the prehistoric world',
      magic: 'Spells and enchantments',
      dragons: 'Legendary creatures',
      superheroes: 'Save the world',
      ocean: 'Underwater mysteries'
    },
    
    // Ages
    years: 'years old',
    
    // Gender
    boy: 'Boy',
    girl: 'Girl',
    selectGender: 'Are you a boy or a girl?',
    
    // Name
    whatsYourName: "What's your name?",
    enterName: 'Enter your name (optional)',
    
    // Steps
    howOldQuestion: '🎂 How old are you?',
    iThinkYouAre: '✨ I think you are:',
    confirmAge: 'Yes, that\'s my age!',
    selectDifferentAge: 'No, I\'m a different age',
    chooseTheme: '🎨 Choose your adventure!',
    startAdventure: '🚀 Start Adventure',
    
    // Gender options
    imABoy: 'I\'m a boy',
    imAGirl: 'I\'m a girl',
    tellUsAboutYou: '👋 Tell us about you!',
    
    // Name step
    whatsYourNameQuestion: '✨ What\'s your name?',
    personalizeStory: 'So we can personalize your story',
    enterNameHere: 'Enter your name here',
    skipOptional: 'Skip (optional)',
    
    // Navigation
    back: '← Back',
    next: 'Next →',
    continue: 'Continue',
    
    // Photo
    optionalPhoto: 'Optional: Take a photo to appear in the story',
    takeYourPhoto: '📸 Take your photo!',
    appearInStory: 'You will appear as a character in the illustrations',
    youWillBeProtagonist: 'You will be the protagonist of your story',
    createPersonalizedAvatar: 'Create Personalized Avatar',
    tapToCapture: 'Tap to capture your magical photo',
    advancedAI: 'Advanced AI',
    uniqueStyle: 'Unique Style',
    capture: 'Capture',
    processing: '⏳ Processing...',
    useThisPhoto: 'Use this photo',
    retake: 'Retake',
    close: 'Close',
    
    // Buttons
    correct: '✓ Correct!',
    createStory: '✨ Create Story!',
    
    // Questions
    whatStoryToLive: '🎭 What story do you want to live?',
    
    // Story generation
    generatingStory: 'Creating your magical story...',
    pleaseWait: 'Please wait',
    
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
    
    // Admin Access
    adminPanel: 'Admin Panel',
    configureCredentials: 'Configure AWS Credentials',
    
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
    localImageGenerated: '🎨 Illustration generated locally',
    
    // Photo Capture Additional
    storyStyle: 'Story Style',
    private: 'Private',
    changePhoto: 'Change Photo',
    captureYourPhoto: '📸 Capture your Photo!',
    
    // AI Image Generator
    noStoryContext: 'No story context to generate image',
    errorGeneratingImage: 'Error generating image. Try again.',
    photoReadyForAI: 'Photo ready for AI!',
    appearAsMainCharacter: 'You will appear as the main character in the illustration',
    noPersonalizedPhoto: 'No personalized photo',
    genericCharacterUsed: 'A generic character will be used in the illustration',
    generatingAIIllustration: 'Generating AI Illustration...',
    creatingMagicalImage: 'Creating a magical image based on your story',
    
    // Story Area Additional
    begin: 'Begin',
    continueStory: 'Continue',
    continueStoryFull: 'Continue Story',
    creating: 'Creating...',
    
    // Common Additional
    image: 'Image',
    photo: 'Photo',
    yourPhoto: 'Your Photo',
    
    // Placeholders
    foxImage: 'Fox Image',
    generateWithAI: 'Generate with AI',
    avatarReadyForStories: '✨ Avatar ready for your stories',
    photoReadyForIllustrations: '🎨 Photo ready for illustrations',
    avatarReady: 'Avatar Ready',
    youWillAppearInIllustrations: 'You will appear in all illustrations',
    youWillAppearInIllustrationsWithAge: 'You will appear in illustrations',
    willBeUsedForIllustrations: 'Will be used for illustrations',
    years: 'years',
    
    // Additional Story Area
    yourMagicalStory: 'Your Magical Story',
    magicalIllustration: 'Magical Illustration',
    illustratedStory: 'Illustrated Story',
    storyIllustration: 'Story illustration',
    of: 'of',
    by: 'by',
    illustrationStyle: 'Illustration Style:',
    illustrationWithYourFace: 'An illustration with your face as the protagonist',
    generateAIIllustration: 'Generate AI Illustration',
    aiGeneratedIllustration: 'AI-generated illustration!',
    youAppearAsMainCharacter: 'You appear as the main character.',
    wantToChangeSomething: 'Want to change something in the story?',
    whatDoYouWantToHappen: '💭 What do you want to happen in the story?',
    storyCompleted: 'Story Completed!',
    adventureHasEnded: 'The adventure has come to an end',
    newStoryButton: 'New Story',
    magicalStoryOfThemeBy: 'Magical story of',
    beautifulIllustrationWillAppear: 'A beautiful illustration will appear here',
    beautifulIllustrationAccompanies: 'A beautiful illustration accompanies this part of the story',
    continuingTheStory: 'Continuing the story...',
    magicalStoryOf: 'Magical story of',
    creatingYourMagicalStory: 'Creating your magical story...',
    yourMagicalStoryWillBeginHere: 'Your magical story will begin here...',
    clickToStartAdventure: '✨ Click "Start Story" to begin your magical adventure! 🚀',
    chapter: 'Chapter',
    readyToBegin: 'Ready to begin',
    creatingYourStory: 'Creating your story...',
    startStory: 'Start Story',
    beginAdventure: 'Begin Adventure!',
    creatingAvatar: '🎭 Creating avatar...',
    photoCaptured: 'Photo captured!',
    avatarCreated: '✨ Avatar created!',
    photoReady: '📸 Photo ready!',
    newStory: 'New Story',
    endStory: 'End Story',
    howDoYouFeel: 'How do you feel?',
    analyzingPhoto: 'Analyzing photo...',
    generatingAvatar: 'Generating avatar...'
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
    
    // Emotion Descriptions
    emotionDescriptions: {
      entertain: 'Historias llenas de aventura y risas',
      calm: 'Cuentos relajantes y tranquilos',
      stimulate_play: 'Aventuras emocionantes y dinámicas'
    },
    
    // Detected Emotions (from face recognition)
    detectedEmotions: {
      happy: 'Feliz',
      sad: 'Triste',
      angry: 'Enfadado',
      surprised: 'Sorprendido',
      neutral: 'Neutral',
      excited: 'Emocionado',
      scared: 'Asustado',
      calm: 'Tranquilo',
      confused: 'Confundido',
      disgusted: 'Disgustado',
      fear: 'Miedo'
    },
    
    // Themes
    themes: {
      animals: 'Animales',
      space: 'Espacio',
      pirates: 'Piratas',
      dinosaurs: 'Dinosaurios',
      magic: 'Magia',
      dragons: 'Dragones',
      superheroes: 'Superhéroes',
      ocean: 'Océano',
      adventure: 'Aventuras',
      fantasy: 'Fantasía',
      friendship: 'Amistad'
    },
    
    // Theme subtitles
    themeSubtitles: {
      animals: 'Aventuras con amigos peludos',
      space: 'Viajes entre las estrellas',
      pirates: 'Tesoros y aventuras en el mar',
      dinosaurs: 'Viaje al mundo prehistórico',
      magic: 'Hechizos y encantamientos',
      dragons: 'Criaturas legendarias',
      superheroes: 'Salva el mundo',
      ocean: 'Misterios submarinos'
    },
    
    // Ages
    years: 'años',
    
    // Gender
    boy: 'Niño',
    girl: 'Niña',
    selectGender: '¿Eres niño o niña?',
    
    // Name
    whatsYourName: '¿Cómo te llamas?',
    enterName: 'Escribe tu nombre (opcional)',
    
    // Steps
    howOldQuestion: '🎂 ¿Cuántos años tienes?',
    iThinkYouAre: '✨ Creo que tienes:',
    confirmAge: '¡Sí, esa es mi edad!',
    selectDifferentAge: 'No, tengo otra edad',
    chooseTheme: '🎨 ¡Elige tu aventura!',
    startAdventure: '🚀 Comenzar Aventura',
    
    // Gender options
    imABoy: 'Soy un niño',
    imAGirl: 'Soy una niña',
    tellUsAboutYou: '👋 ¡Cuéntanos sobre ti!',
    
    // Name step
    whatsYourNameQuestion: '✨ ¿Cómo te llamas?',
    personalizeStory: 'Así podremos personalizar tu historia',
    enterNameHere: 'Escribe tu nombre aquí',
    skipOptional: 'Saltar (opcional)',
    
    // Navigation
    back: '← Atrás',
    next: 'Siguiente →',
    continue: 'Continuar',
    
    // Photo
    optionalPhoto: 'Opcional: Toma una foto para aparecer en la historia',
    takeYourPhoto: '📸 ¡Tómate una foto!',
    appearInStory: 'Aparecerás como personaje en las ilustraciones',
    youWillBeProtagonist: 'Serás el protagonista de tu historia',
    createPersonalizedAvatar: 'Crear Avatar Personalizado',
    tapToCapture: 'Toca para capturar tu foto mágica',
    advancedAI: 'IA Avanzada',
    uniqueStyle: 'Estilo Único',
    capture: 'Capturar',
    processing: '⏳ Procesando...',
    useThisPhoto: 'Usar esta foto',
    retake: 'Reintentar',
    close: 'Cerrar',
    
    // Buttons
    correct: '✓ ¡Correcto!',
    createStory: '✨ ¡Crear Historia!',
    
    // Questions
    whatStoryToLive: '🎭 ¿Qué historia quieres vivir?',
    
    // Story generation
    generatingStory: 'Creando tu historia mágica...',
    pleaseWait: 'Por favor espera',
    
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
    
    // Admin Access
    adminPanel: 'Panel de Administración',
    configureCredentials: 'Configurar Credenciales AWS',
    
    // Common
    loading: 'Cargando...',
    pleaseWait: 'Por favor espera un momento',
    error: 'Error',
    retry: 'Reintentar',
    
    // Auto Image Generation
    autoImageGenerated: '🎨 Imagen generada automáticamente',
    generatedAutomatically: '🤖 Generada automáticamente',
    generatedImages: 'Ilustraciones Generadas',
    segment: 'Segmento',
    auto: 'Auto',
    localImageGenerated: '🎨 Ilustración generada localmente',
    
    // Photo Capture Additional
    storyStyle: 'Estilo Cuento',
    private: 'Privado',
    changePhoto: 'Cambiar foto',
    captureYourPhoto: '📸 ¡Captura tu Foto!',
    
    // AI Image Generator
    noStoryContext: 'No hay contexto de historia para generar la imagen',
    errorGeneratingImage: 'Error al generar la imagen. Inténtalo de nuevo.',
    photoReadyForAI: '¡Foto lista para AI!',
    appearAsMainCharacter: 'Aparecerás como personaje principal en la ilustración',
    noPersonalizedPhoto: 'Sin foto personalizada',
    genericCharacterUsed: 'Se usará un personaje genérico en la ilustración',
    generatingAIIllustration: 'Generando Ilustración AI...',
    creatingMagicalImage: 'Creando una imagen mágica basada en tu historia',
    
    // Story Area Additional
    begin: 'Comenzar',
    continueStory: 'Continuar',
    continueStoryFull: 'Continuar Historia',
    creating: 'Creando...',
    
    // Common Additional
    image: 'Imagen',
    photo: 'Foto',
    yourPhoto: 'Tu Foto',
    
    // Placeholders
    foxImage: 'Imagen del Zorrito',
    generateWithAI: 'Generar con IA',
    avatarReadyForStories: '✨ Avatar listo para tus historias',
    photoReadyForIllustrations: '🎨 Foto lista para ilustraciones',
    avatarReady: 'Avatar Listo',
    youWillAppearInIllustrations: 'Aparecerás en todas las ilustraciones',
    youWillAppearInIllustrationsWithAge: 'Aparecerás en las ilustraciones',
    willBeUsedForIllustrations: 'Se usará para ilustraciones',
    years: 'años',
    
    // Additional Story Area
    yourMagicalStory: 'Tu Historia Mágica',
    magicalIllustration: 'Ilustración Mágica',
    illustratedStory: 'Historia Ilustrada',
    storyIllustration: 'Ilustración de la historia',
    of: 'de',
    by: 'de',
    illustrationStyle: 'Estilo de Ilustración:',
    illustrationWithYourFace: 'Una ilustración con tu cara como protagonista',
    generateAIIllustration: 'Generar Ilustración AI',
    aiGeneratedIllustration: '¡Ilustración generada con IA!',
    youAppearAsMainCharacter: 'Apareces como personaje principal.',
    wantToChangeSomething: '¿Quieres cambiar algo en la historia?',
    whatDoYouWantToHappen: '💭 ¿Qué quieres que pase en la historia?',
    storyCompleted: '¡Historia Completada!',
    adventureHasEnded: 'La aventura ha llegado a su fin',
    newStoryButton: 'Nueva Historia',
    magicalStoryOfThemeBy: 'Historia mágica de',
    beautifulIllustrationWillAppear: 'Aquí aparecerá una hermosa ilustración',
    beautifulIllustrationAccompanies: 'Una hermosa ilustración acompaña esta parte de la historia',
    continuingTheStory: 'Continuando la historia...',
    magicalStoryOf: 'Historia mágica de',
    creatingYourMagicalStory: 'Creando tu historia mágica...',
    yourMagicalStoryWillBeginHere: 'Tu historia mágica comenzará aquí...',
    clickToStartAdventure: '✨ ¡Haz clic en "Comenzar Historia" para iniciar tu aventura mágica! 🚀',
    chapter: 'Capítulo',
    readyToBegin: 'Lista para comenzar',
    creatingYourStory: 'Creando tu historia...',
    startStory: 'Comenzar Historia',
    beginAdventure: '¡Comenzar Aventura!',
    creatingAvatar: '🎭 Creando avatar...',
    photoCaptured: '¡Foto capturada!',
    avatarCreated: '✨ ¡Avatar creado!',
    photoReady: '📸 ¡Foto lista!',
    newStory: 'Historia nueva',
    endStory: 'Terminar Historia',
    howDoYouFeel: '¿Cómo te sientes?',
    analyzingPhoto: 'Analizando foto...',
    generatingAvatar: 'Generando avatar...'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Try to get language from localStorage first
    const savedLanguage = localStorage.getItem('dreamairy-language');
    if (savedLanguage && translations[savedLanguage]) {
      return savedLanguage;
    }
    
    // Default to English (changed from browser detection)
    return 'en';
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