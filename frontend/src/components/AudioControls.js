import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const AudioControls = ({ 
  sessionId, 
  storyService, 
  currentText, 
  isPlaying, 
  setIsPlaying 
}) => {
  const { t, language } = useLanguage();
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [audioProvider, setAudioProvider] = useState('Browser TTS');
  const [volume, setVolume] = useState(0.8);
  const [speed, setSpeed] = useState(1.0);
  const audioRef = useRef(null);
  const currentAudioRef = useRef(null);

  useEffect(() => {
    loadAvailableVoices();
  }, []);

  const loadAvailableVoices = async () => {
    try {
      const response = await fetch('/api/v1/demo/available-voices');
      const data = await response.json();
      
      if (data.success) {
        const voices = language === 'es' ? data.voices.spanish : data.voices.english;
        setAvailableVoices(voices);
        setAudioProvider(data.provider);
        
        // Set default voice
        const defaultVoice = language === 'es' ? data.default.spanish : data.default.english;
        setSelectedVoice(defaultVoice);
      }
    } catch (error) {
      console.error('Error loading voices:', error);
      // Fallback to browser voices
      setAvailableVoices([
        { id: language === 'es' ? 'es-ES' : 'en-US', name: 'Sistema', gender: 'System' }
      ]);
      setAudioProvider('Browser TTS');
    }
  };

  const generateSpeech = async (text, voiceId = selectedVoice) => {
    if (!text) return;
    
    console.log('🎵 Starting audio generation...');
    
    // FIRST: Stop any current audio before starting new one
    stopCurrentAudio();
    
    try {
      setIsPlaying(true);
      
      // Try AWS Polly first
      const response = await fetch(`/api/v1/demo/sessions/${sessionId}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          language: language,
          voice_id: voiceId
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.audio_data) {
          // Use AWS Polly audio
          console.log(`🗣️ Using ${result.provider} with voice ${result.voice_used}`);
          const audio = new Audio(result.audio_data);
          audio.volume = volume;
          
          currentAudioRef.current = audio;
          
          audio.onended = () => {
            setIsPlaying(false);
            currentAudioRef.current = null;
          };
          
          audio.onerror = (error) => {
            console.warn('AWS Polly audio playback failed, falling back to browser TTS', error);
            currentAudioRef.current = null;
            setIsPlaying(false);
            // Don't auto-fallback, let user try again
            // fallbackToBrowserTTS(text);
          };
          
          try {
            await audio.play();
          } catch (playError) {
            console.warn('AWS Polly audio play() failed, falling back to browser TTS');
            currentAudioRef.current = null;
            fallbackToBrowserTTS(text);
          }
        } else {
          // Fallback to browser TTS
          fallbackToBrowserTTS(text);
        }
      } else {
        // Fallback to browser TTS
        fallbackToBrowserTTS(text);
      }
    } catch (error) {
      console.error('Speech generation error:', error);
      fallbackToBrowserTTS(text);
    }
  };
  
  const fallbackToBrowserTTS = (text) => {
    if ('speechSynthesis' in window) {
      console.log('🗣️ Using browser TTS (fallback)');
      
      // Stop any current speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'en' ? 'en-US' : 'es-ES';
      utterance.rate = speed;
      utterance.pitch = 1.1;
      utterance.volume = volume;
      
      // Try to use selected voice if available
      const voices = speechSynthesis.getVoices();
      const voice = voices.find(v => v.lang.startsWith(language === 'en' ? 'en' : 'es'));
      if (voice) {
        utterance.voice = voice;
      }
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      
      speechSynthesis.speak(utterance);
    } else {
      setIsPlaying(false);
    }
  };

  const stopCurrentAudio = () => {
    console.log('🛑 Stopping all audio playback');
    
    // Stop AWS Polly audio
    if (currentAudioRef.current) {
      try {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current = null;
        console.log('   ✅ AWS Polly audio stopped');
      } catch (e) {
        console.warn('   ⚠️ Error stopping AWS audio:', e);
      }
    }
    
    // Stop browser TTS
    if ('speechSynthesis' in window) {
      try {
        speechSynthesis.cancel();
        console.log('   ✅ Browser TTS stopped');
      } catch (e) {
        console.warn('   ⚠️ Error stopping browser TTS:', e);
      }
    }
    
    setIsPlaying(false);
  };

  const toggleAudio = () => {
    if (isPlaying) {
      stopCurrentAudio();
    } else if (currentText) {
      generateSpeech(currentText);
    }
  };

  const testVoice = async (voiceId) => {
    const testText = language === 'es' 
      ? "Hola, soy tu narrador de cuentos mágicos." 
      : "Hello, I'm your magical story narrator.";
    
    await generateSpeech(testText, voiceId);
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 shadow-xl"
         style={{
           background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
           boxShadow: '0 15px 35px -5px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
         }}>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white/95 font-semibold flex items-center gap-2">
          🗣️ {language === 'en' ? 'Audio Controls' : 'Controles de Audio'}
        </h3>
        <div className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded-full">
          {audioProvider}
        </div>
      </div>

      {/* Main Play/Stop Button */}
      <div className="flex items-center gap-3 mb-4">
        <motion.button
          className={`flex-1 py-3 px-4 rounded-xl font-semibold transition-all duration-300 ${
            isPlaying 
              ? 'bg-red-500/80 hover:bg-red-500 text-white' 
              : 'bg-green-500/80 hover:bg-green-500 text-white'
          }`}
          onClick={toggleAudio}
          disabled={!currentText}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isPlaying ? (
            <>⏹️ {language === 'en' ? 'Stop' : 'Parar'}</>
          ) : (
            <>▶️ {language === 'en' ? 'Play' : 'Reproducir'}</>
          )}
        </motion.button>
      </div>

      {/* Voice Selection */}
      {availableVoices.length > 1 && (
        <div className="mb-4">
          <label className="block text-white/80 text-sm font-medium mb-2">
            {language === 'en' ? 'Voice' : 'Voz'}:
          </label>
          <select
            value={selectedVoice || ''}
            onChange={(e) => setSelectedVoice(e.target.value)}
            className="w-full bg-white/10 text-white border border-white/20 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {availableVoices.map((voice) => (
              <option key={voice.id} value={voice.id} className="bg-gray-800 text-white">
                {voice.name} ({voice.gender})
              </option>
            ))}
          </select>
          
          {/* Test Voice Button */}
          {audioProvider === 'Amazon Polly' && (
            <motion.button
              className="w-full mt-2 bg-white/10 text-white/80 py-2 px-3 rounded-lg text-sm hover:bg-white/20 transition-all"
              onClick={() => testVoice(selectedVoice)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              🎵 {language === 'en' ? 'Test Voice' : 'Probar Voz'}
            </motion.button>
          )}
        </div>
      )}

      {/* Volume Control */}
      <div className="mb-4">
        <label className="block text-white/80 text-sm font-medium mb-2">
          🔊 {language === 'en' ? 'Volume' : 'Volumen'}: {Math.round(volume * 100)}%
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => setVolume(parseFloat(e.target.value))}
          className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
        />
      </div>

      {/* Speed Control (only for browser TTS) */}
      {audioProvider === 'Browser TTS' && (
        <div className="mb-4">
          <label className="block text-white/80 text-sm font-medium mb-2">
            ⚡ {language === 'en' ? 'Speed' : 'Velocidad'}: {speed}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>
      )}

      {/* Status */}
      <div className="text-center">
        <p className="text-white/60 text-xs">
          {isPlaying ? (
            <>🎵 {language === 'en' ? 'Playing...' : 'Reproduciendo...'}</>
          ) : (
            <>⏸️ {language === 'en' ? 'Ready to play' : 'Listo para reproducir'}</>
          )}
        </p>
      </div>

      {/* Custom CSS for sliders */}
      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          box-shadow: 0 2px 6px rgba(59, 130, 246, 0.4);
        }
        
        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 6px rgba(59, 130, 246, 0.4);
        }
      `}</style>
    </div>
  );
};

export default AudioControls;