import React from 'react';
import { motion } from 'framer-motion';

const ForestBackground = () => {
  const stars = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    top: Math.random() * 70,
    delay: Math.random() * 5,
    size: Math.random() * 2 + 1,
    duration: Math.random() * 3 + 2
  }));

  const floatingElements = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 10,
    duration: Math.random() * 20 + 15,
    size: Math.random() * 4 + 2
  }));

  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-forest-800/50 via-forest-700/30 to-forest-900/80" />
      
      {/* Atmospheric layers */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-forest-600/10 to-forest-900/20" />
      
      {/* Hills - Multiple layers for depth */}
      <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-forest-700/60 to-transparent rounded-t-full transform scale-x-150 blur-sm" />
      <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-forest-600/40 to-transparent rounded-t-full transform scale-x-125" />
      <div className="absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t from-forest-500/30 to-transparent rounded-t-full" />
      
      {/* Trees - More subtle and layered */}
      <div className="absolute bottom-0 left-0 w-24 h-64 bg-gradient-to-t from-forest-900/80 to-forest-800/40 rounded-t-full transform -skew-x-6 -translate-x-4 blur-sm" />
      <div className="absolute bottom-0 right-0 w-20 h-48 bg-gradient-to-t from-forest-900/70 to-forest-800/30 rounded-t-full transform skew-x-8 translate-x-2 blur-sm" />
      <div className="absolute bottom-0 left-1/5 w-16 h-40 bg-gradient-to-t from-forest-900/60 to-forest-800/20 rounded-t-full blur-sm" />
      <div className="absolute bottom-0 right-1/4 w-18 h-44 bg-gradient-to-t from-forest-900/50 to-forest-800/15 rounded-t-full blur-sm" />
      
      {/* Mid-ground trees */}
      <div className="absolute bottom-0 left-1/8 w-12 h-32 bg-gradient-to-t from-forest-800/40 to-transparent rounded-t-full blur-xs" />
      <div className="absolute bottom-0 right-1/6 w-14 h-36 bg-gradient-to-t from-forest-800/35 to-transparent rounded-t-full blur-xs" />
      
      {/* Stars - More varied and subtle */}
      {stars.map((star) => (
        <motion.div
          key={star.id}
          className="absolute bg-kiro-100 rounded-full"
          style={{
            left: `${star.left}%`,
            top: `${star.top}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
          }}
          animate={{
            opacity: [0.2, 0.8, 0.2],
            scale: [0.8, 1.2, 0.8],
          }}
          transition={{
            duration: star.duration,
            repeat: Infinity,
            delay: star.delay,
            ease: "easeInOut"
          }}
        />
      ))}
      
      {/* Magical floating particles */}
      {floatingElements.map((element) => (
        <motion.div
          key={`particle-${element.id}`}
          className="absolute bg-kiro-200/30 rounded-full blur-sm"
          style={{
            left: `${element.left}%`,
            width: `${element.size}px`,
            height: `${element.size}px`,
          }}
          animate={{
            y: ['100vh', '-10vh'],
            x: [0, Math.sin(element.id) * 50],
            opacity: [0, 0.6, 0.8, 0.6, 0],
            scale: [0.5, 1, 1.2, 1, 0.5],
          }}
          transition={{
            duration: element.duration,
            repeat: Infinity,
            delay: element.delay,
            ease: "linear"
          }}
        />
      ))}
      
      {/* Ambient light rays */}
      <div className="absolute top-0 left-1/4 w-1 h-full bg-gradient-to-b from-kiro-200/20 via-transparent to-transparent transform rotate-12 blur-sm" />
      <div className="absolute top-0 right-1/3 w-1 h-full bg-gradient-to-b from-kiro-200/15 via-transparent to-transparent transform -rotate-6 blur-sm" />
      
      {/* Subtle mist effect */}
      <motion.div
        className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-white/5 to-transparent"
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  );
};

export default ForestBackground;