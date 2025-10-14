import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LoadingModal = ({ isOpen, message }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl max-w-md w-full mx-4"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: "spring", duration: 0.5 }}
          >
            <div className="flex flex-col items-center">
              <motion.div
                className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full mb-6"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              <h3 className="text-white text-xl font-bold mb-2 text-center">
                {message || 'Cargando...'}
              </h3>
              <p className="text-white/70 text-sm text-center">
                Por favor espera un momento
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LoadingModal;
