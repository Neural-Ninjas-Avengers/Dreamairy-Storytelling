import React from 'react';
import { motion } from 'framer-motion';
import PhotoCapture from './PhotoCapture';
import LanguageSelector from './LanguageSelector';
import AIServiceStatus from './AIServiceStatus';
import { useLanguage } from '../contexts/LanguageContext';

const ModernWelcomeScreen = ({ 
  selectedAge, 
  selectedEmotion, 
  selectedTheme,
  selectedGender,
  onAgeSelect, 
  onEmotionSelect, 
  onThemeSelect,
  onGenderSelect,
  onStartStory,
  onPhotoTaken,
  sessionId,
  storytellingService,
  capturedPhoto,
  onNavigateToAdmin
}) => {
  const { t } = useLanguage();
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" }
    }
  };

  const ages = [3, 4, 5, 6, 7, 8, 9, 10];

  const themes = [
    { id: 'animals', icon: '🐾', label: t('themes.animals') },
    { id: 'adventure', icon: '🗺️', label: t('themes.adventure') },
    { id: 'fantasy', icon: '🧚‍♀️', label: t('themes.fantasy') },
    { id: 'friendship', icon: '👫', label: t('themes.friendship') }
  ];

  const isFormComplete = selectedAge && selectedTheme;

  return (
    <motion.div
      className="bg-white/5 backdrop-blur-xl rounded-3xl p-4 sm:p-6 lg:p-8 border border-white/10 shadow-2xl max-h-screen overflow-hidden relative"
      style={{
        background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      }}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Language Selector - Top Right */}
      <div className="absolute top-4 right-4 z-10">
        <LanguageSelector />
      </div>

      {/* AI Service Status - Top Left */}
      <div className="absolute top-4 left-4 z-10">
        <AIServiceStatus storytellingService={storytellingService} />
      </div>
      {/* Logo and branding */}
      <motion.div variants={itemVariants} className="text-center mb-4 sm:mb-6">
        <motion.div 
          className="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 mx-auto mb-2 sm:mb-4 flex items-center justify-center shadow-lg"
          animate={{ 
            scale: [1, 1.05, 1],
            rotate: capturedPhoto?.url ? [0, 0, 0] : [0, 2, -2, 0]
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
              className="w-full h-full object-cover rounded-full border-4 border-white border-opacity-50 shadow-2xl"
              style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.3))' }}
              onLoad={() => console.log('✅ Avatar loaded in logo')}
              onError={(e) => {
                console.error('❌ Avatar failed to load:', e);
                e.target.src = "/dreamairy-logo.svg";
              }}
            />
          ) : capturedPhoto?.url ? (
            <img 
              src={capturedPhoto.url} 
              alt="Tu Avatar" 
              className="w-full h-full object-cover rounded-full border-4 border-white border-opacity-50 shadow-2xl"
              style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.3))' }}
              onLoad={() => console.log('✅ Photo loaded in logo')}
              onError={(e) => {
                console.error('❌ Photo failed to load:', e);
                e.target.src = "/dreamairy-logo.svg";
              }}
            />
          ) : (
            <img 
              src="/dreamairy-logo.svg" 
              alt="DreamAIry Logo" 
              className="w-full h-full object-contain drop-shadow-lg"
              style={{ filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))' }}
            />
          )}
        </motion.div>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-1 sm:mb-2 bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent drop-shadow-sm">
          {capturedPhoto?.url ? t('yourMagicalStory') : t('appTitle')}
        </h1>
        <p className="text-slate-200/90 text-sm sm:text-base lg:text-lg font-medium">
          {capturedPhoto?.url ? t('starringYou') : t('appSubtitle')}
        </p>
      </motion.div>

      {/* Photo capture section - Moved up */}
      <motion.div variants={itemVariants} className="mb-4 sm:mb-6">
        <h3 className="text-white/95 text-base sm:text-lg lg:text-xl font-semibold mb-2 sm:mb-4 text-center tracking-wide">
          {t('takePhoto')}
        </h3>
        <PhotoCapture 
          onPhotoTaken={onPhotoTaken}
          sessionId={sessionId}
          storytellingService={storytellingService}
        />
        {/* Show detected info */}
        {capturedPhoto?.detected_age && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 p-3 bg-green-500/20 border border-green-400/30 rounded-xl text-center"
          >
            <p className="text-green-200 text-sm font-medium">
              ✅ IA detectó: {capturedPhoto.detected_age} años • {capturedPhoto.detected_gender === 'male' ? '👦 Chico' : '👧 Chica'}
            </p>
          </motion.div>
        )}
      </motion.div>

      {/* Gender selection */}
      <motion.div variants={itemVariants} className="mb-4 sm:mb-6">
        <h3 className="text-white/95 text-base sm:text-lg lg:text-xl font-semibold mb-2 sm:mb-4 text-center tracking-wide">
          Eres...
        </h3>
        <div className="grid grid-cols-2 gap-2 sm:gap-3">
          <motion.button
            className={`
              p-3 sm:p-4 rounded-xl font-semibold transition-all duration-300 text-sm sm:text-base
              ${selectedGender === 'male' 
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-xl scale-105 border border-white/20' 
                : 'bg-white/10 text-white/90 hover:bg-white/20 border border-white/10'
              }
            `}
            onClick={() => onGenderSelect('male')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            👦 Chico
          </motion.button>
          <motion.button
            className={`
              p-3 sm:p-4 rounded-xl font-semibold transition-all duration-300 text-sm sm:text-base
              ${selectedGender === 'female' 
                ? 'bg-gradient-to-r from-pink-600 to-pink-500 text-white shadow-xl scale-105 border border-white/20' 
                : 'bg-white/10 text-white/90 hover:bg-white/20 border border-white/10'
              }
            `}
            onClick={() => onGenderSelect('female')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            👧 Chica
          </motion.button>
        </div>
      </motion.div>

      {/* Age selection */}
      <motion.div variants={itemVariants} className="mb-4 sm:mb-6">
        <h3 className="text-white/95 text-base sm:text-lg lg:text-xl font-semibold mb-2 text-center tracking-wide">
          {t('howOldAreYou')}
        </h3>
        {selectedAge && (
          <p className="text-center text-blue-300 text-sm font-medium mb-2">
            🎂 {selectedAge} años seleccionados
          </p>
        )}
        <div className="grid grid-cols-4 gap-1 sm:gap-2">
          {ages.map((age) => (
            <motion.button
              key={age}
              className={`
                p-2 sm:p-3 rounded-xl font-semibold transition-all duration-300 text-sm sm:text-base relative overflow-hidden
                ${selectedAge === age 
                  ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-xl shadow-blue-500/25 scale-105 border border-white/20' 
                  : 'bg-white/10 text-white/90 hover:bg-white/20 hover:text-white border border-white/10 hover:border-white/20'
                }
              `}
              style={selectedAge === age ? {
                boxShadow: '0 10px 25px -5px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
              } : {}}
              onClick={() => onAgeSelect(age)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {age}
            </motion.button>
          ))}
        </div>
      </motion.div>



      {/* Theme selection */}
      <motion.div variants={itemVariants} className="mb-4 sm:mb-8">
        <h3 className="text-white/95 text-base sm:text-lg lg:text-xl font-semibold mb-2 sm:mb-4 text-center tracking-wide">
          {t('whatStoryType')}
        </h3>
        <div className="grid grid-cols-2 gap-2 sm:gap-3">
          {themes.map((theme) => (
            <motion.button
              key={theme.id}
              className={`
                p-2 sm:p-4 rounded-2xl text-center transition-all duration-300 flex items-center justify-center gap-1 sm:gap-2 relative overflow-hidden
                ${selectedTheme === theme.id 
                  ? 'bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white shadow-xl shadow-blue-500/25 scale-105 border border-white/20' 
                  : 'bg-white/10 text-white/90 hover:bg-white/20 hover:text-white border border-white/10 hover:border-white/20'
                }
              `}
              style={selectedTheme === theme.id ? {
                boxShadow: '0 15px 35px -5px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
              } : {}}
              onClick={() => onThemeSelect(theme.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="text-base sm:text-xl">{theme.icon}</span>
              <span className="text-xs sm:text-sm font-medium">{theme.label}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>



      {/* Start button */}
      <motion.div variants={itemVariants} className="text-center">
        <motion.button
          className={`
            w-full py-3 sm:py-4 px-6 sm:px-8 rounded-2xl font-bold text-base sm:text-lg transition-all duration-300 relative overflow-hidden
            ${isFormComplete 
              ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/40 border border-white/20' 
              : 'bg-slate-600/30 text-slate-400 cursor-not-allowed border border-slate-500/20'
            }
          `}
          style={isFormComplete ? {
            boxShadow: '0 20px 40px -10px rgba(59, 130, 246, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
          } : {}}
          onClick={onStartStory}
          disabled={!isFormComplete}
          whileHover={isFormComplete ? { scale: 1.02, y: -2 } : {}}
          whileTap={isFormComplete ? { scale: 0.98 } : {}}
        >
          {t('startMagicalStory')}
        </motion.button>
      </motion.div>

      {/* Admin Access Button */}
      <motion.div variants={itemVariants} className="mt-4">
        <motion.button
          className="w-full py-2 px-4 rounded-xl font-medium text-sm transition-all duration-300 bg-slate-700/30 text-slate-300 hover:bg-slate-600/40 hover:text-white border border-slate-500/30 hover:border-slate-400/50"
          onClick={onNavigateToAdmin}
          whileHover={{ scale: 1.01, y: -1 }}
          whileTap={{ scale: 0.99 }}
        >
          🛠️ {t('adminAccess', 'Admin Dashboard')}
        </motion.button>
      </motion.div>

    </motion.div>
  );
};

export default ModernWelcomeScreen;