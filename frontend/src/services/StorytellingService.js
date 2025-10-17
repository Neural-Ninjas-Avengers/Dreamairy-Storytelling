// Theme services removed - using fixed design
import illustrationStyleTracker from './IllustrationStyleTracker';
import claudeDesignService from './ClaudeDesignService';

/**
 * Main storytelling service that coordinates all story-related functionality
 * Now uses the backend API which handles AWS/free service selection automatically
 * Enhanced with Claude design integration for dynamic theming and illustration consistency
 */
export class StorytellingService {
    constructor() {
        this.baseUrl = 'http://localhost:3001';
        this.currentSessionId = null;
        this.currentTheme = null;
        this.currentAge = null;
        this.currentEmotionalGoal = null;
        this.themeInitialized = false;
    }
    
    /**
     * Create a new storytelling session with dynamic theme
     */
    async createSession(sessionData) {
        try {
            console.log('🎬 Creating new session...');
            
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.currentSessionId = result.session_id;
            
            // Store session parameters for theme generation
            this.currentAge = sessionData.age || 7;
            this.currentEmotionalGoal = sessionData.emotional_goal || 'entertain';
            
            // Extract theme from preferences
            if (sessionData.preferences && sessionData.preferences.length > 0) {
                this.currentTheme = sessionData.preferences[0];
            }
            
            console.log('✅ Session created:', this.currentSessionId);
            
            // Initialize theme if we have all parameters (non-blocking)
            if (this.currentTheme && this.currentAge && this.currentEmotionalGoal) {
                // Don't await - let it run in background to avoid blocking story generation
                this.initializeTheme().catch(err => {
                    console.error('Theme initialization failed (non-critical):', err);
                });
            }
            
            return {
                success: true,
                sessionId: result.session_id,
                message: result.message
            };
        } catch (error) {
            console.error('❌ Session creation failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * Initialize dynamic theme for the session
     */
    async initializeTheme() {
        if (this.themeInitialized) {
            console.log('Theme already initialized');
            return;
        }
        
        // Theme initialization removed - using fixed design
        this.themeInitialized = true;
    }
    
    /**
     * Get current session ID or create a new one
     */
    async ensureSession(sessionData = {}) {
        if (!this.currentSessionId) {
            const defaultSessionData = {
                age: 7,
                preferences: ['fantasy'],
                emotional_goal: 'entertain',
                anonymous_id: `user_${Date.now()}`,
                ...sessionData
            };
            
            const result = await this.createSession(defaultSessionData);
            if (!result.success) {
                throw new Error('Failed to create session');
            }
        }
        return this.currentSessionId;
    }

    async generateStory(sessionId, storyData) {
        try {
            console.log('🎯 Generating story via backend API...');
            
            // Clean storyData to avoid circular references - ensure all values are primitives
            const cleanData = {
                theme: String(storyData.theme || ''),
                segments_so_far: Number(storyData.segments_so_far || 0),
                child_age: Number(storyData.child_age || 5),
                emotional_goal: String(storyData.emotional_goal || 'entertain'),
                language: String(storyData.language || 'es'),
                story_context: String(storyData.story_context || ''),
                last_segment: String(storyData.last_segment || ''),
                is_finale: Boolean(storyData.is_finale),
                detected_emotion: storyData.detected_emotion ? String(storyData.detected_emotion) : undefined,
                emotion_confidence: storyData.emotion_confidence ? Number(storyData.emotion_confidence) : undefined
            };
            
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/story`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(cleanData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Story generated via backend:', {
                provider: result.ai_provider,
                type: result.ai_type,
                environment: result.environment
            });
            
            return {
                success: true,
                story: result.text,
                metadata: {
                    provider: result.ai_provider || 'Backend API',
                    type: result.ai_type || 'unknown',
                    environment: result.environment || 'unknown',
                    costStatus: result.cost_status || 'unknown',
                    emotionalTone: result.emotional_tone,
                    pacing: result.pacing,
                    charactersInvolved: result.characters_involved
                }
            };
        } catch (error) {
            console.error('❌ Story generation failed:', error);
            return {
                success: false,
                error: error.message,
                fallback: this._generateFallbackStory(storyData)
            };
        }
    }

    async generateImage(sessionId, imageData) {
        try {
            const url = `${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/generate-image`;
            console.log('🎨 Generating image via backend API...');
            console.log('📍 URL:', url);
            console.log('📦 Payload:', JSON.stringify(imageData, null, 2));
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(imageData)
            });
            
            console.log('📥 Response status:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Image generated via backend:', {
                provider: result.ai_provider,
                type: result.ai_type,
                environment: result.environment,
                usingAWS: result.using_aws
            });
            
            return {
                success: result.success || true,
                imageUrl: result.image_url,
                image_url: result.image_url, // Agregar ambos formatos para compatibilidad
                metadata: {
                    provider: result.ai_provider || 'Backend API',
                    type: result.ai_type || 'unknown',
                    environment: result.environment || 'unknown',
                    costStatus: result.cost_status || 'unknown',
                    usingAWS: result.using_aws || false,
                    generationTime: result.generation_time || 0,
                    styleApplied: result.style_applied,
                    hasUserCharacter: result.has_user_character
                }
            };
        } catch (error) {
            console.error('❌ Image generation failed:', error);
            return {
                success: false,
                error: error.message,
                fallback: this._generateFallbackImage(imageData)
            };
        }
    }

    // Legacy methods for compatibility
    async generateStorySegment(sessionId, context) {
        console.log('📚 StorytellingService.generateStorySegment called with:', {
            sessionId,
            theme: context.theme,
            segments_so_far: context.segments_so_far,
            child_age: context.child_age
        });
        
        const result = await this.generateStory(sessionId, {
            theme: context.theme,
            segments_so_far: context.segments_so_far || 0,
            child_age: context.child_age,
            emotional_goal: context.emotional_goal,
            language: context.language || 'es',
            story_context: context.story_context || '',
            last_segment: context.last_segment || '',
            is_finale: context.is_finale || false,
            detected_emotion: context.detected_emotion,
            emotion_confidence: context.emotion_confidence
        });
        
        console.log('📚 StorytellingService.generateStorySegment result:', result);
        return result;
    }

    async generateStoryImage(sessionId, imageRequest) {
        console.log('🎨 StorytellingService.generateStoryImage called with:', {
            sessionId,
            hasSceneDescription: !!imageRequest.scene_description,
            theme: imageRequest.theme,
            hasUserPhoto: imageRequest.has_user_photo,
            hasUserAvatar: imageRequest.has_user_avatar
        });
        
        // Initialize illustration style guide if not done yet
        if (!illustrationStyleTracker.getStyleGuide()) {
            const theme = imageRequest.theme || this.currentTheme || 'fantasy';
            const age = imageRequest.child_age || this.currentAge || 7;
            const avatarDesc = imageRequest.character_description || 'friendly character';
            
            await illustrationStyleTracker.initializeStyleGuide(theme, age, avatarDesc);
        }
        
        // Optimize prompt with Claude for better consistency
        let optimizedPrompt = imageRequest.scene_description;
        try {
            const previousPrompts = illustrationStyleTracker.getPreviousPromptTexts(2);
            const promptOptimization = await claudeDesignService.optimizeIllustrationPrompt(
                imageRequest.scene_description,
                imageRequest.character_description || '',
                previousPrompts
            );
            
            // Apply style guide to optimized prompt
            optimizedPrompt = illustrationStyleTracker.getStyleConsistentPrompt(
                promptOptimization.prompt
            );
            
            console.log('✨ Prompt optimized with Claude and style guide');
            
        } catch (error) {
            console.warn('Prompt optimization failed, using base prompt:', error);
            // Apply style guide to base prompt as fallback
            optimizedPrompt = illustrationStyleTracker.getStyleConsistentPrompt(
                imageRequest.scene_description
            );
        }
        
        const result = await this.generateImage(sessionId, {
            scene_description: optimizedPrompt,
            story_context: imageRequest.story_context,
            character_description: imageRequest.character_description,
            style: imageRequest.style || 'children_book',
            has_user_photo: imageRequest.has_user_photo || false,
            has_user_avatar: imageRequest.has_user_avatar || false,
            user_photo_base64: imageRequest.user_photo_base64 || null,
            user_avatar_url: imageRequest.user_avatar_url || null,
            theme: imageRequest.theme,
            emotional_goal: imageRequest.emotional_goal,
            child_age: imageRequest.child_age
        });
        
        // Track prompt and image for consistency
        if (result.success && result.imageUrl) {
            illustrationStyleTracker.trackPrompt(
                optimizedPrompt,
                result.imageUrl,
                {
                    theme: imageRequest.theme,
                    age: imageRequest.child_age,
                    timestamp: new Date().toISOString()
                }
            );
            
            // Log consistency score
            const consistencyScore = illustrationStyleTracker.getConsistencyScore();
            console.log(`📊 Illustration consistency score: ${(consistencyScore * 100).toFixed(0)}%`);
        }
        
        console.log('🎨 StorytellingService.generateStoryImage result:', result);
        return result;
    }

    async requestStory(sessionId, storyData) {
        return this.generateStorySegment(sessionId, storyData);
    }

    async uploadUserPhoto(sessionId, photoBase64) {
        try {
            console.log('📸 Uploading user photo to session...');
            
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/upload-photo`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    photo_base64: photoBase64
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Photo uploaded successfully:', {
                hasAvatar: result.has_avatar,
                provider: result.avatar_provider,
                message: result.message
            });
            
            return {
                success: true,
                hasAvatar: result.has_avatar,
                avatarUrl: result.avatar_url,
                provider: result.avatar_provider,
                message: result.message
            };
        } catch (error) {
            console.error('❌ Photo upload failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async detectEmotionFromWebcam(sessionId) {
        try {
            console.log('📸 Capturing photo from webcam for emotion detection...');
            
            // Capturar foto de la webcam
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            
            // Esperar a que el video esté listo
            await new Promise(resolve => {
                video.onloadedmetadata = resolve;
            });
            
            // Capturar frame
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            // Detener stream
            stream.getTracks().forEach(track => track.stop());
            
            // Convertir a base64
            const photoBase64 = canvas.toDataURL('image/jpeg').split(',')[1];
            
            // Enviar al backend para detección de emoción
            const response = await fetch(`${this.getBackendUrl()}/api/v1/detect-emotion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    photo_base64: photoBase64,
                    session_id: sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Emotion detected:', result);
            
            return {
                emotion: result.emotion,
                confidence: result.confidence,
                allEmotions: result.all_emotions
            };
        } catch (error) {
            console.error('❌ Emotion detection failed:', error);
            return null;
        }
    }

    async sendEmotionFeedback(sessionId, emotionData) {
        try {
            console.log('🎭 Sending emotion feedback...');
            
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/emotion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emotionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Emotion feedback sent:', result);
            
            return {
                success: true,
                adaptation: result.adaptation,
                message: result.message
            };
        } catch (error) {
            console.error('❌ Emotion feedback failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getAvailableVoices() {
        try {
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/available-voices`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('🎤 Backend response:', result);
            
            // Extract voices based on current language
            if (result.voices) {
                const currentLang = this.language || 'es';
                const langKey = currentLang === 'en' ? 'english' : 'spanish';
                console.log('🎤 Current language:', currentLang, 'Key:', langKey);
                
                // If voices is an object with language keys, extract the appropriate array
                if (typeof result.voices === 'object' && !Array.isArray(result.voices)) {
                    const voices = result.voices[langKey] || [];
                    console.log('🎤 Extracted voices:', voices);
                    return voices;
                }
                
                // If it's already an array, return it
                return Array.isArray(result.voices) ? result.voices : [];
            }
            
            return [];
        } catch (error) {
            console.error('❌ Failed to get available voices:', error);
            // Return default voices as fallback
            return [
                { id: 'Lucia', name: 'Lucía', gender: 'Female', language: 'es-ES' },
                { id: 'Enrique', name: 'Enrique', gender: 'Male', language: 'es-ES' }
            ];
        }
    }

    async playStoryAudio(sessionId, text, voiceId = 'Lucia') {
        try {
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/audio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice_id: voiceId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Play audio
            if (result.audio_url) {
                const audio = new Audio(result.audio_url);
                await audio.play();
            }
            
            return { success: true };
        } catch (error) {
            console.error('❌ Failed to play audio:', error);
            return { success: false, error: error.message };
        }
    }

    async endSession(sessionId) {
        try {
            const response = await fetch(`${this.getBackendUrl()}/api/v1/demo/sessions/${sessionId}/end`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Session ended via API:', result);
                this.currentSessionId = null;
                return result;
            } else {
                throw new Error(`API error: ${response.status}`);
            }
        } catch (error) {
            console.warn('API not available, session ended locally:', error);
            this.currentSessionId = null;
            return {
                message: "Session ended (offline mode)",
                session_id: sessionId,
                duration_minutes: 0.0,
                total_segments: 0
            };
        }
    }

    _generateFallbackStory(storyData) {
        const theme = storyData.theme || 'adventure';
        const age = storyData.child_age || 7;
        
        const fallbackStories = {
            fantasy: [
                "Once upon a time, in a magical land far away, there lived a brave little hero who discovered that the greatest adventures come from helping others.",
                "In an enchanted forest filled with talking animals, a young child learned that friendship and kindness are the most powerful magic of all.",
                "Deep in a crystal castle, a curious adventurer found that every challenge is an opportunity to grow stronger and wiser."
            ],
            adventure: [
                "In a cozy village surrounded by mysterious mountains, an explorer discovered hidden treasures in the most unexpected places.",
                "On a sunny day, a brave child set out on a journey that would teach them about courage and determination.",
                "In a world full of wonders, a young hero learned that the best adventures happen when you help others."
            ],
            animals: [
                "In a peaceful meadow, a little rabbit named Luna made friends with all the forest creatures.",
                "A wise old owl taught a young fox about the importance of being kind to everyone.",
                "In the heart of the jungle, animals of all sizes learned to work together."
            ]
        };
        
        const stories = fallbackStories[theme] || fallbackStories.fantasy;
        
        return {
            story: stories[Math.floor(Math.random() * stories.length)],
            provider: 'Local Fallback Generator',
            model: 'Template-based',
            type: 'fallback'
        };
    }

    _generateFallbackImage(imageData) {
        const description = imageData.scene_description || 'Story scene';
        const theme = imageData.theme || 'adventure';
        
        // Theme-based colors
        const themeColors = {
            fantasy: { bg: '#e8f5e8', accent: '#4caf50', text: '#2e7d32' },
            adventure: { bg: '#fff3e0', accent: '#ff9800', text: '#ef6c00' },
            animals: { bg: '#f3e5f5', accent: '#9c27b0', text: '#7b1fa2' }
        };
        
        const colors = themeColors[theme] || themeColors.adventure;
        
        const svgImage = `data:image/svg+xml;base64,${btoa(`
            <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="300" fill="${colors.bg}"/>
                <circle cx="200" cy="120" r="40" fill="${colors.accent}" opacity="0.7"/>
                <rect x="150" y="180" width="100" height="60" rx="10" fill="${colors.accent}" opacity="0.5"/>
                <text x="200" y="270" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="${colors.text}">
                    ${description.substring(0, 25)}...
                </text>
                <text x="200" y="290" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="${colors.text}" opacity="0.7">
                    Fallback Illustration
                </text>
            </svg>
        `)}`;
        
        return {
            imageUrl: svgImage,
            provider: 'SVG Fallback Generator',
            model: 'Local SVG',
            type: 'fallback'
        };
    }

    // WebSocket compatibility methods (disabled)
    connect() {
        console.log('WebSocket connection disabled, using HTTP REST API only');
        return Promise.resolve();
    }

    disconnect() {
        // WebSocket disconnection (no-op)
    }

    onMessage(handler) {
        console.log('WebSocket messaging disabled');
        return () => {}; // Return empty unsubscribe function
    }

    sendMessage(message) {
        console.log('WebSocket messaging disabled, use HTTP REST API methods instead');
        return Promise.resolve();
    }

    generateConnectionId() {
        return 'react-demo-' + Math.random().toString(36).substring(2, 11);
    }

    getBackendUrl() {
        return window.location.hostname === 'localhost' 
            ? 'http://localhost:3001' 
            : '';
    }

    /**
     * Get AI service status information
     */
    async getAIServiceStatus() {
        try {
            console.log('🔍 Checking AI service status via backend...');
            
            const response = await fetch(`${this.getBackendUrl()}/api/v1/ai-info/current`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const aiInfo = await response.json();
            
            console.log('✅ AI service status retrieved:', aiInfo);
            
            // Transform backend AI info into the format expected by the frontend
            const status = {};
            
            if (aiInfo.using_aws_services) {
                status['aws-bedrock'] = {
                    available: true,
                    type: 'aws',
                    description: `${aiInfo.mode_name} - Professional AI services`,
                    features: ['High Quality', 'AWS Bedrock', 'Production Ready']
                };
            } else {
                status['free-services'] = {
                    available: true,
                    type: 'free',
                    description: `${aiInfo.mode_name} - Free AI services`,
                    features: ['No Cost', 'Demo Mode', 'Basic Quality']
                };
            }
            
            // Add fallback service
            status['local-fallback'] = {
                available: true,
                type: 'local',
                description: 'Local story templates and SVG generation',
                features: ['Always Available', 'Offline Ready', 'Template Based']
            };
            
            return status;
            
        } catch (error) {
            console.warn('❌ Failed to get AI service status, using fallback:', error);
            
            // Return fallback status
            return {
                'local-fallback': {
                    available: true,
                    type: 'local',
                    description: 'Local story generation (backend unavailable)',
                    features: ['Always Available', 'Offline Mode', 'Template Based']
                },
                'backend-unavailable': {
                    available: false,
                    type: 'error',
                    description: 'Backend services unavailable',
                    features: ['Connection Error']
                }
            };
        }
    }
}