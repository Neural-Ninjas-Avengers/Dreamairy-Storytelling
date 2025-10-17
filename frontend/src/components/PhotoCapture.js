import React, { useState, useRef, useCallback, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const PhotoCapture = ({ onPhotoTaken, sessionId, storytellingService }) => {
  const { t } = useLanguage();
  const [showModal, setShowModal] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [stream, setStream] = useState(null);
  const [avatarData, setAvatarData] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const openCameraModal = useCallback(() => {
    setShowModal(true);
  }, []);

  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user' // Front camera
        }
      });

      setStream(mediaStream);
      setIsCapturing(true);

      // Wait a bit for the video element to be ready
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.play();
        }
      }, 100);
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('No se pudo acceder a la cámara. Por favor verifica los permisos.');
      setShowModal(false);
    }
  }, []);

  // Auto-start camera when modal opens
  useEffect(() => {
    if (showModal && !isCapturing && !capturedPhoto) {
      startCamera();
    }
  }, [showModal, isCapturing, capturedPhoto, startCamera]);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCapturing(false);
  }, [stream]);

  const closeModal = useCallback(() => {
    stopCamera();
    setShowModal(false);
    setCapturedPhoto(null);
    setAvatarData(null);
    setUploadSuccess(false);
    setIsUploading(false);
  }, [stopCamera]);

  const capturePhoto = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob(async (blob) => {
      if (blob) {
        const photoUrl = URL.createObjectURL(blob);
        setCapturedPhoto(photoUrl);
        
        // Convert to base64 for API
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64Data = reader.result;
          
          console.log('📸 Photo captured, generating storybook avatar...');
          setIsUploading(true);
          
          try {
            // Automatically generate storybook avatar from photo
            const endpoint = sessionId && sessionId !== 'null' 
              ? `/api/v1/demo/sessions/${sessionId}/upload-photo`
              : '/api/v1/upload-photo';
              
            const response = await fetch(endpoint, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                photo_base64: base64Data
              }),
            });
            
            if (response.ok) {
              const result = await response.json();
              console.log('🎭 Storybook avatar generated:', result.provider);
              
              // Store avatar data
              if (result.avatar_url) {
                setAvatarData({
                  url: result.avatar_url,
                  provider: result.provider,
                  message: result.message,
                  detected_age: result.detected_age,
                  detected_gender: result.detected_gender
                });
              }
              
              setUploadSuccess(true);
              setIsUploading(false);
              
              // Call callback with both photo and avatar data
              onPhotoTaken && onPhotoTaken({
                blob: blob,
                base64: base64Data.split(',')[1],
                url: photoUrl,
                avatar_url: result.avatar_url,
                avatar_provider: result.provider,
                avatar_message: result.message,
                has_avatar: !!result.avatar_url,
                detected_age: result.detected_age,
                detected_gender: result.detected_gender
              });
              
            } else {
              console.error('Failed to generate avatar');
              setUploadSuccess(true);
              setIsUploading(false);
              
              // Still call callback with photo data
              onPhotoTaken && onPhotoTaken({
                blob: blob,
                base64: base64Data.split(',')[1],
                url: photoUrl
              });
            }
            
          } catch (error) {
            console.error('Error generating avatar:', error);
            setUploadSuccess(true);
            setIsUploading(false);
            
            // Still call callback with photo data
            onPhotoTaken && onPhotoTaken({
              blob: blob,
              base64: base64Data.split(',')[1],
              url: photoUrl
            });
          }
        };
        reader.readAsDataURL(blob);
      }
    }, 'image/jpeg', 0.8);

    // Stop camera after capture
    stopCamera();
  }, [stopCamera, onPhotoTaken, sessionId, storytellingService]);

  const retakePhoto = useCallback(() => {
    if (capturedPhoto) {
      URL.revokeObjectURL(capturedPhoto);
    }
    setCapturedPhoto(null);
    setAvatarData(null);
    setUploadSuccess(false);
    setIsUploading(false);
    startCamera();
  }, [capturedPhoto, startCamera]);

  const confirmPhoto = useCallback(() => {
    setShowModal(false);
  }, []);



  return (
    <>
      {/* Premium Photo Capture Interface */}
      <div className="relative">
        {!capturedPhoto ? (
          <motion.div
            className="group cursor-pointer"
            onClick={openCameraModal}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Main capture area */}
            <div className="relative bg-white border-2 border-gray-300 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300">
              
              {/* Content */}
              <div className="relative z-10 text-center space-y-4">
                {/* Icon with animation */}
                <motion.div
                  className="w-16 h-16 mx-auto bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg"
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  <span className="text-2xl">📸</span>
                </motion.div>
                
                {/* Title */}
                <div>
                  <h3 className="text-gray-800 text-lg font-bold mb-1">{t('createPersonalizedAvatar')}</h3>
                  <p className="text-gray-600 text-sm">{t('tapToCapture')}</p>
                </div>
                
                {/* Features */}
                <div className="flex justify-center gap-4 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <span>✨</span>
                    <span>{t('advancedAI')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>🎭</span>
                    <span>{t('storyStyle')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>🔒</span>
                    <span>{t('private')}</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative"
          >
            {/* Avatar preview card */}
            <div className="bg-gradient-to-br from-emerald-500/20 to-teal-500/20 backdrop-blur-xl border border-emerald-400/30 rounded-3xl p-6 shadow-2xl">
              <div className="flex items-center gap-4">
                {/* Avatar image */}
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl overflow-hidden border-2 border-emerald-400/50 shadow-xl">
                    <img
                      src={avatarData?.url || capturedPhoto}
                      alt="Avatar personalizado"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  {/* Success badge */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center shadow-lg"
                  >
                    <span className="text-white text-xs font-bold">✓</span>
                  </motion.div>
                </div>
                
                {/* Status info */}
                <div className="flex-1">
                  <h4 className="text-white font-bold text-sm mb-1">{t('avatarReady')}</h4>
                  <p className="text-white/70 text-xs mb-2">{t('youWillAppearInIllustrations')}</p>
                  
                  {/* Action button */}
                  <motion.button
                    className="text-emerald-300 text-xs font-semibold hover:text-emerald-200 transition-colors flex items-center gap-1"
                    onClick={openCameraModal}
                    whileHover={{ scale: 1.05 }}
                  >
                    <span>🔄</span>
                    <span>{t('changePhoto')}</span>
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Full Screen Modal - Rendered via Portal */}
      {showModal && ReactDOM.createPortal(
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm overflow-y-auto"
            style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}
            onClick={closeModal}
          >
            <div className="min-h-screen flex items-center justify-center p-4 py-8">
              <motion.div
                initial={{ scale: 0.9, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 20 }}
                className="bg-white rounded-2xl p-4 max-w-lg w-full shadow-2xl my-auto"
                onClick={(e) => e.stopPropagation()}
              >
              {/* Modal Header */}
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-gray-800 text-xl font-bold">{t('captureYourPhoto')}</h2>
                <motion.button
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 text-lg w-8 h-8 rounded-full flex items-center justify-center transition-colors shadow"
                  onClick={closeModal}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  ✕
                </motion.button>
              </div>

              <AnimatePresence mode="wait">
                {/* Camera View */}
                {isCapturing && !capturedPhoto && (
                  <motion.div
                    key="camera-modal"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-3"
                  >
                    <div className="relative bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border-2 border-gray-300">
                      <video
                        ref={videoRef}
                        className="w-full h-64 object-cover"
                        autoPlay
                        muted
                        playsInline
                      />
                      
                      {/* Camera overlay */}
                      <div className="absolute inset-0 border-4 border-dashed border-blue-400 border-opacity-50 pointer-events-none m-4 rounded-2xl"></div>
                      
                      {/* Center focus circle */}
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
                        <motion.div
                          className="w-32 h-32 border-4 border-blue-400 border-opacity-80 rounded-full flex items-center justify-center shadow-lg"
                          animate={{ scale: [1, 1.05, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <div className="w-4 h-4 bg-blue-400 rounded-full opacity-80 shadow-lg"></div>
                        </motion.div>
                      </div>
                    </div>
                    
                    {/* Camera Controls */}
                    <div className="flex gap-3 justify-center flex-wrap">
                      <motion.button
                        className="bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-xl font-bold text-base shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={capturePhoto}
                        disabled={isUploading}
                        whileHover={{ scale: isUploading ? 1 : 1.05 }}
                        whileTap={{ scale: isUploading ? 1 : 0.95 }}
                      >
                        <span className="text-xl">📷</span>
                        <span>{isUploading ? t('processing') : t('capture')}</span>
                      </motion.button>
                      
                      <motion.button
                        className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 px-5 rounded-xl font-bold border border-gray-300 disabled:opacity-50"
                        onClick={closeModal}
                        disabled={isUploading}
                        whileHover={{ scale: isUploading ? 1 : 1.05 }}
                        whileTap={{ scale: isUploading ? 1 : 0.95 }}
                      >
                        ❌ Cancelar
                      </motion.button>
                    </div>
                  </motion.div>
                )}

                {/* Photo Preview */}
                {capturedPhoto && (
                  <motion.div
                    key="photo-modal"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-3"
                  >
                    <div className="text-center">
                      <div className="relative inline-block">
                        <img
                          src={capturedPhoto}
                          alt="Foto capturada"
                          className="w-48 h-48 object-cover rounded-2xl border-4 border-blue-400 shadow-2xl"
                        />
                        
                        {/* Status indicator */}
                        <div className={`absolute -top-2 -right-2 w-10 h-10 rounded-full flex items-center justify-center shadow-xl transition-all duration-300 border-2 border-white ${
                          uploadSuccess ? 'bg-green-500' : isUploading ? 'bg-yellow-500 animate-pulse' : 'bg-blue-500'
                        }`}>
                          <span className="text-white text-lg font-bold">
                            {uploadSuccess ? '✓' : isUploading ? '⏳' : '📸'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Status message */}
                    <div className="text-center bg-gray-100 rounded-xl p-3 border border-gray-300">
                      <p className="text-gray-800 text-base font-bold mb-1">
                        {uploadSuccess 
                          ? (avatarData ? t('avatarCreated') : t('photoReady'))
                          : isUploading 
                          ? t('creatingAvatar')
                          : t('photoCaptured')
                        }
                      </p>
                      <p className="text-gray-600 text-xs">
                        {uploadSuccess 
                          ? (avatarData 
                              ? `${t('youWillAppearInIllustrationsWithAge')}${avatarData.detected_age ? ` · ${avatarData.detected_age} ${t('years')}` : ''}`
                              : t('willBeUsedForIllustrations')
                            )
                          : isUploading
                          ? t('analyzingPhoto')
                          : t('generatingAvatar')
                        }
                      </p>
                    </div>

                    {/* Success indicator */}
                    {uploadSuccess && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`${avatarData ? 'bg-blue-100 border-blue-300' : 'bg-green-100 border-green-300'} border-2 p-3 rounded-xl text-center shadow-lg`}
                      >
                        <div className="flex items-center justify-center gap-2 mb-1">
                          <span className="text-2xl">{avatarData ? '🎭' : '📸'}</span>
                          <span className="font-bold text-base text-gray-800">
                            {avatarData ? '¡Listo!' : '¡Perfecto!'}
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-gray-700">
                          {avatarData 
                            ? t('avatarReadyForStories')
                            : t('photoReadyForIllustrations')
                          }
                        </p>
                      </motion.div>
                    )}
                    
                    {/* Photo controls */}
                    <div className="flex gap-3 justify-center flex-wrap">
                      <motion.button
                        className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-5 rounded-xl font-bold border border-gray-300 text-sm"
                        onClick={retakePhoto}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        🔄 Otra
                      </motion.button>
                      
                      {uploadSuccess && (
                        <motion.button
                          className="bg-green-500 hover:bg-green-600 text-white py-2 px-6 rounded-xl font-bold shadow-lg text-sm"
                          onClick={confirmPhoto}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          ✓ Confirmar
                        </motion.button>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              </motion.div>
            </div>
          </motion.div>
        </AnimatePresence>,
        document.body
      )}

      {/* Hidden canvas for photo processing */}
      <canvas ref={canvasRef} className="hidden" />
    </>
  );
};

export default PhotoCapture;