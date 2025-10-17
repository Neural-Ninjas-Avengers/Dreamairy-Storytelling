import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

const WelcomeScreen = ({ selectedEmotion, onEmotionSelect, onStartStory }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: "easeOut" }
    }
  };

  const emotions = [
    {
      id: 'entertain',
      face: '😄',
      label: 'Diversión',
      bgColor: '#FFD700'
    },
    {
      id: 'calm',
      face: '😌',
      label: 'Calma',
      bgColor: '#4A90A4'
    },
    {
      id: 'stimulate_play',
      face: '😊',
      label: 'Energía',
      bgColor: '#FF7F50'
    }
  ];

  // Zorrito con imagen generada por IA
  const FoxCharacter = () => (
    <motion.div
      className="absolute left-1/2 transform -translate-x-1/2 cursor-pointer"
      style={{ 
        top: '35%',
        height: '30vh',
        width: 'auto'
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      animate={{ 
        y: [0, -8, 0], // Breathing motion
      }}
      transition={{ 
        y: { duration: 4, repeat: Infinity, ease: "easeInOut" }
      }}
    >
      {/* Sombra suave debajo del personaje */}
      <div 
        className="absolute bottom-0 left-1/2 transform -translate-x-1/2 rounded-full blur-sm"
        style={{
          width: '80%',
          height: '8px',
          backgroundColor: '#1A2E4C',
          opacity: 0.15,
          zIndex: -1
        }}
      />
      
      {/* Placeholder para imagen del zorrito */}
      <div 
        className="relative flex items-center justify-center rounded-2xl border-2 border-dashed border-white/30 bg-white/10 backdrop-blur-sm"
        style={{ 
          height: '30vh', 
          width: '20vh',
        }}
      >
        {/* Texto placeholder */}
        <div className="text-center text-white/80 p-4">
          <div className="text-6xl mb-2">🦊</div>
          <div className="text-sm font-medium">
            {t('foxImage')}
          </div>
          <div className="text-xs mt-1 opacity-70">
            {t('generateWithAI')}
          </div>
        </div>
        
        {/* Efecto de brillo sutil */}
        <motion.div
          className="absolute inset-0 rounded-2xl"
          style={{
            background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)'
          }}
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
    </motion.div>
  );

  return (
    <motion.div
      className="h-screen overflow-hidden relative"
      style={{
        background: 'linear-gradient(to bottom, #264653 0%, #2A9D8F 100%)'
      }}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Fondo limpio con puntos amarillos */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Pequeños puntos amarillos dispersos - estrellas/luciérnagas */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={`dot-${i}`}
            className="absolute w-2 h-2 rounded-full"
            style={{
              backgroundColor: '#E9C46A',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.6, 1, 0.6],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Indicador emocional - esquina superior derecha */}
      <motion.div 
        variants={itemVariants}
        className="absolute top-6 right-6 z-20"
      >
        <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
          <span className="text-white text-xl">😊</span>
        </div>
      </motion.div>

      {/* Título Kiro */}
      <motion.div 
        variants={itemVariants} 
        className="absolute top-16 left-1/2 transform -translate-x-1/2 text-center z-10"
      >
        <motion.h1 
          className="text-6xl font-bold text-yellow-200"
          style={{
            fontFamily: 'Comic Sans MS, cursive, system-ui',
            textShadow: '3px 3px 6px rgba(0,0,0,0.5)',
            letterSpacing: '3px'
          }}
        >
          Kiro
        </motion.h1>
      </motion.div>

      {/* Zorrito central - posicionado exactamente según especificaciones */}
      <FoxCharacter />

      {/* Botón principal - Comenzar historia */}
      <motion.div 
        variants={itemVariants} 
        className="absolute bottom-40 left-1/2 transform -translate-x-1/2 text-center z-10"
      >
        <motion.button
          className="text-white font-bold text-xl px-12 py-4 rounded-full shadow-2xl"
          style={{
            background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
            fontFamily: 'Comic Sans MS, cursive, system-ui'
          }}
          onClick={onStartStory}
          whileHover={{ 
            scale: 1.05,
            boxShadow: '0 25px 50px rgba(34,197,94,0.4)'
          }}
          whileTap={{ scale: 0.95 }}
        >
          {t('startStory')}
        </motion.button>
      </motion.div>

      {/* Opciones de historia */}
      <motion.div 
        variants={itemVariants} 
        className="absolute bottom-28 left-1/2 transform -translate-x-1/2 flex gap-6 justify-center z-10"
      >
        <motion.button
          className="bg-white text-gray-800 font-semibold px-6 py-3 rounded-2xl shadow-lg"
          style={{ fontFamily: 'Comic Sans MS, cursive, system-ui' }}
          onClick={onStartStory}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {t('newStory')}
        </motion.button>
        
        <motion.button
          className="bg-white text-gray-800 font-semibold px-6 py-3 rounded-2xl shadow-lg"
          style={{ fontFamily: 'Comic Sans MS, cursive, system-ui' }}
          onClick={() => alert('Función en desarrollo')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {t('continueStoryFull')}
        </motion.button>
      </motion.div>

      {/* Selector de emociones */}
      <motion.div 
        variants={itemVariants} 
        className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-full max-w-md px-6 z-10"
      >
        <motion.h3 
          className="text-center text-white text-lg font-bold mb-4"
          style={{ 
            fontFamily: 'Comic Sans MS, cursive, system-ui',
            textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
          }}
          variants={itemVariants}
        >
          Seleccionar emoción
        </motion.h3>
        
        <div className="grid grid-cols-3 gap-4">
          {emotions.map((emotion) => (
            <motion.div
              key={emotion.id}
              className={`
                relative cursor-pointer text-center p-4 rounded-full shadow-xl
                ${selectedEmotion === emotion.id ? 'ring-4 ring-white ring-opacity-80 scale-110' : ''}
              `}
              style={{
                backgroundColor: emotion.bgColor
              }}
              onClick={() => onEmotionSelect(emotion.id)}
              variants={itemVariants}
              whileHover={{ scale: 1.1, y: -5 }}
              whileTap={{ scale: 0.95 }}
              animate={selectedEmotion === emotion.id ? {
                scale: [1.1, 1.15, 1.1],
                transition: { duration: 1, repeat: Infinity, repeatType: 'reverse' }
              } : {}}
            >
              <motion.div 
                className="text-3xl mb-2"
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              >
                {emotion.face}
              </motion.div>
              <div 
                className="font-bold text-xs text-white"
                style={{ 
                  fontFamily: 'Comic Sans MS, cursive, system-ui',
                  textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
                }}
              >
                {emotion.label}
              </div>
              
              {/* Indicador de selección */}
              {selectedEmotion === emotion.id && (
                <motion.div
                  className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center shadow-lg"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                >
                  <div className="w-3 h-3 bg-green-500 rounded-full" />
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default WelcomeScreen;