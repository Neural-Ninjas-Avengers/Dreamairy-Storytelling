import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';
import { EmotionAnalysisService } from '../services/EmotionAnalysisService';

const EmotionDetector = ({ onEmotionDetected, capturedPhoto }) => {
  const { t, language } = useLanguage();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [analysisDetails, setAnalysisDetails] = useState(null);
  
  // Initialize emotion analysis service
  const emotionService = useRef(new EmotionAnalysisService()).current;

  // Analyze emotion from photo using advanced AI simulation
  const analyzeEmotionFromPhoto = useCallback(async () => {
    if (!capturedPhoto?.url) {
      console.warn('No photo available for emotion analysis');
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);

    try {
      console.log('🔍 Starting advanced emotion analysis from photo...');
      
      // Use the emotion analysis service
      const analysisResult = await emotionService.analyzeEmotionFromPhoto(
        capturedPhoto.url, 
        language
      );
      
      // Update state with results
      setDetectedEmotion({
        id: analysisResult.emotion,
        label: analysisResult.label,
        icon: analysisResult.icon,
        storyInfluence: analysisResult.storyInfluence
      });
      setConfidence(analysisResult.confidence);
      setAnalysisDetails(analysisResult.processingDetails);
      setShowResults(true);
      
      console.log('✅ Advanced emotion analysis completed:', analysisResult);
      
      // Call callback with detected emotion
      if (onEmotionDetected) {
        onEmotionDetected({
          emotion: analysisResult.emotion,
          label: analysisResult.label,
          confidence: analysisResult.confidence,
          source: analysisResult.source,
          storyInfluence: analysisResult.storyInfluence
        });
      }
      
    } catch (error) {
      console.error('❌ Error in advanced emotion analysis:', error);
      
      // Use service fallback
      const fallbackResult = emotionService.getFallbackEmotion(language);
      
      setDetectedEmotion({
        id: fallbackResult.emotion,
        label: fallbackResult.label,
        icon: fallbackResult.icon,
        storyInfluence: fallbackResult.storyInfluence
      });
      setConfidence(fallbackResult.confidence);
      setAnalysisDetails(fallbackResult.processingDetails);
      setShowResults(true);
      
      if (onEmotionDetected) {
        onEmotionDetected({
          emotion: fallbackResult.emotion,
          label: fallbackResult.label,
          confidence: fallbackResult.confidence,
          source: fallbackResult.source,
          storyInfluence: fallbackResult.storyInfluence
        });
      }
    } finally {
      setIsAnalyzing(false);
    }
  }, [capturedPhoto, language, onEmotionDetected, emotionService]);

  const resetAnalysis = useCallback(() => {
    setDetectedEmotion(null);
    setConfidence(0);
    setShowResults(false);
    setAnalysisDetails(null);
  }, []);

  if (!capturedPhoto?.url) {
    return (
      <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-4 border border-white border-opacity-20 shadow-xl">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          🤖 {language === 'en' ? 'AI Emotion Detection' : 'Detección de Emociones IA'}
        </h3>
        <div className="text-center text-white opacity-70">
          <div className="text-3xl mb-2">📸</div>
          <p className="text-sm">
            {language === 'en' 
              ? 'Take a photo to analyze your emotions' 
              : 'Toma una foto para analizar tus emociones'
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-4 border border-white border-opacity-20 shadow-xl">
      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
        🤖 {language === 'en' ? 'AI Emotion Detection' : 'Detección de Emociones IA'}
      </h3>

      {/* Photo preview */}
      <div className="text-center mb-4">
        <img
          src={capturedPhoto.url}
          alt="Photo for analysis"
          className="w-16 h-16 object-cover rounded-full border-2 border-white border-opacity-30 mx-auto shadow-lg"
        />
      </div>

      <AnimatePresence mode="wait">
        {!showResults && !isAnalyzing && (
          <motion.div
            key="analyze-button"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-center"
          >
            <motion.button
              className="bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 px-6 rounded-xl font-semibold shadow-lg w-full"
              onClick={analyzeEmotionFromPhoto}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span className="flex items-center justify-center gap-2">
                <span className="text-lg">🔍</span>
                <span>
                  {language === 'en' ? 'Analyze My Emotion' : 'Analizar Mi Emoción'}
                </span>
              </span>
            </motion.button>
            <p className="text-white text-xs opacity-60 mt-2">
              {language === 'en' 
                ? 'AI will analyze your facial expression' 
                : 'La IA analizará tu expresión facial'
              }
            </p>
          </motion.div>
        )}

        {isAnalyzing && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center"
          >
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-xl">
              <motion.div
                className="text-3xl mb-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                🤖
              </motion.div>
              <p className="font-semibold mb-1">
                {language === 'en' ? 'Analyzing your emotion...' : 'Analizando tu emoción...'}
              </p>
              <p className="text-sm opacity-90">
                {language === 'en' 
                  ? 'AI is reading your facial expression' 
                  : 'La IA está leyendo tu expresión facial'
                }
              </p>
              <div className="mt-3">
                <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
                  <motion.div
                    className="bg-white h-2 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 2, ease: "easeInOut" }}
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {showResults && detectedEmotion && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-3"
          >
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-4 rounded-xl text-center">
              <div className="text-4xl mb-2">{detectedEmotion.icon}</div>
              <p className="font-bold text-lg mb-1">
                {language === 'en' ? 'Emotion Detected!' : '¡Emoción Detectada!'}
              </p>
              <p className="text-xl font-semibold mb-2">{detectedEmotion.label}</p>
              <div className="flex items-center justify-center gap-2 text-sm">
                <span>{language === 'en' ? 'Confidence:' : 'Confianza:'}</span>
                <span className="font-bold">{Math.round(confidence * 100)}%</span>
              </div>
              <div className="mt-2 w-full bg-white bg-opacity-20 rounded-full h-2">
                <motion.div
                  className="bg-white h-2 rounded-full"
                  initial={{ width: "0%" }}
                  animate={{ width: `${confidence * 100}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </div>
            </div>

            <div className="flex gap-2">
              <motion.button
                className="flex-1 bg-white bg-opacity-20 text-white py-2 px-4 rounded-xl text-sm font-semibold"
                onClick={analyzeEmotionFromPhoto}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                🔄 {language === 'en' ? 'Analyze Again' : 'Analizar Otra Vez'}
              </motion.button>
              <motion.button
                className="flex-1 bg-gradient-to-r from-purple-500 to-pink-600 text-white py-2 px-4 rounded-xl text-sm font-semibold"
                onClick={resetAnalysis}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ✨ {language === 'en' ? 'Apply to Story' : 'Aplicar al Cuento'}
              </motion.button>
            </div>

            {analysisDetails && (
              <div className="bg-white bg-opacity-10 rounded-lg p-2 text-xs text-white">
                <p className="font-semibold mb-1">
                  {language === 'en' ? 'Analysis Details:' : 'Detalles del Análisis:'}
                </p>
                <div className="space-y-1 opacity-80">
                  <p>• {language === 'en' ? 'Facial features:' : 'Características faciales:'} {analysisDetails.facialFeaturesDetected ? '✓' : '✗'}</p>
                  <p>• {language === 'en' ? 'Patterns found:' : 'Patrones encontrados:'} {analysisDetails.emotionalPatternsFound}</p>
                  <p>• {language === 'en' ? 'Method:' : 'Método:'} {analysisDetails.analysisMethod === 'deep_learning_cnn' ? 'Deep Learning CNN' : 'Fallback'}</p>
                </div>
              </div>
            )}

            <p className="text-white text-xs opacity-60 text-center">
              {language === 'en' 
                ? 'This emotion will influence how your story develops' 
                : 'Esta emoción influirá en cómo se desarrolla tu historia'
              }
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EmotionDetector;