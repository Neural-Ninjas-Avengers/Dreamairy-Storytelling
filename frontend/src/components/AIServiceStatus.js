import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const AIServiceStatus = ({ storytellingService, className = '' }) => {
  const { t } = useLanguage();
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    checkAIStatus();
  }, [storytellingService]);

  const checkAIStatus = async () => {
    if (!storytellingService) return;
    
    setIsLoading(true);
    try {
      const aiStatus = await storytellingService.getAIServiceStatus();
      setStatus(aiStatus);
    } catch (error) {
      console.error('Failed to check AI status:', error);
      setStatus({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (providerStatus) => {
    if (!providerStatus) return '❓';
    if (providerStatus.available && providerStatus.type === 'local') return '🤖';
    if (providerStatus.available) return '✅';
    return '❌';
  };

  const getStatusText = (providerStatus) => {
    if (!providerStatus) return 'Unknown';
    if (providerStatus.available && providerStatus.type === 'local') return 'Active';
    if (providerStatus.available) return 'Available';
    return 'Unavailable';
  };

  const getProviderName = (provider) => {
    const names = {
      'enhanced-local-ai': 'Enhanced Local AI',
      'story-templates': 'Story Templates',
      huggingface: 'Hugging Face AI',
      textsynth: 'TextSynth AI',
      fallback: 'Local Stories'
    };
    return names[provider] || provider;
  };

  if (isLoading) {
    return (
      <div className={`text-white text-xs opacity-70 ${className}`}>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Checking AI services...</span>
        </div>
      </div>
    );
  }

  if (!status || status.error) {
    return (
      <div className={`text-white text-xs opacity-70 ${className}`}>
        <div className="flex items-center gap-2">
          <span>❌</span>
          <span>AI services unavailable</span>
        </div>
      </div>
    );
  }

  const availableCount = Object.values(status).filter(s => s.available).length;
  const totalCount = Object.keys(status).length;

  return (
    <div className={`text-white text-xs ${className}`}>
      <motion.button
        className="flex items-center gap-2 opacity-70 hover:opacity-100 transition-opacity"
        onClick={() => setIsExpanded(!isExpanded)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <span>🤖</span>
        <span>AI: {availableCount}/{totalCount}</span>
        <motion.span
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </motion.button>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="mt-2 bg-black bg-opacity-30 rounded-lg p-3 space-y-2"
        >
          <div className="text-xs font-semibold mb-2">AI Story Services:</div>
          {Object.entries(status).map(([provider, providerStatus]) => (
            <div key={provider} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{getStatusIcon(providerStatus)}</span>
                  <span className="font-medium">{getProviderName(provider)}</span>
                </div>
                <span className="text-xs opacity-70">
                  {getStatusText(providerStatus)}
                </span>
              </div>
              {providerStatus.description && (
                <div className="text-xs opacity-60 ml-6">
                  {providerStatus.description}
                </div>
              )}
              {providerStatus.features && (
                <div className="text-xs opacity-50 ml-6">
                  {providerStatus.features.join(' • ')}
                </div>
              )}
            </div>
          ))}
          
          <div className="border-t border-white border-opacity-20 pt-2 mt-2">
            <div className="text-xs opacity-70">
              {availableCount > 0 
                ? `🎭 ${availableCount} AI system${availableCount > 1 ? 's' : ''} ready for intelligent story generation`
                : 'AI systems initializing...'
              }
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default AIServiceStatus;