import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const AIImageGenerator = ({ sessionId, storytellingService, storyContext, capturedPhoto, onImageGenerated }) => {
  const { t } = useLanguage();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [availableStyles, setAvailableStyles] = useState({});
  const [selectedStyle, setSelectedStyle] = useState('children_book');
  const [hasUserPhoto, setHasUserPhoto] = useState(false);
  const [userPhotoData, setUserPhotoData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAvailableStyles();
    // Don't check user photo here, let the capturedPhoto useEffect handle it
  }, [sessionId]);

  // Update photo data when capturedPhoto changes
  useEffect(() => {
    console.log('AIImageGenerator - capturedPhoto changed:', capturedPhoto);
    if (capturedPhoto && capturedPhoto.url) {
      console.log('AIImageGenerator - Setting hasUserPhoto to true');
      setHasUserPhoto(true);
      setUserPhotoData(capturedPhoto.url);
      console.log('Using captured photo for AI generation:', capturedPhoto);
    } else {
      console.log('AIImageGenerator - No captured photo, checking backend');
      // If no captured photo, check backend
      checkUserPhoto();
    }
  }, [capturedPhoto]);

  const loadAvailableStyles = async () => {
    try {
      const result = await storytellingService.getAvailableImageStyles();
      setAvailableStyles(result.styles);
      setSelectedStyle(result.default_style);
    } catch (error) {
      console.error('Failed to load image styles:', error);
    }
  };

  const checkUserPhoto = async () => {
    try {
      const result = await storytellingService.getUserPhoto(sessionId);
      setHasUserPhoto(result.has_photo);
      if (result.has_photo && result.photo_data) {
        // Convert base64 to data URL for display
        setUserPhotoData(`data:image/jpeg;base64,${result.photo_data}`);
      }
    } catch (error) {
      console.error('Failed to check user photo:', error);
      setHasUserPhoto(false);
      setUserPhotoData(null);
    }
  };

  const generateImage = async () => {
    if (!storyContext || !storyContext.text) {
      setError(t('noStoryContext'));
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const imageRequest = {
        story_context: storyContext.text,
        character_description: hasUserPhoto 
          ? `A ${storyContext.childAge || 7}-year-old child protagonist who looks like the user photo, realistic but child-friendly, naturally integrated into the story` 
          : `Realistic but child-friendly characters appropriate for a ${storyContext.childAge || 7}-year-old child`,
        scene_description: extractSceneFromStory(storyContext.text),
        style: (storyContext.childAge || 7) >= 10 ? 'realistic_children' : 'semi_realistic_children',
        has_user_photo: hasUserPhoto,
        child_age: storyContext.childAge || 7,
        theme: storyContext.theme || 'fantasy'
      };

      const result = await storytellingService.generateStoryImage(sessionId, imageRequest);
      
      setGeneratedImage(result);
      onImageGenerated && onImageGenerated(result);
      
    } catch (error) {
      console.error('Failed to generate image:', error);
      setError(t('errorGeneratingImage'));
    } finally {
      setIsGenerating(false);
    }
  };

  const extractSceneFromStory = (storyText) => {
    // Extract key visual elements from the story text
    const text = storyText.toLowerCase();
    
    if (text.includes('bosque') || text.includes('árbol')) {
      return 'un bosque mágico con árboles altos y luz filtrada';
    } else if (text.includes('océano') || text.includes('mar') || text.includes('playa')) {
      return 'una escena oceánica con olas brillantes y cielo azul';
    } else if (text.includes('castillo') || text.includes('palacio')) {
      return 'un castillo mágico con torres y banderas ondeando';
    } else if (text.includes('animal') || text.includes('conejo') || text.includes('búho')) {
      return 'una escena con animales amigables en un entorno natural';
    } else if (text.includes('estrella') || text.includes('luna') || text.includes('noche')) {
      return 'una escena nocturna mágica con estrellas brillantes';
    } else {
      return 'una escena mágica y colorida apropiada para niños';
    }
  };

  const regenerateImage = () => {
    setGeneratedImage(null);
    generateImage();
  };

  // Debug log
  console.log('AIImageGenerator render - hasUserPhoto:', hasUserPhoto, 'userPhotoData:', userPhotoData, 'capturedPhoto:', capturedPhoto);

  return (
    <div className="space-y-4">
      <AnimatePresence mode="wait">
        {!generatedImage && !isGenerating && (
          <motion.div
            key="generate-controls"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {/* Style Selection */}
            <div className="space-y-2">
              <h4 className="text-white text-sm font-semibold">{t('illustrationStyle')}</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(availableStyles).map(([key, style]) => (
                  <motion.button
                    key={key}
                    className={`p-3 rounded-xl text-xs transition-all duration-300 ${
                      selectedStyle === key
                        ? 'bg-gradient-to-r from-pink-500 to-indigo-600 text-white shadow-lg'
                        : 'bg-white bg-opacity-10 text-white hover:bg-opacity-20'
                    }`}
                    onClick={() => setSelectedStyle(key)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="font-semibold">{style.name}</div>
                    <div className="opacity-80 mt-1">{style.description}</div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* User Photo Preview */}
            {hasUserPhoto && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-green-500 bg-opacity-20 text-green-100 p-4 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  {userPhotoData ? (
                    <div className="relative">
                      <img
                        src={userPhotoData}
                        alt="Tu foto para AI"
                        className="w-16 h-16 object-cover rounded-xl border-2 border-green-300 shadow-lg"
                      />
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-400 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    </div>
                  ) : (
                    <div className="w-16 h-16 bg-green-400 bg-opacity-30 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">👤</span>
                    </div>
                  )}
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{t('photoReadyForAI')}</div>
                    <div className="opacity-80 text-xs mt-1">
                      {t('appearAsMainCharacter')}
                    </div>
                  </div>
                </div>
                
                {/* Preview of what will be generated */}
                <div className="mt-3 pt-3 border-t border-green-300 border-opacity-30">
                  <div className="text-xs opacity-90">
                    <div className="font-semibold mb-1">Se generará:</div>
                    <div className="flex items-center gap-2">
                      <span>🎨</span>
                      <span>{t('illustrationWithYourFace')}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span>📖</span>
                      <span>Basada en: "{storyContext?.text?.substring(0, 50)}..."</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* No Photo Message */}
            {!hasUserPhoto && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-blue-500 bg-opacity-20 text-blue-100 p-3 rounded-xl text-xs flex items-center gap-2"
              >
                <span className="text-lg">ℹ️</span>
                <div>
                  <div className="font-semibold">{t('noPersonalizedPhoto')}</div>
                  <div className="opacity-80">{t('genericCharacterUsed')}</div>
                </div>
              </motion.div>
            )}

            {/* Generate Button */}
            <motion.button
              className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 px-6 rounded-2xl font-semibold shadow-lg flex items-center justify-center gap-2"
              onClick={generateImage}
              disabled={!storyContext}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span className="text-xl">🎨</span>
              <span>{t('generateAIIllustration')}</span>
            </motion.button>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-500 bg-opacity-20 text-red-100 p-3 rounded-xl text-xs"
              >
                {error}
              </motion.div>
            )}
          </motion.div>
        )}

        {isGenerating && (
          <motion.div
            key="generating"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center space-y-4"
          >
            <div className="relative">
              <motion.div
                className="w-32 h-32 mx-auto bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center"
                animate={{ 
                  rotate: 360,
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  rotate: { duration: 2, repeat: Infinity, ease: "linear" },
                  scale: { duration: 1, repeat: Infinity }
                }}
              >
                <span className="text-4xl">🎨</span>
              </motion.div>
            </div>
            
            <div className="space-y-2">
              <h3 className="text-white font-semibold">{t('generatingAIIllustration')}</h3>
              <p className="text-white text-sm opacity-70">
                {t('creatingMagicalImage')}
              </p>
              <div className="flex justify-center space-x-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-white rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ 
                      duration: 1.5, 
                      repeat: Infinity, 
                      delay: i * 0.2 
                    }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {generatedImage && (
          <motion.div
            key="generated-image"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="space-y-4"
          >
            <div className="relative">
              <img
                src={generatedImage.imageUrl || generatedImage.image_url}
                alt={t('aiGeneratedIllustration')}
                className="w-full max-w-md mx-auto rounded-2xl shadow-2xl border-4 border-white border-opacity-20"
                onError={(e) => {
                  e.target.src = '/static/images/demo_magical_scene.jpg';
                }}
              />
              
              {/* Image Info Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-3 rounded-b-2xl">
                <div className="text-xs space-y-1">
                  <div className="flex justify-between">
                    <span>Estilo:</span>
                    <span className="font-semibold">{availableStyles[generatedImage.style_applied]?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tiempo:</span>
                    <span className="font-semibold">{generatedImage.generation_time.toFixed(1)}s</span>
                  </div>
                  {generatedImage.has_user_character && (
                    <div className="flex justify-between text-green-300">
                      <span>Personaje:</span>
                      <span className="font-semibold">¡Tú apareces! 👤</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-center">
              <motion.button
                className="bg-white bg-opacity-20 text-white py-2 px-4 rounded-xl font-semibold text-sm"
                onClick={regenerateImage}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                🔄 Regenerar
              </motion.button>
              
              <motion.button
                className="bg-gradient-to-r from-green-500 to-blue-600 text-white py-2 px-4 rounded-xl font-semibold text-sm"
                onClick={() => {
                  // Download or share functionality could go here
                  console.log('Save image:', generatedImage.imageUrl || generatedImage.image_url);
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                💾 Guardar
              </motion.button>
            </div>

            <p className="text-white text-xs opacity-80 text-center">
              {t('aiGeneratedIllustration')} {generatedImage.has_user_character && t('youAppearAsMainCharacter')}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AIImageGenerator;