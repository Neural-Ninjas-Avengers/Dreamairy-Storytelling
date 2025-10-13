// BACKUP: Original React App with Fox Design
// This file contains the original React application with the forest/fox theme
// To restore the original React app, replace App.js content with this file

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import WelcomeScreen from './components/WelcomeScreen';
import ProfileSetup from './components/ProfileSetup';
import StoryArea from './components/StoryArea';
import ForestBackground from './components/ForestBackground';
import { StorytellingService } from './services/StorytellingService';

function App() {
  const [currentScreen, setCurrentScreen] = useState('welcome');
  const [selectedAge, setSelectedAge] = useState(6);
  const [selectedEmotion, setSelectedEmotion] = useState('entertain');
  const [storyService, setStoryService] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Initialize storytelling service
    const service = new StorytellingService();
    setStoryService(service);

    // Cleanup on unmount
    return () => {
      if (service) {
        service.disconnect();
      }
    };
  }, []);

  const handleStartStory = async () => {
    if (!storyService) return;

    try {
      const session = await storyService.createSession({
        age: selectedAge,
        preferences: ['animals', 'adventure'],
        emotional_goal: selectedEmotion
      });
      
      setSessionId(session.session_id);
      setCurrentScreen('story');
    } catch (error) {
      console.error('Failed to start story:', error);
      alert('No se pudo conectar al servidor. Por favor, verifica que esté ejecutándose.');
    }
  };

  const handleEndSession = async () => {
    if (storyService && sessionId) {
      try {
        await storyService.endSession(sessionId);
        setSessionId(null);
        setCurrentScreen('welcome');
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
  };

  const screenVariants = {
    initial: { opacity: 0, y: 50 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -50 }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-forest-800 via-forest-700 to-forest-900 relative overflow-hidden">
      <ForestBackground />
      
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <AnimatePresence mode="wait">
          {currentScreen === 'welcome' && (
            <motion.div
              key="welcome"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.5 }}
              className="w-full max-w-4xl"
            >
              <WelcomeScreen
                selectedEmotion={selectedEmotion}
                onEmotionSelect={setSelectedEmotion}
                onStartStory={() => setCurrentScreen('profile')}
              />
            </motion.div>
          )}

          {currentScreen === 'profile' && (
            <motion.div
              key="profile"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.5 }}
              className="w-full max-w-2xl"
            >
              <ProfileSetup
                selectedAge={selectedAge}
                selectedEmotion={selectedEmotion}
                onAgeSelect={setSelectedAge}
                onEmotionSelect={setSelectedEmotion}
                onStartStory={handleStartStory}
                onBack={() => setCurrentScreen('welcome')}
              />
            </motion.div>
          )}

          {currentScreen === 'story' && (
            <motion.div
              key="story"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.5 }}
              className="w-full max-w-6xl"
            >
              <StoryArea
                storyService={storyService}
                sessionId={sessionId}
                selectedAge={selectedAge}
                onEndSession={handleEndSession}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;