import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import EmotionDetector from './EmotionDetector';
import AudioControls from './AudioControls';
import { useLanguage } from '../contexts/LanguageContext';

const ModernStoryArea = ({ 
  storyService, 
  sessionId, 
  selectedAge, 
  selectedEmotion, 
  selectedTheme,
  selectedGender,
  capturedPhoto,
  onEndSession 
}) => {
  const { t, language } = useLanguage();
  const [storySegments, setStorySegments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionDuration, setSessionDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const storyContentRef = React.useRef(null);

  useEffect(() => {
    // Start session timer
    const startTime = Date.now();
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setSessionDuration(elapsed);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Extract visual elements from story text for image generation
  const extractVisualDescription = (storyText, theme) => {
    const text = storyText.toLowerCase();
    
    // Extract key visual elements with more comprehensive detection
    const characters = [];
    const settings = [];
    const objects = [];
    const actions = [];
    const emotions = [];
    
    // Character detection (expanded)
    if (text.includes('hada') || text.includes('fairy')) characters.push('magical fairy');
    if (text.includes('princesa') || text.includes('princess')) characters.push('princess');
    if (text.includes('dragón') || text.includes('dragon')) characters.push('friendly dragon');
    if (text.includes('unicornio') || text.includes('unicorn')) characters.push('unicorn');
    if (text.includes('conejo') || text.includes('rabbit') || text.includes('luna')) characters.push('cute rabbit');
    if (text.includes('león') || text.includes('lion')) characters.push('brave lion');
    if (text.includes('búho') || text.includes('owl')) characters.push('wise owl');
    if (text.includes('ardilla') || text.includes('squirrel')) characters.push('playful squirrel');
    if (text.includes('capitán') || text.includes('captain')) characters.push('brave captain');
    if (text.includes('pirata') || text.includes('pirate')) characters.push('friendly pirate');
    
    // Setting detection (expanded)
    if (text.includes('bosque') || text.includes('forest') || text.includes('árbol')) settings.push('enchanted forest with tall trees');
    if (text.includes('castillo') || text.includes('castle') || text.includes('torre')) settings.push('magical castle with towers');
    if (text.includes('reino') || text.includes('kingdom') || text.includes('cristal')) settings.push('crystal kingdom');
    if (text.includes('jardín') || text.includes('garden')) settings.push('beautiful garden');
    if (text.includes('mar') || text.includes('océano') || text.includes('ocean') || text.includes('barco')) settings.push('magical ocean with ships');
    if (text.includes('montaña') || text.includes('mountain')) settings.push('mystical mountains');
    if (text.includes('cueva') || text.includes('cave')) settings.push('mysterious cave');
    if (text.includes('isla') || text.includes('island')) settings.push('tropical island');
    if (text.includes('pueblo') || text.includes('village') || text.includes('casa')) settings.push('cozy village');
    if (text.includes('sendero') || text.includes('camino') || text.includes('path')) settings.push('winding forest path');
    if (text.includes('nube') || text.includes('cloud') || text.includes('cielo')) settings.push('sky with fluffy clouds');
    
    // Object detection (expanded)
    if (text.includes('corona') || text.includes('crown')) objects.push('golden crown');
    if (text.includes('varita') || text.includes('wand')) objects.push('magic wand');
    if (text.includes('espada') || text.includes('sword')) objects.push('shining sword');
    if (text.includes('flor') || text.includes('flower')) objects.push('colorful flowers');
    if (text.includes('estrella') || text.includes('star')) objects.push('sparkling stars');
    if (text.includes('luna') || text.includes('moon')) objects.push('bright moon');
    if (text.includes('tesoro') || text.includes('treasure')) objects.push('treasure chest');
    if (text.includes('mapa') || text.includes('map')) objects.push('ancient map');
    if (text.includes('luz') || text.includes('light') || text.includes('brilla')) objects.push('magical glowing light');
    if (text.includes('melodía') || text.includes('música') || text.includes('canta')) objects.push('musical notes');
    
    // Action detection (expanded)
    if (text.includes('volar') || text.includes('voló') || text.includes('flying')) actions.push('flying gracefully through the air');
    if (text.includes('bailar') || text.includes('dancing')) actions.push('dancing joyfully');
    if (text.includes('cantar') || text.includes('singing') || text.includes('canta')) actions.push('singing beautifully');
    if (text.includes('correr') || text.includes('running') || text.includes('saltó')) actions.push('running and jumping happily');
    if (text.includes('explorar') || text.includes('descubr') || text.includes('encontr')) actions.push('exploring and discovering');
    if (text.includes('ayudar') || text.includes('ayudó') || text.includes('helping')) actions.push('helping others kindly');
    if (text.includes('jugar') || text.includes('jugó') || text.includes('playing')) actions.push('playing together');
    if (text.includes('navegar') || text.includes('navegó')) actions.push('sailing across the seas');
    
    // Emotion detection
    if (text.includes('feliz') || text.includes('alegr') || text.includes('happy')) emotions.push('happy and joyful');
    if (text.includes('curioso') || text.includes('curiosidad')) emotions.push('curious and excited');
    if (text.includes('valiente') || text.includes('brave')) emotions.push('brave and confident');
    if (text.includes('amigo') || text.includes('amistad') || text.includes('friend')) emotions.push('friendly and caring');
    
    // Build rich description from story context
    let description = '';
    
    // Start with the main character and action
    if (characters.length > 0) {
      description += characters.slice(0, 2).join(' and ');
      if (actions.length > 0) {
        description += ' ' + actions[0];
      }
    } else if (actions.length > 0) {
      description += 'The protagonist ' + actions[0];
    }
    
    // Add setting
    if (settings.length > 0) {
      description += ' in ' + settings[0];
    } else {
      description += theme === 'fantasy' ? ' in a magical realm' : 
                    theme === 'animals' ? ' in a peaceful forest' : 
                    theme === 'adventure' ? ' on an exciting journey' :
                    ' in a wonderful place';
    }
    
    // Add objects
    if (objects.length > 0) {
      description += ', with ' + objects.slice(0, 2).join(' and ');
    }
    
    // Add emotions
    if (emotions.length > 0) {
      description += ', feeling ' + emotions[0];
    }
    
    // Add theme-specific atmosphere
    if (theme === 'fantasy') {
      description += ', magical sparkles and enchanted atmosphere';
    } else if (theme === 'animals') {
      description += ', natural beauty and friendly environment';
    } else if (theme === 'adventure') {
      description += ', exciting atmosphere and sense of discovery';
    } else if (theme === 'friendship') {
      description += ', warm and heartfelt atmosphere';
    }
    
    return description || 'A beautiful children\'s story scene';
  };

  const generateStorySegment = async (isFinale = false) => {
    setIsLoading(true);
    
    try {
      const storyContext = storySegments.map(s => s.text).join(' ');
      const lastSegment = storySegments.length > 0 ? storySegments[storySegments.length - 1].text : '';
      
      const response = await storyService.generateStorySegment(sessionId, {
        theme: selectedTheme,
        segments_so_far: storySegments.length,
        child_age: selectedAge,
        emotional_goal: selectedEmotion,
        language: language,
        gender: selectedGender,
        story_context: storyContext,
        last_segment: lastSegment,
        is_finale: isFinale,
        detected_emotion: detectedEmotion?.emotion,
        emotion_confidence: detectedEmotion?.confidence
      });
      
      const newSegment = {
        text: response.story || response.text || response.content,
        timestamp: Date.now(),
        index: storySegments.length
      };
      
      setStorySegments(prev => [...prev, newSegment]);
      
      // Auto-scroll to the latest segment
      setTimeout(() => {
        if (storyContentRef.current) {
          storyContentRef.current.scrollTop = storyContentRef.current.scrollHeight;
        }
      }, 100);
      
      // 🎨 Automatically generate image for the story segment
      await generateAutomaticImage(newSegment);
      
      // Audio will be controlled by AudioControls component
    } catch (error) {
      console.error('Error generating story segment:', error);
      // Fallback to demo content on error
      const fallbackSegment = {
        text: language === 'en' 
          ? "The story continues in a magical way... (Demo mode active)"
          : "La historia continúa de manera mágica... (Modo demo activo)",
        timestamp: Date.now(),
        index: storySegments.length
      };
      setStorySegments(prev => [...prev, fallbackSegment]);
      
      // Auto-scroll to the latest segment
      setTimeout(() => {
        if (storyContentRef.current) {
          storyContentRef.current.scrollTop = storyContentRef.current.scrollHeight;
        }
      }, 100);
      
      // Even for fallback, try to generate an image
      await generateAutomaticImage(fallbackSegment);
    } finally {
      setIsLoading(false);
    }
  };

  // 🎨 Generate enhanced SVG fallback
  const generateEnhancedSVGFallback = async (storySegment) => {
    // Create a simple but attractive SVG based on story content
    const storyText = storySegment.text.toLowerCase();
    
    // Detect theme from story content
    let theme = selectedTheme;
    if (storyText.includes('bosque') || storyText.includes('árbol')) theme = 'forest';
    else if (storyText.includes('océano') || storyText.includes('mar')) theme = 'ocean';
    else if (storyText.includes('castillo') || storyText.includes('palacio')) theme = 'castle';
    else if (storyText.includes('animal') || storyText.includes('conejo')) theme = 'animals';
    
    // Premium color schemes
    const themes = {
      animals: { bg: '#F59E0B', accent: '#D97706', secondary: '#FCD34D' },
      adventure: { bg: '#10B981', accent: '#059669', secondary: '#34D399' },
      fantasy: { bg: '#8B5CF6', accent: '#7C3AED', secondary: '#A78BFA' },
      friendship: { bg: '#EC4899', accent: '#DB2777', secondary: '#F472B6' },
      forest: { bg: '#059669', accent: '#047857', secondary: '#10B981' },
      ocean: { bg: '#3B82F6', accent: '#2563EB', secondary: '#60A5FA' },
      castle: { bg: '#6366F1', accent: '#4F46E5', secondary: '#818CF8' }
    };
    
    const colors = themes[theme] || themes.fantasy;
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
      <text x="200" y="280" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#FFF" opacity="0.8">${language === 'en' ? 'Illustrated Story' : 'Historia Ilustrada'}</text>
    </svg>`;
    
    return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`;
  };

  // 🎨 Automatic image generation for story segments
  const generateAutomaticImage = async (storySegment) => {
    try {
      console.log('🎨 Auto-generating image for story segment:', storySegment.index);
      
      // Create image request based on story content and user avatar/photo
      const hasUserAvatar = capturedPhoto?.has_avatar && capturedPhoto?.avatar_url;
      const hasUserPhoto = capturedPhoto?.base64;
      
      const genderDesc = selectedGender === 'male' ? 'boy' : selectedGender === 'female' ? 'girl' : 'child';
      
      // Extract key elements from the current story segment
      const visualDesc = extractVisualDescription(storySegment.text, selectedTheme);
      
      // Build rich scene description with full story context
      const storyExcerpt = storySegment.text.substring(0, 300);
      const enrichedDescription = `${visualDesc}. STORY MOMENT: "${storyExcerpt}". The ${genderDesc} protagonist is the main focus, actively participating in this exact scene with clear facial expressions and body language that matches what's happening in the story. Show the specific action and emotion from this moment.`;
      
      const imageRequest = {
        scene_description: enrichedDescription,
        story_context: storySegments.map(s => s.text).join(' '),
        character_description: hasUserAvatar ? 
          `The main character is a ${selectedAge}-year-old ${genderDesc} who looks like the storybook avatar provided. The ${genderDesc} should be clearly visible and central to the scene, showing emotions and actions from the story. Integrate naturally into the scene with the avatar's appearance.` :
          hasUserPhoto ? 
          `A ${selectedAge}-year-old ${genderDesc} protagonist who looks like the user photo. The ${genderDesc} should be the focus of the image, showing clear emotions and actions from the story moment. Realistic but child-friendly style.` : 
          `A ${selectedAge}-year-old ${genderDesc} as the main character, clearly visible and central to the scene, showing emotions and actions from the story`,
        style: selectedAge >= 10 ? 'realistic_children' : 'semi_realistic_children',
        has_user_photo: hasUserPhoto,
        has_user_avatar: hasUserAvatar,
        user_photo_base64: capturedPhoto?.base64 || null,
        user_avatar_url: capturedPhoto?.avatar_url || null,
        theme: selectedTheme,
        emotional_goal: selectedEmotion,
        child_age: selectedAge,
        gender: selectedGender
      };
      
      // Generate image using the storytelling service
      const imageResult = await storyService.generateStoryImage(sessionId, imageRequest);
      
      if (imageResult && (imageResult.imageUrl || imageResult.image_url)) {
        // Add the generated image to our images array
        const newImage = {
          id: `auto-${storySegment.index}-${Date.now()}`,
          url: imageResult.imageUrl || imageResult.image_url,
          prompt: imageResult.prompt || storySegment.text.substring(0, 100),
          timestamp: Date.now(),
          storySegmentIndex: storySegment.index,
          isAutoGenerated: true
        };
        
        setGeneratedImages(prev => [...prev, newImage]);
        
        console.log('✅ Auto-generated image successfully:', newImage.id);
        showNotification(t('autoImageGenerated'), 'success');
      }
    } catch (error) {
      console.warn('⚠️ Auto image generation failed, using enhanced SVG fallback:', error.message);
      
      // Generate enhanced SVG fallback directly
      const fallbackImage = {
        id: `fallback-${storySegment.index}-${Date.now()}`,
        url: await generateEnhancedSVGFallback(storySegment),
        prompt: storySegment.text.substring(0, 100),
        timestamp: Date.now(),
        storySegmentIndex: storySegment.index,
        isAutoGenerated: true,
        isFallback: true
      };
      
      setGeneratedImages(prev => [...prev, fallbackImage]);
      showNotification(t('localImageGenerated'), 'info');
    }
  };

  const showNotification = (message, type = 'info') => {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      color: white;
      font-weight: 500;
      z-index: 1000;
      max-width: 300px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideInRight 0.3s ease-out;
      background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#667eea'};
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);
  };

  const sendStoryDirection = async (direction) => {
    try {
      // Always try the story service (which now has proper fallbacks)
      const result = await storyService.sendEmotionFeedback(sessionId, {
        emotion: direction,
        confidence: 0.8,
        source: 'story_direction',
        timestamp: Date.now()
      });
      
      console.log('Story direction sent:', direction, result);
      
      // Show feedback to user
      const directionLabel = storyDirections.find(d => d.id === direction)?.label || direction;
      showNotification(
        language === 'en' 
          ? `Story direction: ${directionLabel}` 
          : `Dirección de historia: ${directionLabel}`
      );
      
      // If there's an adaptation, show it
      if (result.adaptation && result.adaptation.action_type !== 'no_action') {
        setTimeout(() => {
          showNotification(
            language === 'en'
              ? `Story adapted: ${result.adaptation.reason}`
              : `Historia adaptada: ${result.adaptation.reason}`
          );
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending story direction:', error);
      const directionLabel = storyDirections.find(d => d.id === direction)?.label || direction;
      showNotification(
        language === 'en'
          ? `Story direction: ${directionLabel} (local mode)`
          : `Dirección de historia: ${directionLabel} (modo local)`
      );
    }
  };

  const handleEmotionDetected = async (emotionData) => {
    console.log('🎭 Emotion detected from photo:', emotionData);
    
    setDetectedEmotion(emotionData);
    
    try {
      const result = await storyService.sendEmotionFeedback(sessionId, {
        emotion: emotionData.emotion,
        confidence: emotionData.confidence,
        source: emotionData.source,
        timestamp: Date.now()
      });
      
      showNotification(
        language === 'en' 
          ? `AI detected: ${emotionData.label} (${Math.round(emotionData.confidence * 100)}%)` 
          : `IA detectó: ${emotionData.label} (${Math.round(emotionData.confidence * 100)}%)`
      );
      
      if (result.adaptation && result.adaptation.action_type !== 'no_action') {
        setTimeout(() => {
          showNotification(
            language === 'en'
              ? `Story adapted: ${result.adaptation.reason}`
              : `Historia adaptada: ${result.adaptation.reason}`
          );
        }, 1500);
      }
      
      // Auto-generate next segment with emotion adaptation
      if (storySegments.length > 0) {
        setTimeout(() => generateStorySegment(false), 2000);
      }
    } catch (error) {
      console.error('Error sending detected emotion:', error);
      showNotification(
        language === 'en'
          ? `AI detected: ${emotionData.label} (local mode)`
          : `IA detectó: ${emotionData.label} (modo local)`
      );
    }
  };

  // Get current text for audio controls
  const getCurrentText = () => {
    if (storySegments.length > 0) {
      return storySegments[storySegments.length - 1].text;
    }
    return '';
  };

  const storyDirections = [
    { 
      id: 'adventure', 
      icon: '🗺️', 
      label: language === 'en' ? 'Adventure' : 'Aventura',
      description: language === 'en' ? 'More exciting and bold' : 'Más emocionante y audaz'
    },
    { 
      id: 'mystery', 
      icon: '🔍', 
      label: language === 'en' ? 'Mystery' : 'Misterio',
      description: language === 'en' ? 'Intriguing and curious' : 'Intrigante y curioso'
    },
    { 
      id: 'friendship', 
      icon: '👫', 
      label: language === 'en' ? 'Friendship' : 'Amistad',
      description: language === 'en' ? 'Warm and heartfelt' : 'Cálido y emotivo'
    },
    { 
      id: 'magic', 
      icon: '✨', 
      label: language === 'en' ? 'Magic' : 'Magia',
      description: language === 'en' ? 'Fantastical and wonderful' : 'Fantástico y maravilloso'
    }
  ];

  const getEmotionLabel = (emotion) => {
    return t(`emotions.${emotion}`) || emotion;
  };

  const getThemeLabel = (theme) => {
    return t(`themes.${theme}`) || theme;
  };



  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-screen">
      {/* Main story area */}
      <div className="lg:col-span-2 bg-white/5 backdrop-blur-xl rounded-3xl p-6 border border-white/10 shadow-2xl flex flex-col min-h-[80vh]"
           style={{
             background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
             boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
           }}>
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-white">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">{language === 'en' ? 'Active session' : 'Sesión activa'}</span>
            </div>
            <div className="text-white text-sm">
              {formatDuration(sessionDuration)}
            </div>
          </div>
          
          {/* User avatar in header */}
          {capturedPhoto && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center justify-center gap-3 mb-4"
            >
              <img
                src={capturedPhoto.avatar_url || capturedPhoto.url || capturedPhoto}
                alt="Tu avatar"
                className="w-12 h-12 object-cover rounded-full border-2 border-white border-opacity-50 shadow-lg"
              />
              <div className="text-left">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent">{t('yourStory')}</h1>
                <p className="text-slate-200/90 text-sm font-medium">{language === 'en' ? 'Starring you' : 'Protagonizada por ti'}</p>
              </div>
            </motion.div>
          )}
          
          {!capturedPhoto && (
            <>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent mb-2">{t('yourStory')}</h1>
              <p className="text-slate-200/90 font-medium">{t('appSubtitle')}</p>
            </>
          )}
        </div>

        {/* Story content */}
        <div 
          ref={storyContentRef}
          className="story-content flex-1 bg-white/5 rounded-2xl p-6 overflow-y-auto mb-6 max-h-[60vh] border border-white/5"
          style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
            boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.1)',
          }}
        >
          {storySegments.length === 0 ? (
            <div className="text-center text-white opacity-70 py-12">
              <div className="text-4xl mb-4">📖</div>
              <p className="text-lg mb-2">{t('storyWillBeginHere')}</p>
              <p className="text-sm">{t('clickToStart')}</p>
            </div>
          ) : (
            <div className="space-y-4 pb-4">
              {storySegments.map((segment, index) => {
                const segmentImage = generatedImages.find(img => img.storySegmentIndex === index);
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="bg-white/8 rounded-xl p-4 border-l-4 border-gradient-to-b from-blue-400 to-indigo-500 backdrop-blur-sm"
                    style={{
                      background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)',
                      borderLeft: '4px solid transparent',
                      borderImage: 'linear-gradient(to bottom, #60a5fa, #6366f1) 1',
                      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                    }}
                  >
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg"
                           style={{
                             boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
                           }}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-white leading-relaxed">{segment.text}</p>
                      </div>
                    </div>
                    
                    {segmentImage && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="mt-4"
                      >
                        <img
                          src={segmentImage.url}
                          alt="Ilustración de la historia"
                          className="w-full max-w-sm mx-auto rounded-xl shadow-lg border-2 border-white border-opacity-20"
                          onError={(e) => {
                            e.target.src = '/static/images/demo_magical_scene.jpg';
                          }}
                        />
                        <p className="text-center text-white text-xs opacity-70 mt-2">
                          {segmentImage.isAutoGenerated ? t('generatedAutomatically') : 'Ilustración AI'}
                        </p>
                      </motion.div>
                    )}
                  </motion.div>
                );
              })}
              
              {/* Scroll indicator */}
              {storySegments.length > 2 && (
                <div className="text-center py-2">
                  <p className="text-white text-xs opacity-50">
                    📖 {storySegments.length} {language === 'en' ? 'chapters • Scroll to see more' : 'capítulos • Desliza para ver más'}
                  </p>
                </div>
              )}
            </div>
          )}

          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-white">{t('generating')}</p>
            </div>
          )}
        </div>

        {/* Story controls */}
        <div className="space-y-3">
          <div className="flex gap-3">
            <motion.button
              className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-3 px-6 rounded-xl font-semibold shadow-xl border border-white/20"
              onClick={() => generateStorySegment(false)}
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                boxShadow: '0 15px 35px -5px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
              }}
            >
              {storySegments.length === 0 ? `✨ ${t('startMagicalStory')}` : `📖 ${t('newChapter')}`}
            </motion.button>
            
            {storySegments.length > 0 && (
              <motion.button
                className="bg-gradient-to-r from-amber-500 to-orange-600 text-white py-3 px-6 rounded-xl font-semibold shadow-xl border border-white/20"
                onClick={() => generateStorySegment(true)}
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  boxShadow: '0 15px 35px -5px rgba(245, 158, 11, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
                }}
              >
                🎬 {language === 'en' ? 'Finish Story' : 'Terminar Cuento'}
              </motion.button>
            )}
            
            <motion.button
              className="bg-white/10 text-white/90 py-3 px-6 rounded-xl font-semibold border border-white/20 hover:bg-white/20 hover:text-white transition-all duration-300"
              onClick={onEndSession}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
              }}
            >
              🏠 {t('backToWelcome')}
            </motion.button>
          </div>

        </div>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* Audio Controls */}
        <AudioControls
          sessionId={sessionId}
          storyService={storyService}
          currentText={getCurrentText()}
          isPlaying={isPlaying}
          setIsPlaying={setIsPlaying}
        />

        {/* AI Emotion Detection */}
        <EmotionDetector 
          onEmotionDetected={handleEmotionDetected}
          capturedPhoto={capturedPhoto}
        />

        {/* Story Direction */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 shadow-xl"
             style={{
               background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
               boxShadow: '0 15px 35px -5px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
             }}>
          <h3 className="text-white/95 font-semibold mb-4 flex items-center gap-2 tracking-wide">
            🎭 {language === 'en' ? 'How should the story continue?' : '¿Cómo quieres que avance la historia?'}
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {storyDirections.map((direction) => (
              <motion.button
                key={direction.id}
                className="bg-white/10 text-white/90 p-3 rounded-xl text-center hover:bg-white/20 hover:text-white transition-all duration-300 border border-white/10 hover:border-white/20"
                style={{
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                }}
                onClick={() => sendStoryDirection(direction.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title={direction.description}
              >
                <div className="text-xl mb-1">{direction.icon}</div>
                <div className="text-xs font-medium">{direction.label}</div>
              </motion.button>
            ))}
          </div>
          <p className="text-white text-xs opacity-60 mt-3 text-center">
            {language === 'en' 
              ? 'Choose how you want the next part to develop' 
              : 'Elige cómo quieres que se desarrolle la siguiente parte'
            }
          </p>
        </div>

        {/* Profile info */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 shadow-xl"
             style={{
               background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
               boxShadow: '0 15px 35px -5px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
             }}>
          <h3 className="text-white/95 font-semibold mb-4 flex items-center gap-2 tracking-wide">
            👤 {language === 'en' ? 'Your Profile' : 'Tu Perfil'}
          </h3>
          
          {/* User avatar section */}
          {capturedPhoto && (
            <div className="text-center mb-4">
              <div className="relative inline-block">
                <img
                  src={capturedPhoto.avatar_url || capturedPhoto.url || capturedPhoto}
                  alt="Tu avatar"
                  className="w-16 h-16 object-cover rounded-full border-3 border-white border-opacity-50 shadow-lg"
                />
              </div>
              <p className="text-white text-xs opacity-70 mt-2">
                {language === 'en' ? 'Story protagonist' : 'Protagonista de la historia'}
              </p>
              {detectedEmotion && (
                <div className="mt-2 bg-white bg-opacity-20 rounded-lg px-2 py-1">
                  <p className="text-white text-xs font-semibold">
                    {language === 'en' ? 'AI Detected:' : 'IA Detectó:'} {detectedEmotion.label}
                  </p>
                  <div className="w-full bg-white bg-opacity-30 rounded-full h-1 mt-1">
                    <div 
                      className="bg-green-400 h-1 rounded-full transition-all duration-500"
                      style={{ width: `${detectedEmotion.confidence * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
          
          <div className="space-y-3 text-white text-sm">
            <div className="flex justify-between">
              <span className="opacity-70">{language === 'en' ? 'Age' : 'Edad'}</span>
              <span className="font-medium">{selectedAge} {language === 'en' ? 'years old' : 'años'}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-70">{language === 'en' ? 'Goal' : 'Objetivo'}</span>
              <span className="font-medium">{getEmotionLabel(selectedEmotion)}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-70">{language === 'en' ? 'Theme' : 'Tema'}</span>
              <span className="font-medium">{getThemeLabel(selectedTheme)}</span>
            </div>
          </div>
        </div>


      </div>
    </div>
  );
};

// Add notification animation styles and scrollbar styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOutRight {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }

  /* Custom scrollbar styles */
  .story-content::-webkit-scrollbar {
    width: 8px;
  }

  .story-content::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }

  .story-content::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    transition: background 0.3s ease;
  }

  .story-content::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }

  /* Smooth scrolling */
  .story-content {
    scroll-behavior: smooth;
  }
`;

// Add styles to document head if not already added
if (!document.head.querySelector('#notification-styles')) {
  notificationStyles.id = 'notification-styles';
  document.head.appendChild(notificationStyles);
}

export default ModernStoryArea;