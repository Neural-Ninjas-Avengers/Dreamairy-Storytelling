import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AudioControls from './AudioControls';
import EmotionDetector from './EmotionDetector';
import { useLanguage } from '../contexts/LanguageContext';

// Mapeo de temas a nombres - se usará con traducciones dentro del componente

// Mapeo de temas a imágenes de fondo
const themeBackgrounds = {
  animals: '/theme-images/animals.jpg',
  dinosaurs: '/theme-images/dinosaurs.jpg',
  magic: '/theme-images/magic.jpg',
  pirates: '/theme-images/pirates.jpg',
  space: '/theme-images/space.jpg',
  superheroes: '/theme-images/superheroes.jpg',
  // Fallback para temas sin imagen específica
  adventure: '/theme-images/animals.jpg',
  fantasy: '/theme-images/magic.jpg',
  friendship: '/theme-images/animals.jpg',
  ocean: '/theme-images/pirates.jpg',
  dragons: '/theme-images/magic.jpg'
};

// Mapeo de emociones a emojis y colores (incluye todas las emociones de AWS Rekognition)
const emotionConfig = {
  happy: { emoji: '😊', label: 'Feliz', color: 'bg-yellow-100 text-yellow-800' },
  sad: { emoji: '😢', label: 'Triste', color: 'bg-blue-100 text-blue-800' },
  angry: { emoji: '😠', label: 'Enfadado', color: 'bg-red-100 text-red-800' },
  surprised: { emoji: '😲', label: 'Sorprendido', color: 'bg-purple-100 text-purple-800' },
  neutral: { emoji: '😐', label: 'Neutral', color: 'bg-gray-100 text-gray-800' },
  excited: { emoji: '🤩', label: 'Emocionado', color: 'bg-pink-100 text-pink-800' },
  scared: { emoji: '😨', label: 'Asustado', color: 'bg-orange-100 text-orange-800' },
  calm: { emoji: '😌', label: 'Tranquilo', color: 'bg-green-100 text-green-800' },
  confused: { emoji: '😕', label: 'Confundido', color: 'bg-amber-100 text-amber-800' },
  disgusted: { emoji: '🤢', label: 'Disgustado', color: 'bg-lime-100 text-lime-800' },
  fear: { emoji: '😰', label: 'Miedo', color: 'bg-orange-100 text-orange-800' }
};

