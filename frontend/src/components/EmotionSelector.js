import React from 'react';
import { motion } from 'framer-motion';

const EmotionSelector = ({ selectedEmotion, onEmotionSelect, size = 'large' }) => {
  const emotions = [
    {
      id: 'entertain',
      emoji: '😄',
      label: 'Diversión',
      description: 'Historias llenas de aventura y risas',
      gradient: 'from-amber-400 via-orange-500 to-yellow-500',
      shadowColor: 'shadow-amber-500/30',
      ringColor: 'ring-amber-300'
    },
    {
      id: 'calm',
      emoji: '😌',
      label: 'Calma',
      description: 'Cuentos relajantes y tranquilos',
      gradient: 'from-blue-400 via-cyan-500 to-teal-500',
      shadowColor: 'shadow-blue-500/30',
      ringColor: 'ring-blue-300'
    },
    {
      id: 'stimulate_play',
      emoji: '😊',
      label: 'Energía',
      description: 'Aventuras emocionantes y dinámicas',
      gradient: 'from-pink-400 via-rose-500 to-red-500',
      shadowColor: 'shadow-pink-500/30',
      ringColor: 'ring-pink-300'
    }
  ];

  const sizeClasses = {
    large: {
      container: 'w-28 h-28 lg:w-32 lg:h-32',
      emoji: 'text-4xl lg:text-5xl',
      label: 'text-lg lg:text-xl',
      description: 'text-sm lg:text-base'
    },
    compact: {
      container: 'w-20 h-20 md:w-24 md:h-24',
      emoji: 'text-2xl md:text-3xl',
      label: 'text-sm md:text-base',
      description: 'text-xs md:text-sm'
    },
    small: {
      container: 'w-16 h-16',
      emoji: 'text-xl',
      label: 'text-sm',
      description: 'text-xs'
    }
  };

  const currentSize = sizeClasses[size];

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
    hidden: { opacity: 0, y: 20, scale: 0.8 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  };

  const gridClasses = size === 'compact' 
    ? "grid grid-cols-3 gap-3 md:gap-4" 
    : "grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8";

  return (
    <motion.div
      className={gridClasses}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {emotions.map((emotion) => {
        const isSelected = selectedEmotion === emotion.id;
        
        return (
          <motion.div
            key={emotion.id}
            className="group relative"
            variants={itemVariants}
            whileHover={{ y: -8 }}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className={`
                relative bg-white/90 backdrop-blur-sm rounded-2xl p-6 cursor-pointer
                border-2 transition-all duration-300
                ${isSelected 
                  ? `border-white ${emotion.shadowColor} shadow-2xl` 
                  : 'border-white/20 hover:border-white/40 shadow-lg hover:shadow-xl'
                }
              `}
              onClick={() => onEmotionSelect(emotion.id)}
              animate={isSelected ? {
                scale: [1, 1.02, 1],
                transition: { duration: 2, repeat: Infinity, repeatType: 'reverse' }
              } : {}}
            >
              {/* Selection Ring */}
              {isSelected && (
                <motion.div
                  className={`absolute inset-0 rounded-2xl ${emotion.ringColor} ring-4 ring-opacity-60`}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.3 }}
                />
              )}

              {/* Glow Effect */}
              <div className={`
                absolute inset-0 rounded-2xl bg-gradient-to-br ${emotion.gradient} opacity-0 
                group-hover:opacity-10 transition-opacity duration-300
                ${isSelected ? 'opacity-5' : ''}
              `} />

              <div className="relative z-10 text-center">
                {/* Emoji Container */}
                <motion.div
                  className={`
                    ${currentSize.container} mx-auto mb-4 rounded-2xl
                    bg-gradient-to-br ${emotion.gradient} ${emotion.shadowColor} shadow-lg
                    flex items-center justify-center
                  `}
                  whileHover={{ rotate: [0, -10, 10, 0] }}
                  transition={{ duration: 0.5 }}
                >
                  <span className={`${currentSize.emoji} filter drop-shadow-sm`}>
                    {emotion.emoji}
                  </span>
                </motion.div>

                {/* Label */}
                <h4 className={`
                  ${currentSize.label} font-bold text-forest-800 mb-2
                  ${isSelected ? 'text-forest-900' : ''}
                `}>
                  {emotion.label}
                </h4>

                {/* Description */}
                <p className={`
                  ${currentSize.description} text-forest-600 leading-relaxed
                  ${isSelected ? 'text-forest-700' : ''}
                `}>
                  {emotion.description}
                </p>

                {/* Selection Indicator */}
                {isSelected && (
                  <motion.div
                    className="mt-4 flex items-center justify-center"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${emotion.gradient}`} />
                    <div className={`w-4 h-1 mx-1 rounded-full bg-gradient-to-r ${emotion.gradient}`} />
                    <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${emotion.gradient}`} />
                  </motion.div>
                )}
              </div>
            </motion.div>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

export default EmotionSelector;