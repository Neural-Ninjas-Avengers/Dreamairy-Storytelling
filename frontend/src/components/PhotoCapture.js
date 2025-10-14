import React, { useState, useRef, useCallback, useEffect } from 'react';
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
      {/* Trigger Button */}
      <div className="text-center">
        {!capturedPhoto ? (
          <motion.button
            className="bg-white bg-opacity-20 text-white py-3 px-6 rounded-2xl font-semibold hover:bg-opacity-30 transition-all duration-300 flex items-center gap-2 mx-auto"
            onClick={openCameraModal}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="text-xl">📸</span>
            <span>{t('takePhotoButton')}</span>
          </motion.button>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-3"
          >
            <div className="relative inline-block">
              <img
                src={avatarData?.url || capturedPhoto}
                alt="Avatar de cuento"
                className="w-20 h-20 object-cover rounded-xl border-2 border-green-400 shadow-lg"
              />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">🎭</span>
              </div>
            </div>
            <div>
              <p className="text-white text-xs font-semibold">
                Avatar de cuento listo
              </p>
              <motion.button
                className="text-white text-xs opacity-70 hover:opacity-100 underline mt-1"
                onClick={openCameraModal}
                whileHover={{ scale: 1.05 }}
              >
                {t('retakePhoto')}
              </motion.button>
            </div>
          </motion.div>
        )}
        
        {!capturedPhoto && (
          <p className="text-white text-xs opacity-70 mt-2">
            {t('optionalPhotoText')}
          </p>
        )}
      </div>

      {/* Full Screen Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gradient-to-br from-indigo-900 to-purple-900 rounded-3xl p-6 max-w-2xl w-full max-h-screen overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-white text-xl font-bold">📸 Captura tu Foto</h2>
                <motion.button
                  className="text-white text-2xl hover:text-red-400 transition-colors"
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
                    className="space-y-6"
                  >
                    <div className="relative bg-black rounded-2xl overflow-hidden shadow-2xl">
                      <video
                        ref={videoRef}
                        className="w-full h-80 object-cover"
                        autoPlay
                        muted
                        playsInline
                      />
                      
                      {/* Camera overlay */}
                      <div className="absolute inset-0 border-4 border-dashed border-white border-opacity-40 pointer-events-none"></div>
                      
                      {/* Center focus circle */}
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
                        <motion.div
                          className="w-32 h-32 border-3 border-white border-opacity-80 rounded-full flex items-center justify-center"
                          animate={{ scale: [1, 1.05, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <div className="w-3 h-3 bg-white rounded-full opacity-80"></div>
                        </motion.div>
                      </div>
                      
                      {/* Instructions */}
                      <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-70 text-white p-4 rounded-xl">
                        <div className="text-center">
                          <div className="font-bold text-lg mb-2">📸 Posiciónate en el centro</div>
                          <div className="text-sm opacity-90">
                            Asegúrate de que tu cara esté bien iluminada y centrada
                          </div>
                          <div className="text-xs opacity-70 mt-2">
                            Tu imagen se usará para crear ilustraciones AI personalizadas
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Camera Controls */}
                    <div className="flex gap-4 justify-center">
                      <motion.button
                        className="bg-gradient-to-r from-pink-500 to-indigo-600 text-white py-4 px-8 rounded-2xl font-bold text-lg shadow-xl flex items-center gap-3"
                        onClick={capturePhoto}
                        disabled={isUploading}
                        whileHover={{ scale: isUploading ? 1 : 1.05 }}
                        whileTap={{ scale: isUploading ? 1 : 0.95 }}
                      >
                        <span className="text-2xl">📷</span>
                        <span>{isUploading ? 'Procesando...' : 'Capturar Foto'}</span>
                      </motion.button>
                      
                      <motion.button
                        className="bg-white bg-opacity-20 text-white py-4 px-6 rounded-2xl font-semibold"
                        onClick={closeModal}
                        disabled={isUploading}
                        whileHover={{ scale: isUploading ? 1 : 1.05 }}
                        whileTap={{ scale: isUploading ? 1 : 0.95 }}
                      >
                        Cancelar
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
                    className="space-y-6"
                  >
                    <div className="text-center">
                      <div className="relative inline-block">
                        <img
                          src={capturedPhoto}
                          alt="Foto capturada"
                          className="w-64 h-64 object-cover rounded-2xl border-4 border-white border-opacity-30 shadow-2xl"
                        />
                        
                        {/* Status indicator */}
                        <div className={`absolute -top-3 -right-3 w-12 h-12 rounded-full flex items-center justify-center shadow-xl transition-all duration-300 ${
                          uploadSuccess ? 'bg-green-500' : isUploading ? 'bg-yellow-500 animate-pulse' : 'bg-blue-500'
                        }`}>
                          <span className="text-white text-lg font-bold">
                            {uploadSuccess ? '✓' : isUploading ? '⏳' : '📸'}
                          </span>
                        </div>
                        
                        {/* Quality badge */}
                        <div className="absolute bottom-3 left-3 right-3 bg-black bg-opacity-70 text-white px-3 py-2 rounded-xl">
                          <div className="flex justify-between items-center text-sm">
                            <span>Calidad:</span>
                            <span className="font-bold text-green-300">Excelente ✨</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Status message */}
                    <div className="text-center">
                      <p className="text-white text-lg font-semibold mb-2">
                        {uploadSuccess 
                          ? (avatarData ? '✨ ¡Avatar de cuento creado!' : '📸 ¡Foto lista para historias!')
                          : isUploading 
                          ? '🎭 Creando tu avatar de cuento...'
                          : '¡Foto capturada exitosamente!'
                        }
                      </p>
                      <p className="text-white text-sm opacity-80">
                        {uploadSuccess 
                          ? (avatarData 
                              ? `Tu avatar personalizado aparecerá en todas las ilustraciones${avatarData.detected_age ? ` · ${avatarData.detected_age} años` : ''}${avatarData.detected_gender ? ` · ${avatarData.detected_gender === 'male' ? 'Chico' : 'Chica'}` : ''}`
                              : 'Tu foto se usará para crear ilustraciones personalizadas'
                            )
                          : isUploading
                          ? 'AWS Rekognition está analizando tu foto...'
                          : 'Se generará automáticamente tu avatar de cuento personalizado'
                        }
                      </p>
                    </div>

                    {/* Success indicator */}
                    {uploadSuccess && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`bg-gradient-to-r ${avatarData ? 'from-purple-500 to-pink-600' : 'from-green-500 to-emerald-600'} text-white p-4 rounded-2xl text-center`}
                      >
                        <div className="flex items-center justify-center gap-3 mb-2">
                          <span className="text-2xl">{avatarData ? '🎭' : '📸'}</span>
                          <span className="font-bold text-lg">
                            {avatarData ? '¡Avatar creado!' : '¡Foto lista!'}
                          </span>
                        </div>
                        <p className="text-sm opacity-90">
                          {avatarData 
                            ? 'Tu avatar de cuento aparecerá en todas las ilustraciones'
                            : 'Tu foto se usará para crear ilustraciones personalizadas'
                          }
                        </p>
                        {avatarData && (
                          <p className="text-xs opacity-75 mt-2">
                            Generado con {avatarData.provider}
                          </p>
                        )}
                      </motion.div>
                    )}
                    
                    {/* Photo controls */}
                    <div className="flex gap-4 justify-center">
                      <motion.button
                        className="bg-white bg-opacity-20 text-white py-3 px-6 rounded-xl font-semibold"
                        onClick={retakePhoto}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        🔄 Tomar Otra
                      </motion.button>
                      
                      {uploadSuccess && (
                        <motion.button
                          className="bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-6 rounded-xl font-semibold"
                          onClick={confirmPhoto}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          ✓ Confirmar y Continuar
                        </motion.button>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hidden canvas for photo processing */}
      <canvas ref={canvasRef} className="hidden" />
    </>
  );
};

export default PhotoCapture;