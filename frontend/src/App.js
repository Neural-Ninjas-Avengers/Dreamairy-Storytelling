import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles/child-friendly.css';
import ChildFriendlyWelcomeScreen from './components/ChildFriendlyWelcomeScreen';
import ChildFriendlyStoryArea from './components/ChildFriendlyStoryArea';
import AdminDashboard from './components/AdminDashboard';
import AIInfoDisplay from './components/AIInfoDisplay';
import LoadingModal from './components/LoadingModal';
import { StorytellingService } from './services/StorytellingService';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';

function AppContent() {
  const { t } = useLanguage();
  // Check if we're on admin route
  const isAdminRoute = window.location.pathname === '/admin' || window.location.hash === '#/admin';
  
  const [currentScreen, setCurrentScreen] = useState(isAdminRoute ? 'admin' : 'welcome');
  const [selectedAge, setSelectedAge] = useState(null);
  const [selectedEmotion, setSelectedEmotion] = useState('entertain'); // Default emotion
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedGender, setSelectedGender] = useState(null);
  const [childName, setChildName] = useState('');
  const [storyService, setStoryService] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

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

    setIsLoading(true);
    setLoadingMessage(t('generatingStory'));

    try {
      const session = await storyService.createSession({
        age: selectedAge,
        preferences: [selectedTheme],
        emotional_goal: selectedEmotion,
        voice_preference: null,
        anonymous_id: 'react_' + Date.now() + '_' + Math.random().toString(36).substring(2, 11),
        gender: selectedGender,
        name: childName
      });
      
      if (!session.success) {
        throw new Error(session.error || 'Failed to create session');
      }
      
      const newSessionId = session.sessionId;
      setSessionId(newSessionId);
      
      // Upload photo if captured
      if (capturedPhoto && capturedPhoto.base64) {
        try {
          setLoadingMessage(t('processing'));
          await storyService.uploadUserPhoto(newSessionId, capturedPhoto.base64);
          console.log('Photo uploaded to session:', newSessionId);
        } catch (error) {
          console.error('Failed to upload photo to session:', error);
        }
      }
      
      setLoadingMessage(t('pleaseWait'));
      setCurrentScreen('story');
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to start story:', error);
      alert('No se pudo conectar al servidor. Usando modo demo...');
      // Continue with demo mode
      const demoSessionId = 'demo_session_' + Date.now();
      setSessionId(demoSessionId);
      setCurrentScreen('story');
      setIsLoading(false);
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
    setSelectedGender(null);
    setCapturedPhoto(null);
  };

  const handlePhotoTaken = (photoData) => {
    setCapturedPhoto(photoData);
    console.log('Photo captured for AI generation:', photoData);
    
    // Auto-select detected age and gender
    if (photoData.detected_age) {
      setSelectedAge(photoData.detected_age);
      console.log('🎯 Age detected and selected:', photoData.detected_age);
    }
    if (photoData.detected_gender) {
      setSelectedGender(photoData.detected_gender);
      console.log('🎯 Gender detected and selected:', photoData.detected_gender);
    }
    
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
    <div className="h-screen overflow-hidden">
      
      {/* AI Info Display - shows current AI services */}
      <AIInfoDisplay />
      
      {/* Loading Modal */}
      <LoadingModal isOpen={isLoading} message={loadingMessage} />
      
      <div className="relative z-10 h-screen flex items-center justify-center overflow-hidden">
        <AnimatePresence mode="wait">
          {currentScreen === 'welcome' && (
            <motion.div
              key="welcome"
              variants={screenVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.6 }}
              className="w-full h-full"
            >
              <ChildFriendlyWelcomeScreen
                selectedAge={selectedAge}
                selectedTheme={selectedTheme}
                selectedGender={selectedGender}
                childName={childName}
                onAgeSelect={setSelectedAge}
                onThemeSelect={setSelectedTheme}
                onGenderSelect={setSelectedGender}
                onNameChange={setChildName}
                onStartStory={handleStartStory}
                onPhotoTaken={handlePhotoTaken}
                capturedPhoto={capturedPhoto}
                sessionId={sessionId}
                storytellingService={storyService}
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
              className="w-full h-full"
            >
              <ChildFriendlyStoryArea
                storyService={storyService}
                sessionId={sessionId}
                selectedAge={selectedAge}
                selectedTheme={selectedTheme}
                selectedGender={selectedGender}
                capturedPhoto={capturedPhoto}
                childName={childName}
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
  );
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
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