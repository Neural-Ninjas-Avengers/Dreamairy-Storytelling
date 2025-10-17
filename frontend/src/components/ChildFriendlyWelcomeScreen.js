import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import PhotoCapture from './PhotoCapture';
import LanguageSelector from './LanguageSelector';
import { useLanguage } from '../contexts/LanguageContext';

const ChildFriendlyWelcomeScreen = ({ 
  selectedAge, 
  selectedTheme,
  selectedGender,
  childName,
  onAgeSelect, 
  onThemeSelect,
  onGenderSelect,
  onNameChange,
  onStartStory,
  onPhotoTaken,
  capturedPhoto,
  sessionId,
  storytellingService
}) => {
  const { t } = useLanguage();
  const [currentStep, setCurrentStep] = useState(1);
  const [tempName, setTempName] = useState(childName || '');

  // Datos para el diseño infantil
  const ages = [
    { value: 3, emoji: '🍼', label: `3 ${t('years')}` },
    { value: 4, emoji: '🧸', label: `4 ${t('years')}` },
    { value: 5, emoji: '🎈', label: `5 ${t('years')}` },
    { value: 6, emoji: '🎨', label: `6 ${t('years')}` },
    { value: 7, emoji: '📚', label: `7 ${t('years')}` },
    { value: 8, emoji: '🚀', label: `8 ${t('years')}` },
    { value: 9, emoji: '🎮', label: `9 ${t('years')}` },
    { value: 10, emoji: '🏆', label: `10 ${t('years')}` }
  ];

  const themes = [
    { 
      id: 'animals', 
      emoji: '🐾', 
      title: t('themes.animals'), 
      subtitle: t('themeSubtitles.animals'),
      color: 'from-green-400 to-emerald-500',
      bgColor: 'bg-green-100',
      bgImage: '/theme-images/animals.jpg'
    },
    { 
      id: 'space', 
      emoji: '🚀', 
      title: t('themes.space'), 
      subtitle: t('themeSubtitles.space'),
      color: 'from-purple-400 to-indigo-500',
      bgColor: 'bg-purple-100',
      bgImage: '/theme-images/space.jpg'
    },
    { 
      id: 'pirates', 
      emoji: '🏴‍☠️', 
      title: t('themes.pirates'), 
      subtitle: t('themeSubtitles.pirates'),
      color: 'from-blue-400 to-cyan-500',
      bgColor: 'bg-blue-100',
      bgImage: '/theme-images/pirates.jpg'
    },
    { 
      id: 'dinosaurs', 
      emoji: '🦕', 
      title: t('themes.dinosaurs'), 
      subtitle: t('themeSubtitles.dinosaurs'),
      color: 'from-orange-400 to-red-500',
      bgColor: 'bg-orange-100',
      bgImage: '/theme-images/dinosaurs.jpg'
    },
    { 
      id: 'magic', 
      emoji: '✨', 
      title: 'Magia', 
      subtitle: 'Hechizos y criaturas mágicas',
      color: 'from-pink-400 to-purple-500',
      bgColor: 'bg-pink-100',
      bgImage: '/theme-images/magic.jpg'
    },
    { 
      id: 'superheroes', 
      emoji: '🦸', 
      title: 'Superhéroes', 
      subtitle: 'Salva el mundo con tus poderes',
      color: 'from-red-400 to-yellow-500',
      bgColor: 'bg-red-100',
      bgImage: '/theme-images/superheroes.jpg'
    }
  ];

  const genders = [
    { value: 'male', emoji: '👦', label: t('imABoy'), color: 'from-blue-400 to-blue-600' },
    { value: 'female', emoji: '👧', label: t('imAGirl'), color: 'from-rose-400 to-red-500' }
  ];

  const isFormComplete = selectedAge && selectedTheme && selectedGender;

  return (
    <div className="h-screen relative overflow-hidden">
      {/* Contenido principal */}
      <div className="relative z-10 h-screen flex items-center justify-center p-4">
        <motion.div
          className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          {/* Header con logo y progreso */}
          <div className="bg-white/60 backdrop-blur-sm p-4 text-center relative overflow-visible">
            {/* Language Selector - Top Right of Card */}
            <div className="absolute top-4 right-4" style={{ zIndex: 10000 }}>
              <LanguageSelector />
            </div>
            <motion.div
              className="w-16 h-16 mx-auto mb-3 bg-white rounded-full flex items-center justify-center shadow-lg"
              animate={{ 
                rotate: [0, 5, -5, 0],
                scale: [1, 1.05, 1]
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
                  className="w-14 h-14 object-cover rounded-full"
                />
              ) : (
                <span className="text-3xl">📚</span>
              )}
            </motion.div>
            
            <h1 className="text-xl font-bold text-gray-800 mb-2">
              {t('yourMagicalStory')} ✨
            </h1>
            
            {/* Indicador de progreso */}
            <div className="flex justify-center space-x-2 mt-4">
              {[1, 2, 3, 4, 5].map((step) => (
                <div
                  key={step}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    step <= currentStep ? 'bg-gray-800' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Contenido por pasos */}
          <div className="p-4">
            <AnimatePresence mode="wait">
              {/* Paso 1: Foto */}
              {currentStep === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  className="text-center"
                >
                  <h2 className="text-xl font-bold text-gray-800 mb-4">
                    {t('takeYourPhoto')}
                  </h2>
                  <p className="text-gray-600 mb-6 text-center">
                    {t('youWillBeProtagonist')}
                  </p>
                  
                  <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 mb-6">
                    <PhotoCapture 
                      onPhotoTaken={onPhotoTaken}
                      sessionId={null}
                      storytellingService={null}
                    />
                  </div>

                  <button
                    onClick={() => setCurrentStep(2)}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 rounded-xl font-bold"
                  >
                    {t('continue')}
                  </button>
                </motion.div>
              )}

              {/* Paso 2: Nombre */}
              {currentStep === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  className="text-center"
                >
                  <h2 className="text-xl font-bold text-gray-800 mb-4">
                    {t('whatsYourNameQuestion')}
                  </h2>
                  <p className="text-gray-600 mb-6">
                    {t('personalizeStory')}
                  </p>
                  
                  <input
                    type="text"
                    value={tempName}
                    onChange={(e) => setTempName(e.target.value)}
                    placeholder={t('enterNameHere')}
                    className="w-full p-4 text-lg text-center rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:outline-none mb-6"
                    maxLength={20}
                  />

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep(1)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-bold"
                    >
                      {t('back')}
                    </button>
                    <button
                      onClick={() => {
                        if (tempName.trim()) {
                          onNameChange(tempName.trim());
                          setCurrentStep(3);
                        }
                      }}
                      disabled={!tempName.trim()}
                      className={`flex-1 py-3 rounded-xl font-bold ${
                        tempName.trim()
                          ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {t('continue')}→
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Paso 3: Género */}
              {currentStep === 3 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                >
                  <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">
                    {t('tellUsAboutYou')}
                  </h2>
                  
                  <div className="space-y-3 mb-6">
                    {genders.map((gender) => (
                      <motion.button
                        key={gender.value}
                        className={`w-full p-4 rounded-2xl border-2 transition-all duration-300 ${
                          selectedGender === gender.value
                            ? `bg-gradient-to-r ${gender.color} text-white border-transparent shadow-lg scale-105`
                            : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => onGenderSelect(gender.value)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="flex items-center justify-center space-x-3">
                          <span className="text-2xl">{gender.emoji}</span>
                          <span className="font-bold">{gender.label}</span>
                        </div>
                      </motion.button>
                    ))}
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep(2)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-bold"
                    >
                      {t('back')}
                    </button>
                    <button
                      onClick={() => setCurrentStep(4)}
                      disabled={!selectedGender}
                      className={`flex-1 py-3 rounded-xl font-bold ${
                        selectedGender
                          ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {t('continue')}→
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Paso 4: Edad */}
              {currentStep === 4 && (
                <motion.div
                  key="step3"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                >
                  <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">
                    {t('howOldQuestion')}
                  </h2>
                  
                  {capturedPhoto?.detected_age && (
                    <div className="mb-4 bg-blue-50 border border-blue-200 rounded-xl p-4">
                      <p className="text-sm text-gray-700 text-center mb-3">
                        <span className="font-semibold">{t('iThinkYouAre')}</span> {capturedPhoto.detected_age} {t('years')}
                      </p>
                      <button
                        onClick={() => onAgeSelect(capturedPhoto.detected_age)}
                        className="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg font-semibold text-sm transition-colors"
                      >
                        {t('correct')}
                      </button>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-4 gap-3 mb-6">
                    {ages.map((age) => (
                      <motion.button
                        key={age.value}
                        className={`aspect-square rounded-2xl border-2 transition-all duration-300 ${
                          selectedAge === age.value
                            ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white border-transparent shadow-lg scale-110'
                            : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => onAgeSelect(age.value)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <div className="flex flex-col items-center justify-center h-full">
                          <span className="text-2xl mb-1">{age.emoji}</span>
                          <span className="text-xs font-bold">{age.value}</span>
                        </div>
                      </motion.button>
                    ))}
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep(3)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-bold"
                    >
                      {t('back')}
                    </button>
                    <button
                      onClick={() => setCurrentStep(5)}
                      disabled={!selectedAge}
                      className={`flex-1 py-3 rounded-xl font-bold ${
                        selectedAge
                          ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {t('continue')}→
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Paso 5: Tema */}
              {currentStep === 5 && (
                <motion.div
                  key="step4"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                >
                  <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">
                    {t('whatStoryToLive')}
                  </h2>
                  
                  <div className="grid grid-cols-2 gap-3 mb-6">
                    {themes.map((theme) => (
                      <motion.button
                        key={theme.id}
                        className={`relative h-24 rounded-2xl border-2 transition-all duration-300 overflow-hidden ${
                          selectedTheme === theme.id
                            ? 'border-blue-500 shadow-xl scale-105'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                        onClick={() => onThemeSelect(theme.id)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {/* Background Image or Gradient */}
                        {theme.bgImage ? (
                          <>
                            <div 
                              className="absolute inset-0 bg-cover bg-center"
                              style={{ backgroundImage: `url(${theme.bgImage})` }}
                            />
                            <div className={`absolute inset-0 ${
                              selectedTheme === theme.id 
                                ? 'bg-blue-600/70' 
                                : 'bg-black/40 hover:bg-black/30'
                            } transition-all duration-300`} />
                          </>
                        ) : (
                          <div className={`absolute inset-0 bg-gradient-to-br ${theme.color} ${
                            selectedTheme === theme.id ? 'opacity-100' : 'opacity-80'
                          } transition-all duration-300`} />
                        )}
                        
                        {/* Content */}
                        <div className="relative flex flex-col items-center justify-center h-full z-10 p-2">
                          <div className="font-bold text-base text-white drop-shadow-md text-center">{theme.title}</div>
                          <div className="text-xs text-white/90 drop-shadow text-center mt-1">{theme.subtitle}</div>
                        </div>
                      </motion.button>
                    ))}
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setCurrentStep(4)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-bold"
                    >
                      {t('back')}
                    </button>
                    <button
                      onClick={onStartStory}
                      disabled={!isFormComplete}
                      className={`flex-1 py-4 rounded-xl font-bold text-lg ${
                        isFormComplete
                          ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-xl hover:shadow-2xl transform hover:scale-105'
                          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {t('createStory')}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ChildFriendlyWelcomeScreen;

