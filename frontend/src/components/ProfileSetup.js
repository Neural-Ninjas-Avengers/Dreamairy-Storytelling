import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import EmotionSelector from './EmotionSelector';

const ProfileSetup = ({ 
  selectedAge, 
  selectedEmotion, 
  onAgeSelect, 
  onEmotionSelect, 
  onStartStory, 
  onBack 
}) => {
  const ages = [3, 4, 5, 6, 7, 8];

  return (
    <motion.div
      className="glass-card p-8 text-center text-white"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h2
        className="font-fredoka text-4xl mb-8 text-kiro-100"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        Configurar Perfil
      </motion.h2>

      {/* Age Selection */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-2xl font-semibold mb-4 text-kiro-100">
          {t('howOldQuestion')}
        </h3>
        <div className="flex gap-3 justify-center flex-wrap">
          {ages.map((age, index) => (
            <motion.button
              key={age}
              className={`
                w-14 h-14 rounded-full font-bold text-lg transition-all duration-300
                ${selectedAge === age 
                  ? 'bg-gradient-to-br from-coral-400 to-coral-600 text-white ring-4 ring-white ring-opacity-60 shadow-lg' 
                  : 'bg-gradient-to-br from-forest-400 to-forest-600 text-white hover:from-forest-300 hover:to-forest-500'
                }
              `}
              onClick={() => onAgeSelect(age)}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              {age}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Emotion Selection */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-2xl font-semibold mb-4 text-kiro-100">
          {t('howDoYouFeel')}
        </h3>
        <EmotionSelector
          selectedEmotion={selectedEmotion}
          onEmotionSelect={onEmotionSelect}
          size="large"
        />
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        className="flex flex-col gap-4 items-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <motion.button
          className="btn-primary text-xl"
          onClick={onStartStory}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {t('beginAdventure')}
        </motion.button>
        
        <motion.button
          className="flex items-center gap-2 text-kiro-100 hover:text-white transition-colors duration-300"
          onClick={onBack}
          whileHover={{ scale: 1.05, x: -5 }}
          whileTap={{ scale: 0.95 }}
        >
          <ArrowLeft size={20} />
          Volver
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default ProfileSetup;