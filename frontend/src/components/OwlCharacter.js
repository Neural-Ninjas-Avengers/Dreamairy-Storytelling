import React from 'react';
import { motion } from 'framer-motion';

const OwlCharacter = ({ onClick, className = "" }) => {
  return (
    <motion.div
      className={`relative cursor-pointer group ${className}`}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      animate={{ 
        y: [0, -8, 0],
        rotate: [0, 1, -1, 0]
      }}
      transition={{ 
        y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
        rotate: { duration: 6, repeat: Infinity, ease: "easeInOut" },
        hover: { duration: 0.3 }
      }}
    >
      <div className="relative w-40 h-40 md:w-48 md:h-48 lg:w-56 lg:h-56">
        {/* Magical Aura */}
        <motion.div 
          className="absolute inset-0 bg-gradient-to-r from-kiro-400/20 via-purple-400/20 to-kiro-400/20 rounded-full blur-2xl"
          animate={{ 
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ 
            duration: 3, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
        />
        
        {/* Sparkles around owl */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-kiro-200 rounded-full"
            style={{
              top: `${20 + Math.sin(i * 60 * Math.PI / 180) * 80}px`,
              left: `${112 + Math.cos(i * 60 * Math.PI / 180) * 80}px`,
            }}
            animate={{
              scale: [0, 1, 0],
              opacity: [0, 1, 0],
              rotate: [0, 180, 360]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.3,
              ease: "easeInOut"
            }}
          />
        ))}
        
        {/* Owl body */}
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          {/* Ears */}
          <motion.div 
            className="absolute top-6 left-16 w-6 h-10 bg-gradient-to-b from-purple-300 via-purple-500 to-purple-700 rounded-t-full transform -rotate-15 shadow-lg"
            animate={{ rotate: [-15, -10, -15] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div 
            className="absolute top-6 right-16 w-6 h-10 bg-gradient-to-b from-purple-300 via-purple-500 to-purple-700 rounded-t-full transform rotate-15 shadow-lg"
            animate={{ rotate: [15, 10, 15] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          />
          
          {/* Main body */}
          <div className="relative w-32 h-36 md:w-36 md:h-40 lg:w-40 lg:h-44 bg-gradient-to-b from-purple-300 via-purple-500 to-purple-800 rounded-full shadow-2xl overflow-hidden">
            {/* Body texture */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-black/10" />
            <div className="absolute top-4 left-4 w-8 h-8 bg-white/5 rounded-full blur-sm" />
            <div className="absolute bottom-8 right-6 w-6 h-6 bg-black/10 rounded-full blur-sm" />
            
            {/* Face */}
            <div className="absolute top-10 left-1/2 transform -translate-x-1/2 w-32 h-28 bg-gradient-to-b from-orange-50 via-orange-100 to-orange-200 rounded-full shadow-inner border-2 border-orange-200/50">
              {/* Face highlight */}
              <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-20 h-8 bg-white/20 rounded-full blur-sm" />
              
              {/* Eyes */}
              <motion.div 
                className="absolute top-8 left-6 w-7 h-7 bg-gradient-to-b from-gray-800 to-black rounded-full shadow-inner"
                animate={{ scaleY: [1, 0.1, 1] }}
                transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
              >
                <div className="absolute top-1 left-1 w-3 h-3 bg-white rounded-full opacity-90" />
                <div className="absolute top-2 left-2 w-1 h-1 bg-blue-200 rounded-full" />
              </motion.div>
              <motion.div 
                className="absolute top-8 right-6 w-7 h-7 bg-gradient-to-b from-gray-800 to-black rounded-full shadow-inner"
                animate={{ scaleY: [1, 0.1, 1] }}
                transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
              >
                <div className="absolute top-1 left-1 w-3 h-3 bg-white rounded-full opacity-90" />
                <div className="absolute top-2 left-2 w-1 h-1 bg-blue-200 rounded-full" />
              </motion.div>
              
              {/* Beak */}
              <div className="absolute top-16 left-1/2 transform -translate-x-1/2">
                <div className="w-0 h-0 border-l-5 border-r-5 border-t-8 border-transparent border-t-orange-600 shadow-sm" />
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-3 border-r-3 border-t-5 border-transparent border-t-orange-400" />
              </div>
            </div>
            
            {/* Wings */}
            <motion.div 
              className="absolute top-16 -left-3 w-12 h-24 bg-gradient-to-br from-purple-400 via-purple-600 to-purple-900 rounded-full transform -rotate-15 shadow-xl"
              animate={{ rotate: [-15, -10, -15] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div 
              className="absolute top-16 -right-3 w-12 h-24 bg-gradient-to-bl from-purple-400 via-purple-600 to-purple-900 rounded-full transform rotate-15 shadow-xl"
              animate={{ rotate: [15, 10, 15] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
            
            {/* Wing details */}
            <div className="absolute top-20 -left-1 w-8 h-16 bg-gradient-to-br from-purple-300/50 to-transparent rounded-full transform -rotate-15" />
            <div className="absolute top-20 -right-1 w-8 h-16 bg-gradient-to-bl from-purple-300/50 to-transparent rounded-full transform rotate-15" />
          </div>
          
          {/* Hover effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-kiro-300/0 via-kiro-200/20 to-kiro-300/0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default OwlCharacter;