const ChildFriendlyStoryArea = ({
  storyService,
  sessionId,
  selectedAge,
  selectedTheme,
  selectedGender,
  capturedPhoto,
  childName,
  onEndSession
}) => {
  const { language, t } = useLanguage();
  
  // Mapeo de temas usando traducciones
  const themeNames = {
    animals: t('themes.animals'),
    adventure: t('themes.adventure'),
    fantasy: t('themes.fantasy'),
    friendship: t('themes.friendship'),
    space: t('themes.space'),
    ocean: t('themes.ocean'),
    dinosaurs: t('themes.dinosaurs'),
    magic: t('themes.magic'),
    pirates: t('themes.pirates'),
    dragons: t('themes.dragons'),
    superheroes: t('themes.superheroes')
  };
  
  const [currentStory, setCurrentStory] = useState('');
  const [storyImage, setStoryImage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [storySegments, setStorySegments] = useState([]);
  const [currentChapter, setCurrentChapter] = useState(0);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [showVoiceSelector, setShowVoiceSelector] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('Lucia');
  const [availableVoices, setAvailableVoices] = useState([]);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [shouldAnalyzeEmotion, setShouldAnalyzeEmotion] = useState(false);
  const [userSuggestion, setUserSuggestion] = useState('');
  const [showSuggestionInput, setShowSuggestionInput] = useState(false);
  const [isStoryFinished, setIsStoryFinished] = useState(false);
  const audioRef = React.useRef(null);

  // NO generar historia automáticamente - el usuario debe hacer click
  // useEffect(() => {
  //   if (storyService && sessionId) {
  //     generateNewStory();
  //   }
  // }, [storyService, sessionId]);

  // Cargar voces disponibles de Polly
  React.useEffect(() => {
    const loadVoices = async () => {
      if (storyService) {
        try {
          // Update service language before fetching voices
          storyService.language = language;
          const voices = await storyService.getAvailableVoices();
          console.log('🎤 Loaded voices:', voices);
          // Asegurar que siempre sea un array
          setAvailableVoices(Array.isArray(voices) ? voices : []);
          
          // Set default voice based on language
          if (voices && voices.length > 0) {
            const defaultVoice = language === 'en' ? 'Joanna' : 'Lucia';
            const voiceExists = voices.find(v => v.id === defaultVoice);
            setSelectedVoice(voiceExists ? defaultVoice : voices[0].id);
            console.log('🎤 Selected voice:', voiceExists ? defaultVoice : voices[0].id);
          }
        } catch (error) {
          console.error('Error loading voices:', error);
          // Fallback a voces por defecto según idioma
          const fallbackVoices = language === 'en' 
            ? [
                { id: 'Joanna', name: 'Joanna', gender: 'Female' },
                { id: 'Matthew', name: 'Matthew', gender: 'Male' }
              ]
            : [
                { id: 'Lucia', name: 'Lucía', gender: 'Female' },
                { id: 'Enrique', name: 'Enrique', gender: 'Male' }
              ];
          setAvailableVoices(fallbackVoices);
          setSelectedVoice(fallbackVoices[0].id);
          console.log('🎤 Using fallback voices:', fallbackVoices);
        }
      }
    };
    loadVoices();
  }, [storyService, language]);

  // Limpiar audio al desmontar
  React.useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Actualizar imagen cuando cambia el capítulo actual
  React.useEffect(() => {
    if (storySegments[currentChapter]) {
      const segment = storySegments[currentChapter];
      const segmentImage = generatedImages.find(img => img.storySegmentIndex === currentChapter);
      
      if (segmentImage) {
        setStoryImage(segmentImage.url);
      } else if (segment.image) {
        setStoryImage(segment.image);
      }
      
      setCurrentStory(segment.text);
    }
  }, [currentChapter, storySegments, generatedImages]);

  // Manejar emoción detectada
  const handleEmotionDetected = (emotionData) => {
    console.log('😊 Emoción detectada por EmotionDetector:', emotionData);
    // Extraer solo el nombre de la emoción del objeto
    const emotionName = emotionData?.emotion || emotionData;
    console.log('🎭 Emoción extraída:', emotionName);
    setDetectedEmotion(emotionName);
    setShouldAnalyzeEmotion(false); // Reset trigger
  };

  // Función para detener el audio
  const stopAudio = () => {
    console.log('🛑 Stopping audio');
    
    // Detener audio de AWS Polly
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    // Detener Browser TTS
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    
    setIsPlaying(false);
  };

  // Función para reproducir audio con Polly
  const playAudio = async () => {
    if (!currentStory || !storyService || !sessionId) {
      console.warn('⚠️ Cannot play audio: missing story, service, or session');
      return;
    }
    
    try {
      console.log('🎵 Playing audio with voice:', selectedVoice);
      setIsPlaying(true);
      
      // Detener audio anterior si existe
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      
      // Obtener el audio del backend
      const response = await fetch(`${storyService.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: currentStory,
          language: language,
          voice_id: selectedVoice
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('🎵 Audio response:', result);
      
      // Verificar si debemos usar Browser TTS
      if (result.use_browser_tts) {
        console.log('🎵 Using browser TTS fallback');
        // Usar Web Speech API del navegador
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(currentStory);
          utterance.lang = language === 'en' ? 'en-US' : 'es-ES';
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          
          // Intentar usar una voz específica
          const voices = speechSynthesis.getVoices();
          const voice = voices.find(v => v.lang.startsWith(language === 'en' ? 'en' : 'es'));
          if (voice) {
            utterance.voice = voice;
          }
          
          utterance.onend = () => {
            console.log('🎵 Browser TTS finished');
            setIsPlaying(false);
          };
          
          utterance.onerror = (error) => {
            console.error('❌ Browser TTS error:', error);
            setIsPlaying(false);
          };
          
          speechSynthesis.speak(utterance);
          console.log('🎵 Browser TTS playing...');
        } else {
          console.error('❌ Browser TTS not supported');
          setIsPlaying(false);
        }
      } else if (result.audio_data || result.audio_url) {
        // Reproducir audio de AWS Polly
        const audioUrl = result.audio_data || result.audio_url;
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        
        audio.onended = () => {
          console.log('🎵 Audio finished');
          setIsPlaying(false);
          audioRef.current = null;
        };
        
        audio.onerror = (error) => {
          console.error('❌ Audio error:', error);
          setIsPlaying(false);
          audioRef.current = null;
        };
        
        await audio.play();
        console.log('🎵 Audio playing...');
      } else {
        console.warn('⚠️ No audio data in response');
        setIsPlaying(false);
      }
    } catch (error) {
      console.error('❌ Error playing audio:', error);
      setIsPlaying(false);
      audioRef.current = null;
    }
  };

  // Generar SVG fallback mejorado
  const generateEnhancedSVGFallback = async (storyText) => {
    const themes = {
      animals: { bg: '#F59E0B', accent: '#D97706', secondary: '#FCD34D' },
      adventure: { bg: '#10B981', accent: '#059669', secondary: '#34D399' },
      fantasy: { bg: '#8B5CF6', accent: '#7C3AED', secondary: '#A78BFA' },
      friendship: { bg: '#EC4899', accent: '#DB2777', secondary: '#F472B6' }
    };

    const colors = themes[selectedTheme] || themes.fantasy;
    const variation = Date.now() % 3;

    const svgContent = `<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="bg${variation}" cx="50%" cy="30%" r="80%">
          <stop offset="0%" style="stop-color:${colors.bg};stop-opacity:0.9" />
          <stop offset="70%" style="stop-color:${colors.accent};stop-opacity:0.7" />
          <stop offset="100%" style="stop-color:${colors.secondary};stop-opacity:1" />
        </radialGradient>
      </defs>
      <rect width="400" height="300" fill="url(#bg${variation})" rx="15"/>
      <ellipse cx="200" cy="250" rx="180" ry="30" fill="${colors.accent}" opacity="0.4"/>
      <circle cx="${150 + variation * 20}" cy="${120 + variation * 10}" r="40" fill="#FFF" opacity="0.3"/>
      <circle cx="${250 - variation * 15}" cy="${140 + variation * 8}" r="30" fill="#FFF" opacity="0.2"/>
      <circle cx="200" cy="${80 + variation * 5}" r="20" fill="#FDCB6E" opacity="0.8"/>
      <text x="200" y="280" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#FFF" opacity="0.8">${t('illustratedStory')}</text>
    </svg>`;

    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // Generar imagen automática para el segmento
  const generateAutomaticImage = async (storySegment, segmentIndex) => {
    try {
      console.log('🎨 Generando imagen automática para capítulo:', segmentIndex + 1);

      const hasUserAvatar = capturedPhoto?.has_avatar && capturedPhoto?.avatar_url;
      const hasUserPhoto = capturedPhoto?.base64;

      // Crear un contexto más enfocado: solo los últimos 2 capítulos para mantener coherencia
      const recentContext = storySegments.slice(-2).map(s => s.text).join(' ');
      
      const imageRequest = {
        scene_description: `Capítulo ${segmentIndex + 1}: ${storySegment.text}. IMPORTANTE: Ilustra específicamente esta escena del capítulo actual. ${selectedGender === 'niña' ? 'La protagonista es una niña' : 'El protagonista es un niño'} de ${selectedAge} años que participa activamente en ESTA escena específica.`,
        story_context: recentContext, // Solo contexto reciente para no confundir
        character_description: hasUserAvatar ?
          `El personaje principal es ${selectedGender === 'niña' ? 'una niña' : 'un niño'} de ${selectedAge} años que se parece al avatar proporcionado. Debe ser claramente visible y central en la escena.` :
          hasUserPhoto ?
            `${selectedGender === 'niña' ? 'Una niña' : 'Un niño'} de ${selectedAge} años protagonista que se parece a la foto del usuario. Debe ser el foco de la imagen.` :
            `${selectedGender === 'niña' ? 'Una niña' : 'Un niño'} de ${selectedAge} años como personaje principal, claramente visible y central en la escena`,
        style: 'semi_realistic_children',
        has_user_photo: hasUserPhoto,
        has_user_avatar: hasUserAvatar,
        user_photo_base64: capturedPhoto?.base64 || null,
        user_avatar_url: capturedPhoto?.avatar_url || null,
        theme: selectedTheme,
        child_age: selectedAge,
        child_gender: selectedGender || 'niño'
      };

      console.log('🔍 Enviando request de imagen:', imageRequest);
      const imageResult = await storyService.generateStoryImage(sessionId, imageRequest);
      console.log('📥 Respuesta de imagen recibida:', imageResult);

      if (imageResult && (imageResult.success !== false) && (imageResult.imageUrl || imageResult.image_url)) {
        const newImage = {
          id: `auto-${segmentIndex}-${Date.now()}`,
          url: imageResult.imageUrl || imageResult.image_url,
          prompt: imageResult.prompt || storySegment.text.substring(0, 100),
          timestamp: Date.now(),
          storySegmentIndex: segmentIndex,
          isAutoGenerated: true
        };

        setGeneratedImages(prev => [...prev, newImage]);

        // Actualizar el segmento con la imagen
        setStorySegments(prev =>
          prev.map((seg, idx) =>
            idx === segmentIndex ? { ...seg, image: newImage.url } : seg
          )
        );

        // Si es el capítulo actual, actualizar la imagen mostrada
        if (segmentIndex === currentChapter) {
          setStoryImage(newImage.url);
        }

        console.log('✅ Imagen generada exitosamente:', newImage.id);
        console.log('🖼️ URL de imagen:', newImage.url.substring(0, 100) + '...');
      }
    } catch (error) {
      console.warn('⚠️ Generación de imagen falló, usando SVG fallback:', error.message);

      // Generar SVG fallback
      const fallbackImage = await generateEnhancedSVGFallback(storySegment.text);

      const fallbackImageObj = {
        id: `fallback-${segmentIndex}-${Date.now()}`,
        url: fallbackImage,
        prompt: storySegment.text.substring(0, 100),
        timestamp: Date.now(),
        storySegmentIndex: segmentIndex,
        isAutoGenerated: true,
        isFallback: true
      };

      setGeneratedImages(prev => [...prev, fallbackImageObj]);

      // Actualizar el segmento con la imagen fallback
      setStorySegments(prev =>
        prev.map((seg, idx) =>
          idx === segmentIndex ? { ...seg, image: fallbackImage } : seg
        )
      );

      // Si es el capítulo actual, actualizar la imagen mostrada
      if (segmentIndex === currentChapter) {
        setStoryImage(fallbackImage);
      }
    }
  };

  const generateNewStory = async (isFinale = false) => {
    if (!storyService || !sessionId) return;

    // Reset finished state if starting a new story
    if (storySegments.length === 0) {
      setIsStoryFinished(false);
      console.log('🔄 Reseteando estado de historia terminada');
    }

    setIsGenerating(true);
    try {
      // Detectar emoción antes de generar cada capítulo
      let detectedEmotion = null;
      let emotionConfidence = 0;
      
      // Detectar emoción siempre (incluso en el primer capítulo)
      try {
        console.log('📸 Capturando foto para detectar emoción...');
        const emotionResult = await storyService.detectEmotionFromWebcam(sessionId);
        if (emotionResult && emotionResult.emotion) {
          detectedEmotion = emotionResult.emotion;
          emotionConfidence = emotionResult.confidence || 0;
          console.log(`😊 Emoción detectada: ${detectedEmotion} (${(emotionConfidence * 100).toFixed(0)}%)`);
          // Actualizar el estado global de emoción
          setDetectedEmotion(detectedEmotion);
        }
      } catch (error) {
        console.warn('⚠️ No se pudo detectar emoción, continuando sin adaptación:', error);
        // TEMPORAL: Simular emoción para testing (eliminar cuando el endpoint funcione)
        const mockEmotions = ['happy', 'excited', 'surprised', 'neutral'];
        const mockEmotion = mockEmotions[Math.floor(Math.random() * mockEmotions.length)];
        console.log(`🎭 Usando emoción simulada para testing: ${mockEmotion}`);
        setDetectedEmotion(mockEmotion);
        detectedEmotion = mockEmotion;
        emotionConfidence = 0.85;
      }

      // Generar historia usando el mismo método que ModernStoryArea
      const storyContext = storySegments.map(s => s.text).join(' ');
      const lastSegment = storySegments.length > 0 ? storySegments[storySegments.length - 1].text : '';

      const requestData = {
        theme: selectedTheme,
        segments_so_far: storySegments.length,
        child_age: selectedAge,
        child_gender: selectedGender || 'niño',
        emotional_goal: 'entertain',
        language: language, // ✅ Use selected language from context
        story_context: storyContext,
        last_segment: lastSegment,
        is_finale: isFinale
      };

      // Solo añadir emoción si fue detectada
      if (detectedEmotion) {
        requestData.detected_emotion = detectedEmotion;
        requestData.emotion_confidence = emotionConfidence;
      }

      // Añadir sugerencia del usuario si existe
      if (userSuggestion && userSuggestion.trim()) {
        requestData.user_suggestion = userSuggestion.trim();
        console.log('💡 Sugerencia del usuario:', userSuggestion);
        // Limpiar la sugerencia después de usarla
        setUserSuggestion('');
        setShowSuggestionInput(false);
      }

      const response = await storyService.generateStorySegment(sessionId, requestData);

      const storyText = response.story || response.text || response.content;

      if (storyText) {
        // Check if this is the final chapter - ONLY when user explicitly pressed "Terminar"
        console.log('📊 isFinale:', isFinale, 'isStoryFinished:', isStoryFinished);
        if (isFinale) {
          setIsStoryFinished(true);
          console.log('🎬 Historia terminada - botones deshabilitados');
        } else {
          console.log('✅ Historia continúa - botones activos');
        }
        
        const newSegment = {
          text: storyText,
          image: null,
          id: Date.now()
        };

        const newSegmentIndex = storySegments.length;

        setStorySegments(prev => {
          const updated = [...prev, newSegment];
          setCurrentChapter(updated.length - 1);
          return updated;
        });

        setCurrentStory(storyText);

        // Generar imagen automáticamente
        await generateAutomaticImage(newSegment, newSegmentIndex);
      }
    } catch (error) {
      console.error('Error generating story:', error);
      // Fallback a historia simple
      const fallbackStory = `Había una vez ${capturedPhoto ? 'un niño muy especial' : 'un pequeño aventurero'} que vivía en un mundo mágico y lleno de aventuras emocionantes...`;
      const newSegment = { text: fallbackStory, image: null, id: Date.now() };
      const newSegmentIndex = storySegments.length;

      setCurrentStory(fallbackStory);
      setStorySegments(prev => {
        const updated = [...prev, newSegment];
        setCurrentChapter(updated.length - 1);
        return updated;
      });

      // Generar imagen fallback incluso para historia demo
      await generateAutomaticImage(newSegment, newSegmentIndex);
    } finally {
      setIsGenerating(false);
    }
  };

  // Audio is now handled by AudioControls component

  // Obtener imagen de fondo según el tema
  const backgroundImage = selectedTheme && themeBackgrounds[selectedTheme] 
    ? themeBackgrounds[selectedTheme] 
    : null;

  return (
    <div className="min-h-screen h-screen relative overflow-y-auto overflow-x-hidden">
      {/* Imagen de fondo temática */}
      {backgroundImage && (
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url(${backgroundImage})`,
            filter: 'brightness(0.7) blur(1px)'
          }}
        />
      )}
      
      {/* Overlay suave para mejorar legibilidad */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/15 to-black/25" />
      
      {/* Elementos decorativos de fondo - reducidos */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Burbujas flotantes - menos cantidad */}
        {[...Array(4)].map((_, i) => (
          <motion.div
            key={`bubble-${i}`}
            className="absolute rounded-full bg-white/10"
            style={{
              width: `${30 + Math.random() * 30}px`,
              height: `${30 + Math.random() * 30}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -80, 0],
              x: [0, Math.random() * 30 - 15, 0],
              scale: [1, 1.1, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: Math.random() * 4
            }}
          />
        ))}
      </div>

      {/* Contenedor centrado con max-width y altura controlada */}
      <div className="relative z-10 max-w-4xl mx-auto px-4 py-4 h-full flex flex-col">

        {/* Header con avatar y controles - compacto */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-3 shadow-xl mb-3 flex-shrink-0 relative" style={{ zIndex: 100 }}>
          <div className="flex items-center justify-between">
            {/* Avatar del usuario */}
            <div className="flex items-center space-x-3">
              <motion.div
                className="w-12 h-12 rounded-full overflow-hidden border-3 border-white shadow-lg"
                animate={{
                  rotate: [0, 3, -3, 0],
                  scale: [1, 1.03, 1]
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                {capturedPhoto?.avatar_url ? (
                  <img
                    src={capturedPhoto.avatar_url}
                    alt="Tu Avatar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                    <span className="text-xl">👤</span>
                  </div>
                )}
              </motion.div>

              <div className="flex-1">
                <h2 className="text-base font-bold text-gray-800">
                  {childName && selectedTheme && themeNames[selectedTheme]
                    ? `${t('magicalStoryOf')} ${themeNames[selectedTheme]} ${t('by')} ${childName}`
                    : childName
                      ? `${t('magicalStoryOf')} ${childName}`
                      : selectedTheme && themeNames[selectedTheme]
                        ? `${t('magicalStoryOf')} ${themeNames[selectedTheme]}`
                        : t('yourMagicalStory')}
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-600">
                    {storySegments.length > 0 ? `${t('chapter')} ${storySegments.length}` : t('readyToBegin')}
                  </p>
                  {detectedEmotion && emotionConfig[detectedEmotion] && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${emotionConfig[detectedEmotion].color}`}
                    >
                      <span>{emotionConfig[detectedEmotion].emoji}</span>
                      <span>{emotionConfig[detectedEmotion].label}</span>
                    </motion.div>
                  )}
                </div>
              </div>
            </div>

            {/* Controles: Audio y Salir */}
            <div className="flex items-center space-x-2 relative">
              {/* Botones de audio */}
              {currentStory && (
                <>
                  {/* Botón de Play/Stop */}
                  <motion.button
                    onClick={isPlaying ? stopAudio : playAudio}
                    className={`${isPlaying ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'} text-white p-2 rounded-full shadow-lg`}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <span className="text-lg">{isPlaying ? '⏹️' : '▶️'}</span>
                  </motion.button>

                  {/* Botón de selector de voz */}
                  <div className="relative">
                    <motion.button
                      onClick={() => setShowVoiceSelector(!showVoiceSelector)}
                      className="bg-blue-400 hover:bg-blue-500 text-white p-2 rounded-full shadow-lg"
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <span className="text-lg">🎤</span>
                    </motion.button>
                    
                    {/* Selector de voces */}
                    {showVoiceSelector && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute right-0 mt-2 bg-white rounded-lg shadow-2xl p-3 min-w-[200px]"
                        style={{ zIndex: 9999 }}
                      >
                        <p className="text-xs font-bold text-gray-700 mb-2">Elige una voz:</p>
                        <div className="space-y-1 max-h-48 overflow-y-auto">
                          {Array.isArray(availableVoices) && availableVoices.map((voice) => (
                            <button
                              key={voice.id}
                              onClick={() => {
                                setSelectedVoice(voice.id);
                                setShowVoiceSelector(false);
                              }}
                              className={`w-full text-left px-3 py-2 rounded text-sm ${
                                selectedVoice === voice.id
                                  ? 'bg-blue-100 text-blue-700 font-bold'
                                  : 'hover:bg-gray-100 text-gray-700'
                              }`}
                            >
                              {voice.name} {voice.gender === 'Female' ? '👧' : '👦'}
                            </button>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </div>
                </>
              )}
              
              {/* Botón de salir */}
              <motion.button
                onClick={onEndSession}
                className="bg-red-400 hover:bg-red-500 text-white p-2 rounded-full shadow-lg"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <span className="text-lg">🏠</span>
              </motion.button>
            </div>
          </div>
        </div>

        {/* Layout compacto: todo en una columna - usa el espacio disponible */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl overflow-hidden flex-grow flex flex-col">
          
          {/* Imagen arriba - responsive */}
          <div className="relative bg-gradient-to-br from-blue-50 to-purple-50 flex-shrink-0" style={{ height: 'clamp(250px, 35vh, 400px)' }}>
              <AnimatePresence>
                {isGenerating ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center"
                  >
                    <div className="text-center">
                      <motion.div
                        className="text-5xl mb-3"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      >
                        ✨
                      </motion.div>
                      <p className="text-base font-bold text-gray-700">{t('creatingYourStory')}</p>
                    </div>
                  </motion.div>
                ) : storyImage ? (
                  <motion.img
                    key="story-image"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    src={storyImage}
                    alt={t('storyIllustration')}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <motion.div
                    key="placeholder"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 flex items-center justify-center bg-gray-50"
                  >
                    <span className="text-6xl">🎭</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

          {/* Texto y controles abajo - flexible y con scroll si es necesario */}
          <div className="p-4 flex-grow overflow-y-auto flex flex-col">
            {/* Navegación de capítulos */}
            {storySegments.length > 1 && (
              <div className="flex justify-center space-x-2 mb-4">
                {storySegments.map((segment, idx) => {
                  const segmentImage = generatedImages.find(img => img.storySegmentIndex === idx);
                  return (
                    <button
                      key={idx}
                      onClick={() => {
                        setCurrentChapter(idx);
                        setCurrentStory(segment.text);
                        setStoryImage(segmentImage?.url || segment.image);
                      }}
                      className={`w-8 h-8 rounded-full font-bold ${currentChapter === idx
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                        }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            )}

            <motion.div
              key={currentChapter}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-3 mb-3 flex-grow overflow-y-auto"
            >
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-xs font-bold text-purple-600">{t('chapter')} {currentChapter + 1}</h3>
              </div>
              <p className="text-base leading-relaxed text-gray-800 font-medium">
                {currentStory || t('clickToStartAdventure')}
              </p>
            </motion.div>

            {/* Botones de acción */}
            {!isStoryFinished ? (
              <>
                <div className="flex gap-2">
                  <motion.button
                    onClick={() => generateNewStory(false)}
                    disabled={isGenerating}
                    className={`flex-1 py-3 px-4 rounded-xl font-bold text-base shadow-lg ${isGenerating
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-400 to-emerald-500 text-white hover:shadow-xl'
                      }`}
                    whileHover={!isGenerating ? { scale: 1.02 } : {}}
                    whileTap={!isGenerating ? { scale: 0.98 } : {}}
                  >
                    {isGenerating ? (
                      <div className="flex items-center justify-center space-x-2">
                        <motion.span
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                          ⏳
                        </motion.span>
                        <span>{t('creating')}</span>
                      </div>
                    ) : (
                      <>
                        <span className="mr-2">📖</span>
                        {storySegments.length === 0 ? t('begin') : t('continueStory')}
                      </>
                    )}
                  </motion.button>

                  {/* Botón de terminar historia - solo si ya hay capítulos */}
                  {storySegments.length > 0 && (
                    <motion.button
                      onClick={() => generateNewStory(true)}
                      disabled={isGenerating}
                      className={`flex-1 py-3 px-4 rounded-xl font-bold text-base shadow-lg ${isGenerating
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-purple-400 to-pink-500 text-white hover:shadow-xl'
                        }`}
                      whileHover={!isGenerating ? { scale: 1.02 } : {}}
                      whileTap={!isGenerating ? { scale: 0.98 } : {}}
                    >
                      <span className="mr-2">🎬</span>
                      Terminar
                    </motion.button>
                  )}
                </div>

                {/* Campo de sugerencias del usuario */}
                {storySegments.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4"
              >
                {!showSuggestionInput ? (
                  <motion.button
                    onClick={() => setShowSuggestionInput(true)}
                    className="w-full py-2 px-4 rounded-xl font-medium text-sm bg-gradient-to-r from-blue-400 to-cyan-500 text-white hover:shadow-lg"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="mr-2">💡</span>
                    {t('wantToChangeSomething')}
                  </motion.button>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white/90 backdrop-blur-sm rounded-xl p-4 shadow-lg border-2 border-blue-300"
                  >
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      {t('whatDoYouWantToHappen')}
                    </label>
                    <textarea
                      value={userSuggestion}
                      onChange={(e) => setUserSuggestion(e.target.value)}
                      placeholder="Ejemplo: Quiero que aparezca un dragón amigable..."
                      className="w-full px-4 py-3 rounded-lg border-2 border-blue-200 focus:border-blue-400 focus:outline-none text-base resize-none"
                      rows="3"
                      maxLength="200"
                    />
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => {
                          setShowSuggestionInput(false);
                          setUserSuggestion('');
                        }}
                        className="flex-1 py-2 px-4 rounded-lg font-medium text-sm bg-gray-200 text-gray-700 hover:bg-gray-300"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={() => {
                          if (userSuggestion.trim()) {
                            generateNewStory();
                          }
                        }}
                        disabled={!userSuggestion.trim()}
                        className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm ${
                          userSuggestion.trim()
                            ? 'bg-gradient-to-r from-blue-400 to-cyan-500 text-white hover:shadow-lg'
                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        ✨ Aplicar
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {userSuggestion.length}/200 caracteres
                    </p>
                  </motion.div>
                )}
              </motion.div>
            )}
              </>
            ) : (
              /* Mensaje cuando la historia ha terminado */
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-6"
              >
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-2xl font-bold text-purple-600 mb-2">{t('storyCompleted')}</h3>
                <p className="text-gray-600 mb-4">{t('adventureHasEnded')}</p>
                <motion.button
                  onClick={onEndSession}
                  className="py-3 px-6 rounded-xl font-bold text-base shadow-lg bg-gradient-to-r from-blue-400 to-purple-500 text-white hover:shadow-xl"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span className="mr-2">✨</span>
                  {t('newStoryButton')}
                </motion.button>
              </motion.div>
            )}

          </div>
        </div>
      </div>

      {/* Elementos decorativos sutiles */}
      <motion.div
        className="absolute bottom-10 left-10 text-4xl opacity-10 pointer-events-none"
        animate={{
          rotate: [0, 5, -5, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        🎪
      </motion.div>

      <motion.div
        className="absolute top-20 right-20 text-3xl opacity-10 pointer-events-none"
        animate={{
          y: [0, -15, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        🎈
      </motion.div>

      {/* Hidden Emotion Detector */}
      <div style={{ display: 'none' }}>
        <EmotionDetector 
          onEmotionDetected={handleEmotionDetected}
          capturedPhoto={capturedPhoto}
          triggerAnalysis={shouldAnalyzeEmotion}
        />
      </div>
    </div>
  );
};

export default ChildFriendlyStoryArea;