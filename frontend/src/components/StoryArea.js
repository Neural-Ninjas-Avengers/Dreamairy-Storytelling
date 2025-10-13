import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Palette, Home } from 'lucide-react';

const StoryArea = ({ storyService, sessionId, selectedAge, onEndSession }) => {
  const [storySegments, setStorySegments] = useState([]);
  const [currentIllustration, setCurrentIllustration] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [narratorAvatar, setNarratorAvatar] = useState('🌟');

  const avatars = {
    3: '🐻', 4: '🦊', 5: '🐸', 
    6: '🌟', 7: '🚀', 8: '🎭'
  };

  useEffect(() => {
    setNarratorAvatar(avatars[selectedAge] || '🌟');
  }, [selectedAge]);

  useEffect(() => {
    if (storyService && sessionId) {
      // Listen for story segments
      storyService.onMessage((message) => {
        if (message.type === 'story_segment') {
          setStorySegments(prev => [...prev, message.segment]);
          if (message.segment.illustration) {
            setCurrentIllustration(message.segment.illustration);
          }
          setIsLoading(false);
        }
      });

      // Auto-start the first story segment
      requestStorySegment();
    }
  }, [storyService, sessionId]);

  const requestStorySegment = async () => {
    if (!storyService || !sessionId) return;
    
    setIsLoading(true);
    const action = storySegments.length === 0 ? 'start' : 'continue';
    
    try {
      await storyService.requestStory(sessionId, {
        action: action,
        theme: 'animals'
      });
    } catch (error) {
      console.error('Failed to request story segment:', error);
      setIsLoading(false);
    }
  };

  const sendEmotion = async (emotion) => {
    if (!storyService || !sessionId) return;
    
    try {
      await storyService.sendEmotion(sessionId, {
        emotion: emotion,
        confidence: 0.8,
        intensity: 0.7
      });
    } catch (error) {
      console.error('Failed to send emotion:', error);
    }
  };

  const renderIllustration = () => {
    if (!currentIllustration) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-forest-600">
          <Palette size={64} className="mb-4 opacity-50" />
          <p className="text-lg font-medium">Aquí aparecerá una hermosa ilustración</p>
        </div>
      );
    }

    if (currentIllustration.type === 'mock_illustration') {
      if (currentIllustration.mock_image_data) {
        return (
          <div 
            className="w-full h-full flex items-center justify-center"
            dangerouslySetInnerHTML={{ __html: currentIllustration.mock_image_data }}
          />
        );
      } else {
        const themeEmojis = {
          'animals': '🐾',
          'adventure': '🗺️',
          'friendship': '👫',
          'magic': '✨',
          'family': '👨‍👩‍👧‍👦',
          'nature': '🌳'
        };
        
        return (
          <div className="flex flex-col items-center justify-center h-full text-forest-600">
            <div className="text-6xl mb-4">
              {themeEmojis[currentIllustration.theme] || '🎨'}
            </div>
            <h3 className="text-xl font-bold mb-2 capitalize">
              {currentIllustration.theme}
            </h3>
            <p className="text-center italic">
              {currentIllustration.placeholder_text}
            </p>
          </div>
        );
      }
    }

    return (
      <div className="flex flex-col items-center justify-center h-full text-forest-600">
        <div className="text-6xl mb-4">🎨</div>
        <h3 className="text-xl font-bold">Ilustración Mágica</h3>
        <p className="text-center italic">Una hermosa ilustración acompaña esta parte de la historia</p>
      </div>
    );
  };

  return (
    <motion.div
      className="glass-card p-6 text-forest-900"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <motion.div
        className="text-center mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="font-fredoka text-3xl text-forest-800 mb-2">
          Tu Historia Mágica
        </h2>
        <motion.div
          className="text-4xl"
          animate={{ rotate: [0, 10, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatType: 'reverse' }}
        >
          {narratorAvatar}
        </motion.div>
      </motion.div>

      {/* Story Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 min-h-96">
        {/* Illustration */}
        <motion.div
          className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 shadow-inner"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          {renderIllustration()}
        </motion.div>

        {/* Story Text */}
        <motion.div
          className="bg-white/80 rounded-2xl p-6 shadow-inner overflow-y-auto max-h-96"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          {storySegments.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-forest-600">
              <BookOpen size={48} className="mb-4 opacity-50" />
              <p className="text-lg font-medium text-center">
                {isLoading ? 'Creando tu historia mágica...' : 'Tu historia mágica comenzará aquí...'}
              </p>
              {isLoading && (
                <motion.div
                  className="mt-4 w-8 h-8 border-4 border-forest-300 border-t-forest-600 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {storySegments.map((segment, index) => (
                <motion.div
                  key={index}
                  className="text-lg leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {segment.text}
                </motion.div>
              ))}
              {isLoading && (
                <motion.div
                  className="flex items-center justify-center py-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <motion.div
                    className="w-6 h-6 border-2 border-forest-300 border-t-forest-600 rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                  <span className="ml-2 text-forest-600">Continuando la historia...</span>
                </motion.div>
              )}
            </div>
          )}
        </motion.div>
      </div>

      {/* Controls */}
      <motion.div
        className="text-center space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        {/* Main Actions */}
        <div className="flex gap-4 justify-center flex-wrap">
          <motion.button
            className="btn-primary"
            onClick={requestStorySegment}
            disabled={isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isLoading ? 'Creando...' : 'Continuar Historia'}
          </motion.button>
          
          <motion.button
            className="btn-secondary flex items-center gap-2"
            onClick={onEndSession}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Home size={20} />
            Terminar Historia
          </motion.button>
        </div>

        {/* Emotion Feedback */}
        <div className="bg-white/60 rounded-2xl p-4">
          <p className="text-forest-700 font-medium mb-3">¿Cómo te sientes?</p>
          <div className="flex gap-3 justify-center flex-wrap">
            {[
              { emotion: 'joy', emoji: '😄', label: 'Feliz' },
              { emotion: 'calm', emoji: '😌', label: 'Tranquilo' },
              { emotion: 'excitement', emoji: '🤩', label: 'Emocionado' },
              { emotion: 'boredom', emoji: '😴', label: 'Aburrido' }
            ].map((item) => (
              <motion.button
                key={item.emotion}
                className="bg-white rounded-full p-3 shadow-md hover:shadow-lg transition-all duration-300"
                onClick={() => sendEmotion(item.emotion)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                title={item.label}
              >
                <span className="text-2xl">{item.emoji}</span>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default StoryArea;