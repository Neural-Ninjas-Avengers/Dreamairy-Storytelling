import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';
import { EmotionAnalysisService } from '../services/EmotionAnalysisService';

const EmotionDetector = ({ onEmotionDetected, capturedPhoto, triggerAnalysis = false }) => {
  const { language } = useLanguage();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [analysisDetails, setAnalysisDetails] = useState(null);
  
  const emotionService = useRef(new EmotionAnalysisService()).current;

  // Analyze emotion from photo using AWS Rekognition
  const analyzeEmotionFromPhoto = useCallback(async () => {
    if (!capturedPhoto?.url) {
      console.warn('No photo available for emotion analysis');
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);

    try {
      console.log('🔍 Starting AWS Rekognition emotion analysis...');
      
      const response = await fetch('http://localhost:3001/api/v1/detect-emotion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_base64: capturedPhoto.url })
      });
      
      const data = await response.json();
      
      let analysisResult;
      if (data.success && data.emotion) {
        analysisResult = {
          emotion: data.emotion,
          label: data.label,
          icon: data.icon,
          confidence: data.confidence,
          storyInfluence: data.story_influence,
          source: 'aws_rekognition',
          processingDetails: {
            facialFeaturesDetected: true,
            emotionalPatternsFound: data.all_emotions?.length || 1,
            analysisMethod: 'aws_rekognition'
          }
        };
      } else {
        analysisResult = await emotionService.analyzeEmotionFromPhoto(capturedPhoto.url, language);
      }
      
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

  // Trigger analysis when requested
  React.useEffect(() => {
    if (triggerAnalysis && capturedPhoto?.url) {
      analyzeEmotionFromPhoto();
    }
  }, [triggerAnalysis, capturedPhoto, analyzeEmotionFromPhoto]);



  if (!capturedPhoto?.url) {
    return null;
  }

  return (
    <div>
      <AnimatePresence mode="wait">
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-white text-xs mt-2"
          >
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg">{detectedEmotion.icon}</span>
              <span>{detectedEmotion.label}</span>
              <span className="opacity-70">({Math.round(confidence * 100)}%)</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EmotionDetector;