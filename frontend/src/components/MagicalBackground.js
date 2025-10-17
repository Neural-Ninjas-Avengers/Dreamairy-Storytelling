import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const MagicalBackground = () => {
  const [backgroundImage, setBackgroundImage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Solo generar si no hay imagen ya cargada
    if (!backgroundImage) {
      generateMagicalBackground();
    }
  }, [backgroundImage]);

  const generateMagicalBackground = async () => {
    // Evitar múltiples llamadas simultáneas
    if (isLoading || backgroundImage) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:3001/api/v1/generate-magical-background', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: "Ultra professional cinematic forest landscape, ancient towering trees, dappled sunlight filtering through canopy, moss-covered ground, ethereal mist, photorealistic, 8K quality, nature documentary style, serene and majestic atmosphere"
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.image_url) {
          setBackgroundImage(data.image_url);
        }
      }
    } catch (error) {
      console.log('Using fallback background');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-green-800 via-emerald-700 to-forest-900">
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="text-4xl text-green-200"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            🌲
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 overflow-hidden">
      {backgroundImage ? (
        <img 
          src={backgroundImage}
          alt="Magical Background"
          className="w-full h-full object-cover"
          style={{ filter: 'brightness(1.1) saturate(1.2)' }}
        />
      ) : (
        <div className="w-full h-full bg-gradient-to-br from-green-800 via-emerald-700 to-forest-900" />
      )}
      
      {/* Overlay suave para legibilidad */}
      <div className="absolute inset-0 bg-black/20" />
    </div>
  );
};

export default MagicalBackground;