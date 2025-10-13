import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ModernWelcomeScreen from './components/ModernWelcomeScreen';
import ModernStoryArea from './components/ModernStoryArea';
import AdminDashboard from './components/AdminDashboard';
import AIInfoDisplay from './components/AIInfoDisplay';
import { StorytellingService } from './services/StorytellingService';
import { LanguageProvider } from './contexts/LanguageContext';

function App() {
  // Check if we're on admin route
  const isAdminRoute = window.location.pathname === '/admin' || window.location.hash === '#/admin';
  
  const [currentScreen, setCurrentScreen] = useState(isAdminRoute ? 'admin' : 'welcome');
  const [selectedAge, setSelectedAge] = useState(null);
  const [selectedEmotion, setSelectedEmotion] = useState('entertain'); // Default emotion
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [storyService, setStoryService] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [capturedPhoto, setCapturedPhoto] = useState(null);

  useEffect(() => {
    // Initialize storytelling service
    const service = new StorytellingService();
    setStoryService(service);

    // Handle URL changes for admin routing
    const handlePopState = () => {
      const isAdmin = window.location.pathname === '/admin' || window.location.hash === '#/admin';
      setCurrentScreen(isAdmin ? 'admin' : 'welcome');
    };

    window.addEventListener('popstate', handlePopState);

    // Cleanup on unmount
    return () => {
      if (service) {
        service.disconnect();
      }
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  const handleStartStory = async () => {
    if (!storyService || !selectedAge || !selectedTheme) return;

    try {
      const session = await storyService.createSession({
        age: selectedAge,
        preferences: [selectedTheme],
        emotional_goal: selectedEmotion,
        voice_preference: null,
        anonymous_id: 'react_' + Date.now() + '_' + Math.random().toString(36).substring(2, 11)
      });
      
      if (!session.success) {
        throw new Error(session.error || 'Failed to create session');
      }
      
      const newSessionId = session.sessionId;
      setSessionId(newSessionId);
      
      // Upload photo if captured
      if (capturedPhoto && capturedPhoto.base64) {
        try {
          await storyService.uploadUserPhoto(newSessionId, capturedPhoto.base64);
          console.log('Photo uploaded to session:', newSessionId);
        } catch (error) {
          console.error('Failed to upload photo to session:', error);
        }
      }
      
      setCurrentScreen('story');
    } catch (error) {
      console.error('Failed to start story:', error);
      alert('No se pudo conectar al servidor. Usando modo demo...');
      // Continue with demo mode
      const demoSessionId = 'demo_session_' + Date.now();
      setSessionId(demoSessionId);
      setCurrentScreen('story');
    }
  };

  const handleEndSession = async () => {
    if (storyService && sessionId) {
      try {
        await storyService.endSession(sessionId);
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
    setSessionId(null);
    setCurrentScreen('welcome');
    // Reset form
    setSelectedAge(null);
    setSelectedEmotion('entertain'); // Reset to default
    setSelectedTheme(null);
    setCapturedPhoto(null);
  };

  const handlePhotoTaken = (photoData) => {
    setCapturedPhoto(photoData);
    console.log('Photo captured for AI generation:', photoData);
    
    // If avatar was generated, log it
    if (photoData.has_avatar && photoData.avatar_url) {
      console.log('🎭 Avatar generated:', photoData.avatar_provider);
      console.log('Avatar URL:', photoData.avatar_url);
    }
  };

  const navigateToAdmin = () => {
    window.history.pushState({}, '', '/admin');
    setCurrentScreen('admin');
  };

  const navigateToApp = () => {
    window.history.pushState({}, '', '/');
    setCurrentScreen('welcome');
  };

  const screenVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  };

  return (
    <LanguageProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 relative overflow-hidden">
        {/* Premium background overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-indigo-600/10 to-purple-600/20"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-400/20 via-transparent to-transparent"></div>
        {/* Premium animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                width: `${2 + Math.random() * 4}px`,
                height: `${2 + Math.random() * 4}px`,
                background: `linear-gradient(45deg, rgba(59, 130, 246, ${0.3 + Math.random() * 0.4}), rgba(147, 51, 234, ${0.2 + Math.random() * 0.3}))`,
                boxShadow: `0 0 ${10 + Math.random() * 20}px rgba(59, 130, 246, 0.3)`,
              }}
              animate={{
                y: [0, -150 - Math.random() * 100, 0],
                x: [0, Math.random() * 50 - 25, 0],
                opacity: [0.2, 0.8, 0.2],
                scale: [0.8, 1.2, 0.8],
              }}
              transition={{
                duration: 8 + Math.random() * 6,
                repeat: Infinity,
                delay: Math.random() * 8,
                ease: "easeInOut"
              }}
            />
          ))}
          
          {/* Floating geometric shapes */}
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={`geo-${i}`}
              className="absolute opacity-10"
              style={{
                left: `${10 + Math.random() * 80}%`,
                top: `${10 + Math.random() * 80}%`,
                width: `${40 + Math.random() * 60}px`,
                height: `${40 + Math.random() * 60}px`,
                background: `linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1))`,
                borderRadius: i % 2 === 0 ? '50%' : '20%',
                border: '1px solid rgba(59, 130, 246, 0.2)',
              }}
              animate={{
                rotate: [0, 360],
                scale: [1, 1.1, 1],
                opacity: [0.05, 0.15, 0.05],
              }}
              transition={{
                duration: 20 + Math.random() * 10,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          ))}
        </div>
      
      {/* AI Info Display - shows current AI services */}
      <AIInfoDisplay />
      
      <div className="relative z-10 min-h-screen flex items-center justify-center p-2 sm:p-4">
        <AnimatePresence mode="wait">
          {currentScreen === 'welcome' && (
            <motion.div
              key="welcome"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.6 }}
              className="w-full max-w-sm sm:max-w-md lg:max-w-lg h-screen max-h-screen flex items-center"
            >
              <ModernWelcomeScreen
                selectedAge={selectedAge}
                selectedEmotion={selectedEmotion}
                selectedTheme={selectedTheme}
                onAgeSelect={setSelectedAge}
                onEmotionSelect={setSelectedEmotion}
                onThemeSelect={setSelectedTheme}
                onStartStory={handleStartStory}
                onPhotoTaken={handlePhotoTaken}
                sessionId={sessionId}
                storytellingService={storyService}
                capturedPhoto={capturedPhoto}
                onNavigateToAdmin={navigateToAdmin}
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
              transition={{ duration: 0.6 }}
              className="w-full max-w-6xl"
            >
              <ModernStoryArea
                storyService={storyService}
                sessionId={sessionId}
                selectedAge={selectedAge}
                selectedEmotion={selectedEmotion}
                selectedTheme={selectedTheme}
                capturedPhoto={capturedPhoto}
                onEndSession={handleEndSession}
              />
            </motion.div>
          )}

          {currentScreen === 'admin' && (
            <motion.div
              key="admin"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.6 }}
              className="w-full h-full"
            >
              <AdminDashboard onNavigateToApp={navigateToApp} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
    </LanguageProvider>
  );
}

// Original App component preserved as backup
/*
function OriginalApp() {
  // Old React app functionality preserved as backup
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
*/

export default App;