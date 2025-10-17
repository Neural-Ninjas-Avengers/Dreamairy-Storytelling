#!/usr/bin/env python3
"""
DreamAIry Backend Server
Simple Flask server for the adaptive storytelling application
"""

import os
import sys
import json
import logging
import requests
import base64
import io
from datetime import datetime
from typing import Tuple
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import admin module
from admin.api import admin_bp
from admin.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS for frontend communication
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Additional CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ===== EMOTION DETECTION ENDPOINT (Must be before blueprints) =====
@app.route('/api/v1/detect-emotion', methods=['POST', 'OPTIONS'])
def detect_emotion_endpoint():
    """Detect emotion from photo using AWS Rekognition"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info("🎭 ===== DETECT EMOTION ENDPOINT CALLED =====")
        data = request.get_json()
        photo_base64 = data.get("photo_base64", "")
        
        if not photo_base64:
            logger.warning("⚠️ No photo data provided")
            return jsonify({"error": "Photo data is required"}), 400
        
        logger.info(f"📸 Photo received (length: {len(photo_base64)} chars)")
        config_manager = ConfigManager()
        credentials = config_manager.get_aws_credentials()
        
        if not credentials:
            logger.warning("⚠️ AWS credentials not configured - returning mock emotion")
            # Return mock emotion for testing
            return jsonify({
                "success": True,
                "emotion": "happy",
                "label": "Feliz",
                "icon": "😊",
                "confidence": 0.85,
                "story_influence": "entertain",
                "all_emotions": [{"type": "HAPPY", "confidence": 85}]
            })
        
        logger.info("✅ AWS credentials found, initializing Rekognition...")
        from admin.aws_connector import AWSConnector
        aws_connector = AWSConnector(credentials)
        photo_bytes = base64.b64decode(photo_base64.split(',')[1] if ',' in photo_base64 else photo_base64)
        
        logger.info("🔍 Calling AWS Rekognition detect_faces...")
        success, faces = aws_connector.detect_faces(photo_bytes)
        
        if not success or not faces:
            logger.warning("⚠️ No face detected in photo")
            return jsonify({"success": False, "message": "No face detected"}), 200
        
        logger.info(f"👤 Face detected! Analyzing emotions...")
        face = faces[0]
        emotions = face.get('Emotions', [])
        
        if not emotions:
            logger.warning("⚠️ No emotions detected in face")
            return jsonify({"success": False, "message": "No emotions detected"}), 200
        
        top_emotion = max(emotions, key=lambda e: e['Confidence'])
        logger.info(f"😊 Top emotion detected: {top_emotion['Type']} ({top_emotion['Confidence']:.1f}%)")
        
        emotion_map = {
            'HAPPY': {'label': 'Feliz', 'icon': '😊', 'influence': 'entertain'},
            'SAD': {'label': 'Triste', 'icon': '😢', 'influence': 'calm'},
            'ANGRY': {'label': 'Enojado', 'icon': '😠', 'influence': 'calm'},
            'CONFUSED': {'label': 'Confundido', 'icon': '😕', 'influence': 'entertain'},
            'DISGUSTED': {'label': 'Disgustado', 'icon': '🤢', 'influence': 'entertain'},
            'SURPRISED': {'label': 'Sorprendido', 'icon': '😲', 'influence': 'entertain'},
            'CALM': {'label': 'Calmado', 'icon': '😌', 'influence': 'calm'},
            'FEAR': {'label': 'Asustado', 'icon': '😨', 'influence': 'calm'}
        }
        
        emotion_type = top_emotion['Type']
        emotion_info = emotion_map.get(emotion_type, {'label': 'Neutral', 'icon': '😐', 'influence': 'entertain'})
        
        return jsonify({
            "success": True,
            "emotion": emotion_type.lower(),
            "label": emotion_info['label'],
            "icon": emotion_info['icon'],
            "confidence": top_emotion['Confidence'] / 100,
            "story_influence": emotion_info['influence'],
            "all_emotions": [{"type": e['Type'], "confidence": e['Confidence']} for e in emotions]
        })
        
    except Exception as e:
        logger.error(f"Error detecting emotion: {e}")
        return jsonify({"success": False, "message": str(e)}), 200

# Register admin blueprint
app.register_blueprint(admin_bp)

# Register background generator blueprint
from api.background_generator import background_bp
app.register_blueprint(background_bp, url_prefix='/api/v1')
app.register_blueprint(background_bp, url_prefix='/api', name='background_legacy')  # Also register for /api/placeholder

# Register Claude design blueprint
from api.claude_design import claude_design_bp
app.register_blueprint(claude_design_bp)

# Serve admin static files
@app.route('/admin/<path:filename>')
def serve_admin_files(filename):
    """Serve admin panel files"""
    admin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'admin')
    return send_from_directory(admin_dir, filename)

# Simple in-memory storage for demo
sessions = {}
stories = {}

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "DreamAIry Backend Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "sessions": "/api/v1/demo/sessions",
            "stories": "/api/v1/demo/sessions/{id}/story"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/v1/system/status')
def system_status():
    """System status endpoint"""
    return jsonify({
        "status": "operational",
        "services": {
            "backend": "running",
            "ai_services": "mock_mode",
            "database": "memory"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/ai-info/current')
def get_current_ai_info():
    """Get information about currently active AI services"""
    try:
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        # Determine current environment and AWS status
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        aws_region = admin_config.get('aws', {}).get('region', 'eu-west-1') if admin_config else 'eu-west-1'
        
        # Determine which services are being used
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        ai_info = {
            "environment": environment,
            "aws_enabled": aws_enabled,
            "aws_region": aws_region,
            "using_aws_services": using_aws,
            "services": {}
        }
        
        if using_aws:
            # AWS Services
            ai_info["services"] = {
                "story_generation": {
                    "provider": "Amazon Bedrock",
                    "model": "amazon.titan-text-express-v1",
                    "type": "aws",
                    "cost": "paid",
                    "description": "AWS Bedrock with Titan Text Express",
                    "icon": "🤖"
                },
                "image_generation": {
                    "provider": "Amazon Bedrock",
                    "model": "amazon.nova-canvas-v1:0", 
                    "type": "aws",
                    "cost": "paid",
                    "description": "AWS Bedrock with Titan Image Generator",
                    "icon": "🎨"
                },
                "text_to_speech": {
                    "provider": "Amazon Polly",
                    "model": "Neural TTS",
                    "type": "aws", 
                    "cost": "paid",
                    "description": "AWS Polly Neural Text-to-Speech",
                    "icon": "🗣️"
                },
                "emotion_detection": {
                    "provider": "Amazon Rekognition",
                    "model": "Face Analysis",
                    "type": "aws",
                    "cost": "paid", 
                    "description": "AWS Rekognition Emotion Detection",
                    "icon": "😊"
                }
            }
            ai_info["cost_warning"] = "AWS costs apply"
            ai_info["quality"] = "high"
            ai_info["mode_icon"] = "☁️"
            ai_info["mode_name"] = "AWS AI"
            
        else:
            # Free/Mock Services
            ai_info["services"] = {
                "story_generation": {
                    "provider": "Local Generator",
                    "model": "Template-based",
                    "type": "local",
                    "cost": "free",
                    "description": "Local story templates and generation",
                    "icon": "📚"
                },
                "image_generation": {
                    "provider": "Pollinations.ai / Hugging Face",
                    "model": "Stable Diffusion",
                    "type": "free_api",
                    "cost": "free",
                    "description": "Free AI image generation services",
                    "icon": "🎨"
                },
                "text_to_speech": {
                    "provider": "Browser TTS",
                    "model": "Web Speech API",
                    "type": "browser",
                    "cost": "free",
                    "description": "Browser-based text-to-speech",
                    "icon": "🔊"
                },
                "emotion_detection": {
                    "provider": "Mock Service",
                    "model": "Simulated",
                    "type": "mock",
                    "cost": "free",
                    "description": "Simulated emotion detection",
                    "icon": "🎭"
                }
            }
            ai_info["cost_warning"] = "No AWS costs"
            ai_info["quality"] = "basic"
            ai_info["mode_icon"] = "🆓"
            ai_info["mode_name"] = "Free AI"
        
        response = jsonify(ai_info)
        # Add cache prevention headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        logger.error(f"Failed to get AI info: {e}")
        return jsonify({"error": "Failed to retrieve AI service information"}), 500

@app.route('/api/v1/demo/sessions', methods=['POST'])
def create_session():
    """Create a new storytelling session"""
    try:
        data = request.get_json()
        
        session_id = f"session_{len(sessions) + 1}_{int(datetime.now().timestamp())}"
        
        session_data = {
            "session_id": session_id,
            "age": data.get("age", 5),
            "preferences": data.get("preferences", []),
            "emotional_goal": data.get("emotional_goal", "entertain"),
            "voice_preference": data.get("voice_preference"),
            "anonymous_id": data.get("anonymous_id"),
            "name": data.get("name"),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        sessions[session_id] = session_data
        stories[session_id] = []
        
        logger.info(f"Created session: {session_id}")
        
        return jsonify({
            "session_id": session_id,
            "message": "Session created successfully",
            "child_profile": session_data
        })
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({"error": "Failed to create session"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """End a storytelling session"""
    try:
        if session_id in sessions:
            sessions[session_id]["status"] = "ended"
            sessions[session_id]["ended_at"] = datetime.now().isoformat()
            
            story_count = len(stories.get(session_id, []))
            
            logger.info(f"Ended session: {session_id}")
            
            return jsonify({
                "message": "Session ended successfully",
                "session_id": session_id,
                "duration_minutes": 5.0,  # Mock duration
                "total_segments": story_count
            })
        else:
            return jsonify({"error": "Session not found"}), 404
            
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"error": "Failed to end session"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/story', methods=['POST'])
def generate_story(session_id):
    """Generate a story segment"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        theme = data.get("theme", "animals")
        segments_so_far = data.get("segments_so_far", 0)
        child_age = data.get("child_age", 5)
        emotional_goal = data.get("emotional_goal", "entertain")
        language = data.get("language", "es")  # Get language from request
        logger.info(f"🌍 Language received from frontend: {language}")
        # Accept both 'gender' and 'child_gender' for compatibility
        gender = data.get("gender") or data.get("child_gender")
        child_name = sessions.get(session_id, {}).get("name")  # Get name from session
        story_context_full = data.get("story_context", "")
        last_segment = data.get("last_segment", "")
        is_finale = data.get("is_finale", False)
        detected_emotion = data.get("detected_emotion")
        emotion_confidence = data.get("emotion_confidence", 0)
        user_suggestion = data.get("user_suggestion", "")  # User's free-text suggestion
        
        # Always use AWS Bedrock for story generation (demo mode removed)
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        # Get environment and AWS settings
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        try:
            # Use real AWS Bedrock for story generation
            logger.info("📚 Using REAL AWS Bedrock for story generation")
            try:
                from admin.aws_connector import AWSConnector
                
                # Get previous story segments for continuity
                previous_segments = stories.get(session_id, [])
                story_context = ""
                
                if previous_segments:
                    # Build context from previous segments
                    story_context = "\n\nHISTORIA ANTERIOR:\n"
                    for i, segment in enumerate(previous_segments[-3:], 1):  # Last 3 segments for context
                        story_context += f"Segmento {len(previous_segments) - 3 + i}: {segment['text']}\n"
                    story_context += "\nCONTINÚA LA HISTORIA:"
                else:
                    story_context = "\nINICIA UNA NUEVA HISTORIA:"

                # Build gender and name context
                # Normalize gender values (accept both Spanish and English)
                is_female = gender in ["female", "niña", "girl"]
                is_male = gender in ["male", "niño", "boy"]
                
                gender_desc = ""
                if child_name:
                    if is_male:
                        gender_desc = f"El protagonista es un niño llamado {child_name}"
                    elif is_female:
                        gender_desc = f"La protagonista es una niña llamada {child_name}"
                    else:
                        gender_desc = f"El/La protagonista se llama {child_name}"
                else:
                    if is_male:
                        gender_desc = "El protagonista es un niño"
                    elif is_female:
                        gender_desc = "La protagonista es una niña"
                
                finale_instruction = ""
                if is_finale:
                    finale_instruction = """

═══════════════════════════════════════════════════════════════
🎬 CAPÍTULO FINAL - CIERRE OBLIGATORIO 🎬
═══════════════════════════════════════════════════════════════

⚠️ ESTE ES EL ÚLTIMO CAPÍTULO ⚠️

REQUISITOS OBLIGATORIOS:
1. Resuelve TODAS las tramas abiertas
2. Da un cierre satisfactorio y emotivo
3. Muestra cómo el protagonista ha crecido
4. Termina con un momento cálido y reconfortante
5. La ÚLTIMA palabra del capítulo DEBE ser exactamente: FIN

IMPORTANTE: Después de la última frase de la historia, en una nueva línea, escribe:

FIN

═══════════════════════════════════════════════════════════════
"""
                
                emotion_adaptation = ""
                if detected_emotion and emotion_confidence > 0.6:
                    emotion_map = {
                        'happy': 'El niño está feliz, mantén el tono alegre y divertido',
                        'sad': 'El niño está triste, haz la historia más reconfortante y esperanzadora',
                        'angry': 'El niño está enojado, usa un tono calmante y pacífico',
                        'confused': 'El niño está confundido, simplifica y clarifica la narrativa',
                        'surprised': 'El niño está sorprendido, mantén elementos de asombro',
                        'calm': 'El niño está calmado, mantén un ritmo tranquilo',
                        'fear': 'El niño tiene miedo, usa tono muy reconfortante y seguro'
                    }
                    emotion_adaptation = f"\n\nADAPTACIÓN EMOCIONAL (Confianza: {int(emotion_confidence*100)}%):\n{emotion_map.get(detected_emotion, 'Adapta el tono según la emoción detectada')}"
                
                # Add user suggestion if provided - MAKE IT SUPER PROMINENT
                user_suggestion_instruction = ""
                has_user_suggestion = user_suggestion and user_suggestion.strip()
                if has_user_suggestion:
                    user_suggestion_instruction = f"""

═══════════════════════════════════════════════════════════════
🌟🌟🌟 REQUISITO OBLIGATORIO DEL NIÑO 🌟🌟🌟
═══════════════════════════════════════════════════════════════

El niño ha pedido específicamente:
"{user_suggestion.strip()}"

⚠️ ESTO ES OBLIGATORIO ⚠️
Debes incorporar esta sugerencia de manera CENTRAL en el siguiente capítulo.
NO es opcional. El capítulo debe girar en torno a esta idea.
Hazlo de manera natural, creativa y emocionante.

═══════════════════════════════════════════════════════════════
"""
                
                # Build chapter structure guidance
                chapter_guidance = ""
                if segments_so_far == 0:
                    chapter_guidance = """
ESTRUCTURA DEL CAPÍTULO 1 (INICIO):
- Presenta al protagonista y su mundo de manera cautivadora
- Establece el tono mágico y emocionante desde la primera frase
- Introduce un elemento de misterio o aventura que enganche
- Termina con anticipación para el siguiente capítulo
- ⚠️ NO escribas "FIN" - esta NO es la conclusión"""
                elif is_finale:
                    chapter_guidance = """
ESTRUCTURA DEL CAPÍTULO FINAL:
- Resuelve la aventura de manera satisfactoria
- Muestra cómo el protagonista ha crecido o aprendido algo
- Incluye un momento emotivo de celebración o logro
- Termina con un cierre cálido y reconfortante
- ✅ DEBES escribir "FIN" al final"""
                else:
                    chapter_guidance = f"""
ESTRUCTURA DEL CAPÍTULO {segments_so_far + 1}:
- Continúa DIRECTAMENTE desde donde terminó el capítulo anterior
- Desarrolla la trama con un nuevo evento o descubrimiento
- Mantiene el ritmo y la emoción de la historia
- Termina con un gancho que invite a seguir leyendo
- ⚠️ NO escribas "FIN" - la historia continúa"""
                
                # Import story prompts
                from prompts.story_prompts import get_story_prompt
                
                # Build prompt in the selected language
                story_prompt = get_story_prompt(
                    language=language,
                    user_suggestion_instruction=user_suggestion_instruction,
                    gender_desc=gender_desc,
                    child_name=child_name,
                    child_age=child_age,
                    theme=theme,
                    segments_so_far=segments_so_far,
                    emotional_goal=emotional_goal,
                    story_context=story_context,
                    previous_segments=previous_segments,
                    last_segment=last_segment,
                    emotion_adaptation=emotion_adaptation,
                    finale_instruction=finale_instruction,
                    chapter_guidance=chapter_guidance,
                    has_user_suggestion=has_user_suggestion
                )
                
                # Get credentials from config manager
                credentials = config_manager.get_aws_credentials()
                if not credentials:
                    logger.error("❌ No AWS credentials found in config")
                    raise Exception("No AWS credentials configured")
                
                # Initialize AWS connector
                aws_connector = AWSConnector(credentials)
                
                # Generate story using real AWS Bedrock
                # Increased max_tokens to allow complete sentences without truncation
                success, story_text = aws_connector.generate_story_with_bedrock(story_prompt, max_tokens=800)
                
                if not success:
                    logger.error("❌ AWS Bedrock story generation failed")
                    raise Exception("AWS Bedrock failed")
                    
                logger.info("✅ AWS Bedrock story generated successfully")
            
            except Exception as inner_e:
                logger.error(f"❌ Error in AWS Bedrock generation: {inner_e}")
                raise
                
        except Exception as e:
            logger.error(f"❌ Error generating story: {e}")
            return jsonify({"error": "Failed to generate story"}), 500
        
        # Store story segment
        story_segment = {
            "text": story_text,
            "timestamp": datetime.now().isoformat(),
            "theme": theme,
            "segment_number": segments_so_far + 1
        }
        
        stories[session_id].append(story_segment)
        
        logger.info(f"Generated story segment for session: {session_id}")
        
        response_data = {
            "text": story_text,
            "emotional_tone": "cheerful" if emotional_goal == "entertain" else "peaceful",
            "pacing": "moderate",
            "characters_involved": ["Luna", "Búho Sabio"] if theme == "animals" else ["Protagonista"],
            "ai_provider": "Amazon Bedrock (Titan Text)" if using_aws else "Local Templates",
            "ai_type": "aws" if using_aws else "local",
            "environment": environment,
            "cost_status": "AWS costs apply" if using_aws else "Free",
            "message": "Story generated successfully"
        }
        
        response = jsonify(response_data)
        # Add cache prevention headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        return jsonify({"error": "Failed to generate story"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/text-to-speech', methods=['POST'])
def generate_text_to_speech(session_id):
    """Generate text-to-speech audio using AWS Polly"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        text = data.get("text", "")
        language = data.get("language", "es")
        voice_id = data.get("voice_id", None)  # Allow voice selection
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Check if we should use real AWS Polly
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        if using_aws:
            # Use real AWS Polly
            logger.info("🗣️ Using REAL AWS Polly for text-to-speech")
            try:
                from admin.aws_connector import AWSConnector
                
                # Get credentials from config manager
                credentials = config_manager.get_aws_credentials()
                if not credentials:
                    logger.error("❌ No AWS credentials found in config")
                    raise Exception("No AWS credentials configured")
                
                # Initialize AWS connector
                aws_connector = AWSConnector(credentials)
                
                # Generate speech using real AWS Polly
                success, audio_url, message = aws_connector.generate_speech_with_polly(text, language, voice_id)
                
                if success:
                    logger.info("✅ REAL AWS Polly speech generated successfully")
                    return jsonify({
                        "success": True,
                        "audio_data": audio_url,
                        "provider": "Amazon Polly",
                        "voice_used": voice_id or ("Lucia" if language == "es" else "Joanna"),
                        "message": message,
                        "cost_status": "AWS costs apply"
                    })
                else:
                    logger.error("❌ AWS Polly speech generation failed")
                    raise Exception("AWS Polly failed")
                    
            except Exception as e:
                logger.error(f"❌ Real AWS Polly failed: {e}, using fallback")
                # Fallback to browser TTS
                using_aws = False
        
        if not using_aws:
            # Demo mode - return instruction for browser TTS
            logger.info("🗣️ DEMO MODE: Using browser TTS fallback")
            return jsonify({
                "success": False,
                "provider": "Browser TTS",
                "message": "Using browser text-to-speech (demo mode)",
                "fallback": True,
                "cost_status": "Free"
            })
        
    except Exception as e:
        logger.error(f"Error generating text-to-speech: {e}")
        return jsonify({"error": "Failed to generate speech"}), 500

@app.route('/api/v1/demo/available-voices', methods=['GET'])
def get_available_voices():
    """Get available AWS Polly voices"""
    try:
        # Check if we should use real AWS Polly
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        if using_aws:
            # Return AWS Polly voices
            voices = {
                "spanish": [
                    {"id": "Lucia", "name": "Lucía", "gender": "Female", "engine": "neural", "description": "Voz femenina española natural (Neural)"},
                    {"id": "Enrique", "name": "Enrique", "gender": "Male", "engine": "standard", "description": "Voz masculina española natural (Standard)"},
                    {"id": "Conchita", "name": "Conchita", "gender": "Female", "engine": "standard", "description": "Voz femenina española clásica (Standard)"},
                    {"id": "Mia", "name": "Mía", "gender": "Female", "engine": "neural", "description": "Voz femenina mexicana (Neural)"},
                    {"id": "Lupe", "name": "Lupe", "gender": "Female", "engine": "neural", "description": "Voz femenina mexicana joven (Neural)"}
                ],
                "english": [
                    {"id": "Joanna", "name": "Joanna", "gender": "Female", "engine": "neural", "description": "Natural female US voice (Neural)"},
                    {"id": "Matthew", "name": "Matthew", "gender": "Male", "engine": "neural", "description": "Natural male US voice (Neural)"},
                    {"id": "Amy", "name": "Amy", "gender": "Female", "engine": "neural", "description": "British female voice (Neural)"},
                    {"id": "Brian", "name": "Brian", "gender": "Male", "engine": "neural", "description": "British male voice (Neural)"},
                    {"id": "Emma", "name": "Emma", "gender": "Female", "engine": "neural", "description": "British female voice (Neural)"}
                ]
            }
            
            return jsonify({
                "success": True,
                "provider": "Amazon Polly",
                "voices": voices,
                "default": {
                    "spanish": "Lucia",
                    "english": "Joanna"
                }
            })
        else:
            # Return browser TTS info
            return jsonify({
                "success": True,
                "provider": "Browser TTS",
                "voices": {
                    "spanish": [{"id": "es-ES", "name": "Español", "gender": "System", "description": "Voz del sistema"}],
                    "english": [{"id": "en-US", "name": "English", "gender": "System", "description": "System voice"}]
                },
                "default": {
                    "spanish": "es-ES",
                    "english": "en-US"
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting available voices: {e}")
        return jsonify({"error": "Failed to get voices"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/emotion', methods=['POST'])
def emotion_feedback(session_id):
    """Handle emotion feedback"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        emotion = data.get("emotion", "neutral")
        confidence = data.get("confidence", 0.8)
        
        logger.info(f"Received emotion feedback for session {session_id}: {emotion}")
        
        return jsonify({
            "message": "Emotion processed successfully",
            "emotion": emotion,
            "confidence": confidence,
            "adaptation": {
                "action_type": "continue",
                "reason": "Story adapted based on emotion",
                "confidence": 0.8
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing emotion: {e}")
        return jsonify({"error": "Failed to process emotion"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/text-to-speech', methods=['POST'])
def generate_speech(session_id):
    """Generate speech audio using AWS Polly or browser fallback"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        text = data.get("text", "")
        language = data.get("language", "es")
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        logger.info(f"Generating speech for session: {session_id}")
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"Language: {language}")
        
        # Check if we should use AWS Polly
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        if using_aws:
            # Use AWS Polly for high-quality speech
            logger.info("🗣️ Using AWS Polly for speech generation")
            try:
                from admin.aws_connector import AWSConnector
                
                # Get credentials
                credentials = config_manager.get_aws_credentials()
                if not credentials:
                    logger.error("❌ No AWS credentials found")
                    raise Exception("No AWS credentials configured")
                
                # Initialize AWS connector
                aws_connector = AWSConnector(credentials)
                
                # Generate speech with Polly
                success, audio_data, message = aws_connector.generate_speech_with_polly(text, language)
                
                if success:
                    logger.info("✅ AWS Polly speech generated successfully")
                    return jsonify({
                        "success": True,
                        "audio_data": audio_data,
                        "provider": "Amazon Polly",
                        "voice_used": "Lucia" if language == "es" else "Joanna",
                        "quality": "neural",
                        "message": "Speech generated with AWS Polly",
                        "cost_status": "AWS costs apply"
                    })
                else:
                    logger.error(f"❌ AWS Polly failed: {message}")
                    raise Exception(f"AWS Polly failed: {message}")
                    
            except Exception as e:
                logger.warning(f"⚠️ AWS Polly failed: {e}, falling back to browser TTS")
                # Fall through to browser TTS
        
        # Fallback to browser TTS (current behavior)
        logger.info("🗣️ Using browser TTS (fallback)")
        return jsonify({
            "success": True,
            "use_browser_tts": True,
            "provider": "Browser TTS",
            "voice_used": "System default",
            "quality": "basic",
            "message": "Using browser text-to-speech",
            "cost_status": "Free"
        })
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return jsonify({"error": "Failed to generate speech"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/upload-photo', methods=['POST'])
def upload_photo(session_id):
    """Upload user photo and generate storybook avatar using enhanced fallback system"""
    try:
        # Handle null or invalid session_id by creating a temporary one
        if session_id == 'null' or session_id not in sessions:
            # Create a temporary session for photo processing
            temp_session_id = f"temp_photo_{int(datetime.now().timestamp())}"
            sessions[temp_session_id] = {
                "session_id": temp_session_id,
                "age": 6,  # Default age
                "created_at": datetime.now().isoformat(),
                "status": "photo_only"
            }
            session_id = temp_session_id
            logger.info(f"Created temporary session for photo: {session_id}")
        
        data = request.get_json()
        photo_base64 = data.get("photo_base64", "")
        
        if not photo_base64:
            return jsonify({"error": "Photo data is required"}), 400
        
        logger.info(f"Processing photo upload for session: {session_id}")
        
        # Store the photo in the session
        sessions[session_id]["user_photo"] = photo_base64
        
        # Get session age for avatar generation
        session_age = sessions[session_id].get("age", 6)
        
        # Try to detect age and gender with AWS Rekognition FIRST
        detected_age = None
        detected_gender = None
        
        config_manager = ConfigManager()
        try:
            credentials = config_manager.get_aws_credentials()
            if credentials:
                from admin.aws_connector import AWSConnector
                aws_connector = AWSConnector(credentials)
                # Detect age and gender from photo
                photo_bytes = base64.b64decode(photo_base64.split(',')[1] if ',' in photo_base64 else photo_base64)
                logger.info("🔍 Attempting age/gender detection with AWS Rekognition...")
                success, faces = aws_connector.detect_faces(photo_bytes)
                if success and faces:
                    face = faces[0]
                    if 'AgeRange' in face:
                        detected_age = int((face['AgeRange']['Low'] + face['AgeRange']['High']) / 2)
                    if 'Gender' in face:
                        detected_gender = face['Gender']['Value'].lower()
                    logger.info(f"✅ Detected age: {detected_age}, gender: {detected_gender}")
                else:
                    logger.warning("⚠️ No faces detected in photo")
        except Exception as e:
            logger.warning(f"⚠️ Age/gender detection failed: {e}")
        
        # Use enhanced avatar generation with fallback system
        from services.avatar_fallback_controller import avatar_fallback_controller, AvatarRequest
        
        avatar_request = AvatarRequest(
            photo_base64=photo_base64,
            age=session_age,
            theme="fantasy",
            style="cartoon"
        )
        
        # Generate avatar
        result = avatar_fallback_controller.generate_avatar(avatar_request)
        
        if result.success:
            # Store avatar data in session
            sessions[session_id]["avatar_url"] = result.avatar_url
            sessions[session_id]["avatar_method"] = result.method_used.value
            sessions[session_id]["avatar_quality"] = result.quality_score
            if detected_age:
                sessions[session_id]["detected_age"] = detected_age
            if detected_gender:
                sessions[session_id]["detected_gender"] = detected_gender
            
            logger.info(f"✅ Avatar generated successfully using {result.method_used.value}")
            
            return jsonify({
                "success": True,
                "avatar_url": result.avatar_url,
                "provider": result.method_used.value.replace('_', ' ').title(),
                "message": result.message,
                "quality_score": result.quality_score,
                "generation_time": result.generation_time,
                "fallback_used": result.fallback_used,
                "detected_age": detected_age,
                "detected_gender": detected_gender,
                "cost_status": "AWS costs apply" if result.method_used.value == "aws_bedrock" else "Free"
            })
        else:
            logger.error(f"❌ All avatar generation methods failed: {result.message}")
            
            # Still store photo for basic personalization
            return jsonify({
                "success": False,
                "avatar_url": None,
                "provider": "Photo Storage",
                "message": "Avatar generation failed, but photo stored for basic personalization",
                "error": result.message,
                "cost_status": "Free"
            })
        
    except Exception as e:
        logger.error(f"Error processing photo upload: {e}")
        return jsonify({"error": "Failed to process photo"}), 500

def _generate_template_avatar_fallback(child_age: int, photo_base64: str, theme: str = "fantasy") -> Tuple[bool, str, str]:
    """Generate template-based avatar as fallback"""
    try:
        from services.template_avatar_generator import template_avatar_generator
        
        # Try photo-based avatar generation first
        success, avatar_url, message = template_avatar_generator.generate_avatar_from_photo_analysis(
            photo_base64, child_age, theme
        )
        
        if success:
            return True, avatar_url, message
        
        # If photo analysis fails, generate generic avatar
        return template_avatar_generator.generate_generic_avatar(child_age, theme)
        
    except Exception as e:
        logger.error(f"Template avatar fallback failed: {e}")
        return False, "", str(e)

@app.route('/api/v1/upload-photo', methods=['POST'])
def upload_photo_simple():
    """Simple photo upload endpoint that doesn't require a session using enhanced fallback system"""
    try:
        data = request.get_json()
        photo_base64 = data.get("photo_base64", "")
        
        if not photo_base64:
            return jsonify({"error": "Photo data is required"}), 400
        
        logger.info("Processing photo upload (no session required)")
        
        # Detect age and gender with AWS Rekognition FIRST
        detected_age = None
        detected_gender = None
        
        config_manager = ConfigManager()
        try:
            credentials = config_manager.get_aws_credentials()
            if credentials:
                from admin.aws_connector import AWSConnector
                aws_connector = AWSConnector(credentials)
                photo_bytes = base64.b64decode(photo_base64.split(',')[1] if ',' in photo_base64 else photo_base64)
                logger.info("🔍 Attempting age/gender detection with AWS Rekognition...")
                success, faces = aws_connector.detect_faces(photo_bytes)
                if success and faces:
                    face = faces[0]
                    if 'AgeRange' in face:
                        detected_age = int((face['AgeRange']['Low'] + face['AgeRange']['High']) / 2)
                    if 'Gender' in face:
                        detected_gender = face['Gender']['Value'].lower()
                    logger.info(f"✅ Detected age: {detected_age}, gender: {detected_gender}")
                else:
                    logger.warning("⚠️ No faces detected in photo")
        except Exception as e:
            logger.warning(f"⚠️ Age/gender detection failed: {e}")
        
        # Use enhanced avatar generation with fallback system
        from services.avatar_fallback_controller import avatar_fallback_controller, AvatarRequest
        
        avatar_request = AvatarRequest(
            photo_base64=photo_base64,
            age=7,  # Default age for simple endpoint
            theme="fantasy",
            style="cartoon"
        )
        
        result = avatar_fallback_controller.generate_avatar(avatar_request)
        
        if result.success:
            logger.info(f"✅ Avatar generated successfully using {result.method_used.value}")
            
            return jsonify({
                "success": True,
                "avatar_url": result.avatar_url,
                "provider": result.method_used.value.replace('_', ' ').title(),
                "message": result.message,
                "quality_score": result.quality_score,
                "generation_time": result.generation_time,
                "fallback_used": result.fallback_used,
                "detected_age": detected_age,
                "detected_gender": detected_gender,
                "cost_status": "AWS costs apply" if result.method_used.value == "aws_bedrock" else "Free"
            })
        else:
            logger.error(f"❌ All avatar generation methods failed: {result.message}")
            
            return jsonify({
                "success": False,
                "avatar_url": None,
                "provider": "Photo Storage",
                "message": "Avatar generation failed, but photo processed",
                "error": result.message,
                "detected_age": detected_age,
                "detected_gender": detected_gender,
                "cost_status": "Free"
            })
        
    except Exception as e:
        logger.error(f"Error processing photo upload: {e}")
        return jsonify({"error": "Failed to process photo"}), 500

@app.route('/api/v1/demo/sessions/<session_id>/generate-image', methods=['POST'])
def generate_image(session_id):
    """Generate story image with user photo/avatar integration"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        scene_description = data.get("scene_description", "")
        has_user_photo = data.get("has_user_photo", False)
        has_user_avatar = data.get("has_user_avatar", False)
        user_photo_base64 = data.get("user_photo_base64")
        user_avatar_url = data.get("user_avatar_url")
        theme = data.get("theme", "animals")
        style = data.get("style", "children_book")
        child_age = data.get("child_age", 5)
        story_context = data.get("story_context", "")
        gender = data.get("gender")
        
        logger.info(f"Generating image for session: {session_id}")
        logger.info(f"Scene: {scene_description[:50]}...")
        logger.info(f"Has user photo: {has_user_photo}")
        logger.info(f"Has user avatar: {has_user_avatar}")
        logger.info(f"Theme: {theme}")
        
        # Check if we should use AWS for image generation
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws = environment in ['staging', 'production'] and aws_enabled
        
        if using_aws:
            # Use AWS Bedrock Titan for image generation
            logger.info("🎨 Using AWS Bedrock Titan for image generation")
            try:
                from admin.aws_connector import AWSConnector
                
                # Get credentials
                credentials = config_manager.get_aws_credentials()
                if not credentials:
                    logger.error("❌ No AWS credentials found")
                    raise Exception("No AWS credentials configured")
                
                # Initialize AWS connector
                aws_connector = AWSConnector(credentials)
                
                # Create enhanced prompt for image generation
                # Create concise prompt (max 512 characters for AWS Titan)
                base_prompt = f"Children's storybook illustration: {scene_description[:200]}. {theme} theme, magical style, colorful, age-appropriate for {child_age}yr old"
                
                if has_user_avatar and user_avatar_url:
                    # Use avatar as reference for story illustration
                    logger.info("🎭 Using user avatar as reference for story illustration")
                    # Create enhanced prompt with story context
                    from services.aws_prompt_generator import aws_prompt_generator
                    enhanced_prompt = aws_prompt_generator.create_story_image_prompt(
                        scene_description, child_age, True, theme, gender, story_context
                    )
                    success, image_url, message = aws_connector.generate_story_image_with_avatar(
                        enhanced_prompt, user_avatar_url, theme, child_age
                    )
                    
                elif has_user_photo and user_photo_base64:
                    # Use photo as reference for story illustration
                    logger.info("📸 Using user photo as reference for story illustration")
                    # Create enhanced prompt with story context
                    from services.aws_prompt_generator import aws_prompt_generator
                    enhanced_prompt = aws_prompt_generator.create_story_image_prompt(
                        scene_description, child_age, True, theme, gender, story_context
                    )
                    success, image_url, message = aws_connector.generate_story_image_with_photo(
                        enhanced_prompt, user_photo_base64, theme, child_age
                    )
                    
                else:
                    # Generic generation
                    image_prompt = f"{base_prompt}, friendly characters, digital painting style."
                    
                    # Ensure prompt is under 512 characters
                    if len(image_prompt) > 512:
                        image_prompt = image_prompt[:509] + "..."
                    
                    success, image_url, message = aws_connector.generate_image_with_titan(
                        image_prompt
                    )
                
                if success:
                    logger.info("✅ AWS Titan image generated successfully")
                    
                    return jsonify({
                        "success": True,
                        "image_url": image_url,
                        "ai_provider": "Amazon Bedrock Titan",
                        "ai_type": "aws",
                        "environment": environment,
                        "cost_status": "AWS costs apply",
                        "using_aws": True,
                        "has_user_character": has_user_photo or has_user_avatar,
                        "style_applied": style,
                        "generation_time": 3.5,
                        "message": "Image generated with AWS Bedrock"
                    })
                else:
                    logger.error(f"❌ AWS Bedrock image generation failed: {message}")
                    raise Exception(f"AWS Bedrock failed: {message}")
                    
            except Exception as e:
                logger.warning(f"⚠️ AWS image generation failed: {e}, using fallback")
                # Fall through to fallback
        
        # Fallback: Generate enhanced SVG
        logger.info("🎨 Using enhanced SVG fallback")
        
        if has_user_avatar or has_user_photo:
            # Generate personalized SVG
            image_url = generate_personalized_svg(scene_description, theme, style, True)
            provider = "Enhanced SVG with User Character"
        else:
            # Generate themed SVG
            image_url = generate_themed_svg(scene_description, theme, style)
            provider = "Enhanced SVG Generator"
        
        return jsonify({
            "success": True,
            "image_url": image_url,
            "ai_provider": provider,
            "ai_type": "local",
            "environment": environment,
            "cost_status": "Free",
            "using_aws": False,
            "has_user_character": has_user_photo or has_user_avatar,
            "style_applied": style,
            "generation_time": 0.5,
            "message": "Image generated with local SVG generator"
        })
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return jsonify({"error": "Failed to generate image"}), 500
    """Generate story image with user photo integration"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        data = request.get_json()
        scene_description = data.get("scene_description", "")
        has_user_photo = data.get("has_user_photo", False)
        user_photo_base64 = data.get("user_photo_base64")
        theme = data.get("theme", "animals")
        style = data.get("style", "children_book")
        # Accept both 'gender' and 'child_gender' for compatibility
        gender = data.get("gender") or data.get("child_gender")
        
        # Get child age from session
        child_age = sessions[session_id].get("age", 5)
        
        logger.info(f"Generating image for session: {session_id}")
        logger.info(f"Child age: {child_age}")
        logger.info(f"Scene: {scene_description[:50]}...")
        logger.info(f"Has user photo: {has_user_photo}")
        logger.info(f"Theme: {theme}")
        
        # Generate AI image or enhanced SVG fallback
        actual_service_used = "unknown"
        if has_user_photo and user_photo_base64:
            # Generate personalized AI image with user as character
            ai_image, actual_service_used = generate_ai_image_with_tracking(scene_description, theme, style, child_age, True, user_photo_base64, gender)
            logger.info("Generated personalized image with user character")
            has_user_character = True
        else:
            # Generate generic AI image
            ai_image, actual_service_used = generate_ai_image_with_tracking(scene_description, theme, style, child_age, False, None, gender)
            logger.info("Generated generic image")
            has_user_character = False
        
        # Get AI provider info based on what was ACTUALLY used
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        using_aws_config = environment in ['staging', 'production'] and aws_enabled
        
        # Determine provider based on what was ACTUALLY used
        if actual_service_used == "aws_titan":
            # Real AWS Bedrock Titan Image Generator
            message = "Image generated with REAL AWS Bedrock Titan"
            provider = "Amazon Bedrock (Titan Image Generator)"
            ai_type = "aws"
            style_applied = f"{style}_aws_titan"
            generation_time = 4.5
            cost_status = "AWS costs apply"
        elif actual_service_used == "pollinations":
            # Pollinations.ai
            message = "Image generated with Pollinations.ai"
            provider = "Pollinations.ai (Free AI)"
            ai_type = "free_api"
            style_applied = f"{style}_pollinations"
            generation_time = 3.0
            cost_status = "Free"
        elif actual_service_used == "huggingface":
            # Hugging Face
            message = "Image generated with Hugging Face"
            provider = "Hugging Face (Free AI)"
            ai_type = "free_api"
            style_applied = f"{style}_huggingface"
            generation_time = 3.5
            cost_status = "Free"
        else:
            # SVG fallback
            message = "Image generated with enhanced SVG fallback"
            provider = "Enhanced SVG Generator"
            ai_type = "svg_fallback"
            style_applied = f"{style}_enhanced_svg"
            generation_time = 0.8
            cost_status = "Free"
        
        return jsonify({
            "success": True,
            "image_url": ai_image,
            "generation_time": generation_time,
            "prompt_used": scene_description[:100],
            "style_applied": style_applied,
            "has_user_character": has_user_character,
            "message": message,
            "ai_provider": provider,
            "ai_type": ai_type,
            "environment": environment,
            "cost_status": cost_status,
            "using_aws": actual_service_used == "aws_titan",
            "actual_service": actual_service_used,
            "aws_configured": using_aws_config
        })
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return jsonify({"error": "Failed to generate image"}), 500

def generate_ai_image_with_tracking(scene_description, theme, style, child_age, has_user_photo=False, user_photo_base64=None, gender=None):
    """Generate AI image using appropriate service based on configuration and return what was actually used"""
    
    # Check if we should use AWS services
    config_manager = ConfigManager()
    admin_config = config_manager.load_config()
    environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
    aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
    using_aws = environment in ['staging', 'production'] and aws_enabled
    
    if using_aws:
        # Try AWS Titan Image Generator first
        try:
            logger.info("🎨 Attempting to use REAL AWS Titan Image Generator")
            image_url = generate_aws_titan_image(scene_description, theme, child_age, has_user_photo, user_photo_base64, gender)
            logger.info("✅ Successfully used REAL AWS Titan")
            return image_url, "aws_titan"
        except Exception as e:
            logger.warning(f"⚠️ AWS Titan failed: {e}")
            logger.info("🔄 Falling back to free services")
            # Continue to fallback services
    
    # Use free AI services (demo mode or AWS fallback)
    logger.info("🎨 Using free AI services")
    
    # Try Pollinations.ai first (completely free, no API key needed)
    try:
        logger.info("🎨 Attempting Pollinations.ai")
        image_url = generate_pollinations_image(scene_description, theme, child_age, has_user_photo, gender)
        logger.info("✅ Successfully used Pollinations.ai")
        return image_url, "pollinations"
    except Exception as e:
        logger.warning(f"⚠️ Pollinations.ai failed: {e}")
    
    # Try Hugging Face if API key is available
    api_key = os.getenv('HUGGINGFACE_API_KEY', '').strip()
    if api_key and api_key != 'your_huggingface_api_key_here':
        try:
            logger.info("🎨 Attempting Hugging Face")
            image_url = generate_huggingface_image(scene_description, theme, child_age, has_user_photo, api_key, gender)
            logger.info("✅ Successfully used Hugging Face")
            return image_url, "huggingface"
        except Exception as e:
            logger.warning(f"⚠️ Hugging Face failed: {e}")
    
    # Fallback to enhanced SVG
    logger.info("🎨 Using enhanced SVG fallback")
    image_url = generate_enhanced_svg_fallback(scene_description, theme, style, child_age, has_user_photo)
    return image_url, "svg_fallback"

def generate_ai_image(scene_description, theme, style, child_age, has_user_photo=False, user_photo_base64=None, gender=None):
    """Generate AI image using appropriate service based on configuration (legacy function)"""
    image_url, _ = generate_ai_image_with_tracking(scene_description, theme, style, child_age, has_user_photo, user_photo_base64, gender)
    return image_url

def generate_aws_titan_image(scene_description, theme, child_age, has_user_photo, user_photo_base64=None, gender=None):
    """Generate image using AWS Titan Image Generator"""
    
    # Check current environment to decide if we should use real AWS or simulation
    config_manager = ConfigManager()
    admin_config = config_manager.load_config()
    environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
    aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
    
    # Only use real AWS in staging/production with proper credentials
    if environment in ['staging', 'production'] and aws_enabled:
        logger.info("🎨 Using REAL AWS Titan Image Generator")
        
        try:
            # Import AWS connector
            from admin.aws_connector import AWSConnector
            
            # Create enhanced prompt
            base_prompt = create_enhanced_prompt(scene_description, theme, child_age, has_user_photo, gender)
            logger.info(f"🎯 Enhanced prompt for AWS: {base_prompt[:100]}...")
            
            # Get credentials from config manager
            credentials = config_manager.get_aws_credentials()
            if not credentials:
                logger.error("❌ No AWS credentials found in config")
                raise Exception("No AWS credentials configured")
            
            # Initialize AWS connector with admin credentials
            aws_connector = AWSConnector(credentials)
            
            # Generate image using real AWS Titan
            if has_user_photo and user_photo_base64:
                # Use specialized avatar generation with user photo as input
                success, image_url, message = aws_connector.generate_storybook_avatar_with_titan(user_photo_base64, scene_description, child_age)
                logger.info("🎭 Generated personalized storybook avatar from user photo with AWS Titan")
            else:
                # Standard image generation
                success, image_url, message = aws_connector.generate_image_with_titan(base_prompt, "illustration")
            
            if success:
                logger.info("✅ REAL AWS Titan image generated successfully")
                return image_url
            else:
                logger.error(f"❌ AWS Titan generation failed: {message}")
                raise Exception(f"AWS Titan generation failed: {message}")
                
        except Exception as e:
            logger.error(f"❌ Real AWS Titan failed: {e}")
            raise Exception(f"AWS Titan service error: {e}")
    
    else:
        # Demo mode - use simulation for testing
        logger.info("🎨 DEMO MODE: Simulating AWS Titan Image Generator")
        
        # Create enhanced prompt (this part works for testing)
        base_prompt = create_enhanced_prompt(scene_description, theme, child_age, has_user_photo, gender)
        logger.info(f"🎯 Enhanced prompt created (demo): {base_prompt[:100]}...")
        
        # Simulate AWS response with a simple base64 image for demo
        import base64
        
        # Create a simple test image (1x1 pixel) to simulate AWS response
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        image_base64 = base64.b64encode(test_image_data).decode('utf-8')
        
        logger.info("✅ DEMO AWS image simulation completed")
        
        return f"data:image/png;base64,{image_base64}"

def generate_pollinations_image(scene_description, theme, child_age, has_user_photo, gender=None):
    """Generate image using Pollinations.ai (free, no API key needed)"""
    
    # Create enhanced prompt for children's book illustration
    base_prompt = create_enhanced_prompt(scene_description, theme, child_age, has_user_photo, gender)
    
    logger.info(f"🎨 Generating AI image with Pollinations.ai: {base_prompt[:100]}...")
    
    # Pollinations.ai URL - completely free
    # URL encode the prompt
    import urllib.parse
    encoded_prompt = urllib.parse.quote(base_prompt)
    
    # Pollinations.ai endpoint
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed=-1&model=flux"
    
    # Make request
    response = requests.get(pollinations_url, timeout=30)
    
    if response.status_code == 200:
        # Validate image data
        image_bytes = response.content
        
        # Check if we got valid image data
        if len(image_bytes) < 100:  # Too small to be a valid image
            raise Exception("Received image data is too small")
            
        # Try to validate it's a proper image using PIL
        try:
            from PIL import Image
            import io
            image_stream = io.BytesIO(image_bytes)
            img = Image.open(image_stream)
            img.verify()  # Verify it's a valid image
            logger.info(f"✅ Image validation passed: {img.format} {img.size}")
        except Exception as img_error:
            logger.warning(f"⚠️ Image validation failed: {img_error}")
            raise Exception(f"Invalid image data received: {img_error}")
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        logger.info("✅ AI image generated successfully with Pollinations.ai")
        return f"data:image/jpeg;base64,{image_base64}"
    else:
        raise Exception(f"Pollinations.ai returned status {response.status_code}")

def generate_huggingface_image(scene_description, theme, child_age, has_user_photo, api_key, gender=None):
    """Generate image using Hugging Face API"""
    
    # Hugging Face API configuration
    HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    # Create enhanced prompt for children's book illustration
    base_prompt = create_enhanced_prompt(scene_description, theme, child_age, has_user_photo, gender)
    
    logger.info(f"🎨 Generating AI image with Hugging Face: {base_prompt[:100]}...")
    
    # Call Hugging Face API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": base_prompt,
        "parameters": {
            "negative_prompt": "ugly, blurry, low quality, distorted, scary, dark, violent, inappropriate, adult content",
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    
    # Make API request
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        # Convert image to base64
        image_bytes = response.content
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        logger.info("✅ AI image generated successfully with Hugging Face")
        return f"data:image/jpeg;base64,{image_base64}"
    else:
        if response.status_code == 401:
            logger.warning("🔑 Invalid Hugging Face API key")
        raise Exception(f"Hugging Face returned status {response.status_code}")

def create_enhanced_prompt(scene_description, theme, child_age, has_user_photo, gender=None):
    """Create enhanced prompt for AI image generation adapted to child's age and gender"""
    
    # Normalize gender values
    is_female = gender in ["female", "niña", "girl"] if gender else False
    is_male = gender in ["male", "niño", "boy"] if gender else False
    
    # Gender-specific descriptors
    if is_female:
        gender_desc = "girl"
        pronoun = "her"
    elif is_male:
        gender_desc = "boy"
        pronoun = "his"
    else:
        gender_desc = "child"
        pronoun = "their"
    
    # Age-appropriate style adjustments with more realistic approach
    if child_age <= 3:
        # Toddlers (0-3): Simple but realistic, soft features
        style_prompt = "realistic children's illustration with soft features, gentle colors, simple composition, safe and comforting, photorealistic but child-friendly"
        complexity = "simple"
        character_style = f"realistic {gender_desc} toddler with soft features and big expressive eyes"
    elif child_age <= 5:
        # Preschoolers (4-5): Semi-realistic, engaging
        style_prompt = "semi-realistic children's book illustration, natural colors, detailed but clear, engaging and magical, photorealistic style"
        complexity = "simple"
        character_style = f"realistic {gender_desc} preschooler with natural features and expressive face"
    elif child_age <= 8:
        # Early elementary (6-8): Realistic with magical elements
        style_prompt = "realistic children's fantasy illustration, natural lighting, detailed environments, magical elements, photorealistic with enchanting atmosphere"
        complexity = "moderate"
        character_style = f"realistic {gender_desc} child with natural proportions and expressive personality"
    elif child_age <= 12:
        # Late elementary (9-12): High-quality realistic
        style_prompt = "high-quality realistic children's fantasy art, cinematic lighting, detailed backgrounds, adventure elements, photorealistic digital art"
        complexity = "detailed"
        character_style = f"realistic {gender_desc} character with detailed features and natural expressions"
    else:
        # Teens (13+): Fully realistic, sophisticated
        style_prompt = "photorealistic fantasy illustration, cinematic quality, complex composition, mature themes, professional digital art"
        complexity = "complex"
        character_style = f"realistic {gender_desc} teenager with detailed facial features and natural expressions"
        style_prompt = "young adult book illustration, realistic style, complex composition, mature themes, artistic quality"
        complexity = "complex"
        character_style = f"realistic {gender_desc} characters with depth and emotion"
    
    # Age-appropriate theme elements
    age_appropriate_themes = {
        "animals": {
            "simple": "big friendly animal faces, simple forest, bright flowers",
            "moderate": "cute forest animals playing, magical woodland, colorful nature",
            "detailed": "diverse forest creatures, enchanted woodland scenes, detailed nature",
            "complex": "realistic wildlife in natural habitats, conservation themes"
        },
        "fantasy": {
            "simple": "friendly dragon, simple castle, rainbow colors",
            "moderate": "magical castle, fairy tale creatures, sparkles and magic",
            "detailed": "enchanted kingdoms, mythical creatures, magical adventures",
            "complex": "epic fantasy realms, complex magical systems, heroic quests"
        },
        "adventure": {
            "simple": "treasure chest, simple boat, sunny day",
            "moderate": "treasure hunt, friendly pirates, exciting exploration",
            "detailed": "epic adventures, mysterious islands, brave explorers",
            "complex": "challenging expeditions, survival themes, personal growth"
        },
        "friendship": {
            "simple": "children holding hands, happy faces, playground",
            "moderate": "friends playing together, sharing toys, helping each other",
            "detailed": "diverse friendships, teamwork adventures, social bonds",
            "complex": "deep friendships, loyalty themes, social challenges"
        }
    }
    
    theme_addition = age_appropriate_themes.get(theme, age_appropriate_themes["animals"])[complexity]
    
    # Enhanced professional storybook avatar with personalized character integration
    if has_user_photo:
        if child_age <= 5:
            character_prompt = f"""featuring a beautifully illustrated storybook character: a charming young {gender_desc} protagonist with distinctive facial features, unique hair color and style, transformed into a professional children's book illustration. The {gender_desc} has expressive eyes, whimsical hair styling, warm facial structure and smile, dressed in beautiful age-appropriate storybook clothing, with inviting expression, {character_style}, seamlessly integrated as the main character"""
        elif child_age <= 8:
            character_prompt = f"""featuring a professionally illustrated storybook avatar: an adventurous young {gender_desc} protagonist who maintains distinctive facial features, unique hair characteristics, rendered in high-quality children's book art style. The {gender_desc} has precise facial features, authentic hair color and style, genuine personality reflected in expression, elegant adventure-ready clothing, {character_style}, perfectly integrated as the story's hero"""
        elif child_age <= 12:
            character_prompt = f"""featuring a masterfully crafted storybook character portrait: a brave young {gender_desc} protagonist whose illustration captures distinctive features while achieving professional children's literature standards. The {gender_desc} has unique facial features, authentic hair representation, personality shining through, sophisticated story-appropriate attire, {character_style}, positioned as the story's protagonist"""
        else:
            character_prompt = f"""featuring an expertly illustrated young hero: a courageous {gender_desc} protagonist whose portrait maintains distinctive features while achieving award-winning children's literature quality. The {gender_desc} has unique facial accuracy, authentic hair representation, individual character and confidence captured, mature adventure-appropriate clothing, {character_style}, established as the story's leader"""
    else:
        character_prompt = f"with {character_style}, age-appropriate for young readers"
    
    # Age-appropriate safety and content filters
    if child_age <= 5:
        safety_prompt = "completely safe for toddlers, no scary elements, only happy content"
    elif child_age <= 8:
        safety_prompt = "safe for young children, gentle adventures, positive emotions"
    elif child_age <= 12:
        safety_prompt = "appropriate for children, mild adventure elements, educational value"
    else:
        safety_prompt = "age-appropriate content, meaningful themes, inspiring messages"
    
    # Combine all elements with age consideration
    full_prompt = f"{style_prompt}, {scene_description}, {theme_addition}, {character_prompt}, {safety_prompt}, high quality digital art"
    
    logger.info(f"🎯 Age-adapted prompt for {child_age}yr old: {complexity} complexity")
    
    return full_prompt

def generate_enhanced_svg_fallback(scene_description, theme, style, child_age, has_user_photo):
    """Generate enhanced SVG as fallback when AI fails"""
    
    logger.info(f"🎨 Generating age-appropriate SVG fallback for {child_age}yr old")
    
    # Age-appropriate color schemes
    if child_age <= 3:
        # Toddlers: Very bright, high contrast, primary colors
        theme_colors = {
            "animals": {"bg": "#FFD700", "ground": "#32CD32", "accent": "#FF69B4", "character": "#FF6347"},
            "fantasy": {"bg": "#FF1493", "ground": "#00FF00", "accent": "#FFD700", "character": "#FF69B4"},
            "adventure": {"bg": "#00BFFF", "ground": "#FFD700", "accent": "#FF4500", "character": "#32CD32"},
            "friendship": {"bg": "#FF69B4", "ground": "#32CD32", "accent": "#FFD700", "character": "#FF6347"}
        }
    elif child_age <= 5:
        # Preschoolers: Bright, cheerful colors
        theme_colors = {
            "animals": {"bg": "#87CEEB", "ground": "#90EE90", "accent": "#FFB6C1", "character": "#FFA07A"},
            "fantasy": {"bg": "#DDA0DD", "ground": "#98FB98", "accent": "#F0E68C", "character": "#FFB6C1"},
            "adventure": {"bg": "#87CEFA", "ground": "#F4A460", "accent": "#32CD32", "character": "#FF6347"},
            "friendship": {"bg": "#FFB6C1", "ground": "#98FB98", "accent": "#87CEEB", "character": "#FFA07A"}
        }
    elif child_age <= 8:
        # Elementary: Balanced, engaging colors
        theme_colors = {
            "animals": {"bg": "#4682B4", "ground": "#228B22", "accent": "#DA70D6", "character": "#CD853F"},
            "fantasy": {"bg": "#9370DB", "ground": "#3CB371", "accent": "#DAA520", "character": "#DB7093"},
            "adventure": {"bg": "#4169E1", "ground": "#D2691E", "accent": "#228B22", "character": "#DC143C"},
            "friendship": {"bg": "#DB7093", "ground": "#3CB371", "accent": "#4682B4", "character": "#CD853F"}
        }
    else:
        # Older kids: More sophisticated, muted colors
        theme_colors = {
            "animals": {"bg": "#2F4F4F", "ground": "#556B2F", "accent": "#8B4789", "character": "#A0522D"},
            "fantasy": {"bg": "#483D8B", "ground": "#2E8B57", "accent": "#B8860B", "character": "#8B4789"},
            "adventure": {"bg": "#191970", "ground": "#8B4513", "accent": "#006400", "character": "#8B0000"},
            "friendship": {"bg": "#8B4789", "ground": "#2E8B57", "accent": "#2F4F4F", "character": "#A0522D"}
        }
    
    colors = theme_colors.get(theme, theme_colors["animals"])
    
    # Create detailed SVG
    svg_content = f'''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="skyGrad" cx="50%" cy="20%" r="80%">
                <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:1" />
                <stop offset="100%" style="stop-color:{colors["bg"]};stop-opacity:1" />
            </radialGradient>
            <linearGradient id="groundGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{colors["ground"]};stop-opacity:1" />
                <stop offset="100%" style="stop-color:#228B22;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.3"/>
            </filter>
        </defs>
        
        <!-- Sky background -->
        <rect width="512" height="350" fill="url(#skyGrad)"/>
        
        <!-- Ground -->
        <rect y="350" width="512" height="162" fill="url(#groundGrad)"/>
        
        <!-- Sun -->
        <circle cx="450" cy="80" r="30" fill="#FFD700" filter="url(#shadow)"/>
        
        <!-- Clouds -->
        <ellipse cx="150" cy="100" rx="40" ry="20" fill="#FFF" opacity="0.8"/>
        <ellipse cx="320" cy="120" rx="35" ry="18" fill="#FFF" opacity="0.8"/>
        
        {get_enhanced_theme_elements(theme, colors, child_age, has_user_photo)}
        
        <!-- Magical sparkles -->
        <circle cx="100" cy="150" r="3" fill="#FFD700" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="400" cy="200" r="2" fill="#FFF" opacity="0.9">
            <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="200" cy="180" r="2" fill="#FFD700" opacity="0.7">
            <animate attributeName="opacity" values="0.4;1;0.4" dur="2.5s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Title -->
        <rect x="50" y="450" width="412" height="50" fill="#FFF" opacity="0.9" rx="10"/>
        <text x="256" y="480" font-family="Arial, sans-serif" font-size="18" font-weight="bold" 
              text-anchor="middle" fill="#2C3E50">✨ Historia Ilustrada con IA ✨</text>
    </svg>'''
    
    # Convert to base64
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

def get_enhanced_theme_elements(theme, colors, child_age, has_user_photo):
    """Get enhanced SVG elements for each theme adapted to child's age"""
    
    # Age-appropriate character sizing and features
    if child_age <= 3:
        # Toddlers: Bigger, simpler characters
        char_size = {"body_rx": 35, "body_ry": 50, "head_r": 30, "eye_r": 6}
        char_pos = {"x": 256, "y": 280}
    elif child_age <= 5:
        # Preschoolers: Standard cute proportions
        char_size = {"body_rx": 30, "body_ry": 45, "head_r": 25, "eye_r": 4}
        char_pos = {"x": 256, "y": 300}
    elif child_age <= 8:
        # Elementary: More proportional
        char_size = {"body_rx": 25, "body_ry": 40, "head_r": 22, "eye_r": 3}
        char_pos = {"x": 256, "y": 320}
    else:
        # Older kids: More realistic proportions
        char_size = {"body_rx": 22, "body_ry": 38, "head_r": 20, "eye_r": 3}
        char_pos = {"x": 256, "y": 330}
    
    # Character element
    if has_user_photo:
        character = f'''
            <!-- User character (age {child_age}) -->
            <g transform="translate({char_pos["x"]}, {char_pos["y"]})" filter="url(#shadow)">
                <!-- Body -->
                <ellipse cx="0" cy="20" rx="{char_size["body_rx"]}" ry="{char_size["body_ry"]}" fill="{colors["character"]}"/>
                <!-- Head -->
                <circle cx="0" cy="-25" r="{char_size["head_r"]}" fill="#FDBCB4"/>
                <!-- Eyes -->
                <circle cx="-10" cy="-30" r="{char_size["eye_r"]}" fill="#2C3E50"/>
                <circle cx="10" cy="-30" r="{char_size["eye_r"]}" fill="#2C3E50"/>
                <!-- Smile -->
                <path d="M -12,-18 Q 0,-12 12,-18" stroke="#E74C3C" stroke-width="3" fill="none"/>
                <!-- Hair -->
                <ellipse cx="0" cy="-45" rx="22" ry="12" fill="#8B4513"/>
                <!-- Arms -->
                <ellipse cx="-25" cy="0" rx="12" ry="30" fill="{colors["character"]}" opacity="0.9"/>
                <ellipse cx="25" cy="0" rx="12" ry="30" fill="{colors["character"]}" opacity="0.9"/>
                <!-- Legs -->
                <ellipse cx="-15" cy="55" rx="12" ry="35" fill="{colors["character"]}" opacity="0.9"/>
                <ellipse cx="15" cy="55" rx="12" ry="35" fill="{colors["character"]}" opacity="0.9"/>
            </g>
        '''
    else:
        character = f'''
            <!-- Generic character (age {child_age}) -->
            <g transform="translate({char_pos["x"]}, {char_pos["y"] + 20})" filter="url(#shadow)">
                <ellipse cx="0" cy="0" rx="{char_size["body_rx"] - 5}" ry="{char_size["body_ry"] - 10}" fill="{colors["character"]}"/>
                <circle cx="0" cy="-20" r="{char_size["head_r"] - 3}" fill="#FDBCB4"/>
                <circle cx="-8" cy="-25" r="{char_size["eye_r"] - 1}" fill="#2C3E50"/>
                <circle cx="8" cy="-25" r="{char_size["eye_r"] - 1}" fill="#2C3E50"/>
                <path d="M -8,-15 Q 0,-10 8,-15" stroke="#E74C3C" stroke-width="2" fill="none"/>
            </g>
        '''
    
    elements = {
        "animals": f'''
            {character}
            <!-- Trees -->
            <g filter="url(#shadow)">
                <rect x="80" y="280" width="15" height="70" fill="#8B4513"/>
                <circle cx="87" cy="270" r="35" fill="#228B22"/>
                <rect x="400" y="290" width="12" height="60" fill="#8B4513"/>
                <circle cx="406" cy="280" r="30" fill="#228B22"/>
            </g>
            
            <!-- Animals -->
            <g transform="translate(150, 380)" filter="url(#shadow)">
                <!-- Rabbit -->
                <ellipse cx="0" cy="0" rx="20" ry="15" fill="#FFF"/>
                <circle cx="-5" cy="-8" r="8" fill="#FFF"/>
                <ellipse cx="-8" cy="-15" rx="3" ry="8" fill="#FFB6C1"/>
                <ellipse cx="-2" cy="-15" rx="3" ry="8" fill="#FFB6C1"/>
                <circle cx="-8" cy="-10" r="2" fill="#000"/>
            </g>
            
            <!-- Flowers -->
            <g>
                <circle cx="180" cy="400" r="8" fill="#FF69B4"/>
                <circle cx="320" cy="420" r="6" fill="#FFB6C1"/>
                <circle cx="120" cy="430" r="7" fill="#FF1493"/>
            </g>
        ''',
        
        "fantasy": f'''
            {character}
            <!-- Castle -->
            <g filter="url(#shadow)">
                <rect x="350" y="200" width="80" height="150" fill="#708090"/>
                <rect x="340" y="180" width="25" height="80" fill="#708090"/>
                <rect x="415" y="180" width="25" height="80" fill="#708090"/>
                <polygon points="380,180 390,160 400,180" fill="#DC143C"/>
                <polygon points="352,180 362,160 372,180" fill="#DC143C"/>
                <polygon points="427,180 437,160 447,180" fill="#DC143C"/>
            </g>
            
            <!-- Magic elements -->
            <g>
                <polygon points="150,150 160,180 180,180 165,195 170,220 150,205 130,220 135,195 120,180 140,180" fill="#FFD700"/>
                <circle cx="200" cy="100" r="4" fill="#FF69B4" opacity="0.8">
                    <animate attributeName="r" values="2;6;2" dur="2s" repeatCount="indefinite"/>
                </circle>
            </g>
        ''',
        
        "adventure": f'''
            {character}
            <!-- Mountains -->
            <g filter="url(#shadow)">
                <polygon points="100,250 150,150 200,250" fill="#696969"/>
                <polygon points="300,260 360,160 420,260" fill="#696969"/>
                <polygon points="140,150 150,130 160,150" fill="#FFF"/>
                <polygon points="350,160 360,140 370,160" fill="#FFF"/>
            </g>
            
            <!-- Adventure path -->
            <path d="M 50 400 Q 150 380 250 400 Q 350 420 450 400" stroke="#8B4513" stroke-width="8" fill="none"/>
            
            <!-- Treasure chest -->
            <g transform="translate(400, 380)" filter="url(#shadow)">
                <rect x="-15" y="-10" width="30" height="20" fill="#8B4513"/>
                <rect x="-12" y="-8" width="24" height="16" fill="#FFD700"/>
                <circle cx="0" cy="0" r="3" fill="#FF6347"/>
            </g>
        ''',
        
        "friendship": f'''
            {character}
            <!-- Friend characters -->
            <g transform="translate(180, 320)" filter="url(#shadow)">
                <ellipse cx="0" cy="0" rx="20" ry="30" fill="#87CEEB"/>
                <circle cx="0" cy="-18" r="15" fill="#FDBCB4"/>
                <circle cx="-6" cy="-22" r="2" fill="#2C3E50"/>
                <circle cx="6" cy="-22" r="2" fill="#2C3E50"/>
                <path d="M -6,-12 Q 0,-8 6,-12" stroke="#E74C3C" stroke-width="2" fill="none"/>
            </g>
            
            <g transform="translate(330, 320)" filter="url(#shadow)">
                <ellipse cx="0" cy="0" rx="20" ry="30" fill="#98FB98"/>
                <circle cx="0" cy="-18" r="15" fill="#FDBCB4"/>
                <circle cx="-6" cy="-22" r="2" fill="#2C3E50"/>
                <circle cx="6" cy="-22" r="2" fill="#2C3E50"/>
                <path d="M -6,-12 Q 0,-8 6,-12" stroke="#E74C3C" stroke-width="2" fill="none"/>
            </g>
            
            <!-- Heart -->
            <path d="M 256,200 C 246,190 226,190 226,210 C 226,230 256,250 256,250 C 256,250 286,230 286,210 C 286,190 266,190 256,200 Z" 
                  fill="#FF69B4" filter="url(#shadow)"/>
        '''
    }
    
    return elements.get(theme, elements["animals"])

def generate_personalized_svg(scene_description, theme, style, has_user=False):
    """Generate personalized SVG with user as main character"""
    
    # Enhanced color schemes based on theme
    theme_colors = {
        "animals": {"bg": "#4ECDC4", "accent": "#45B7B8", "character": "#FF6B6B", "secondary": "#FDCB6E"},
        "fantasy": {"bg": "#A29BFE", "accent": "#6C5CE7", "character": "#FD79A8", "secondary": "#FDCB6E"},
        "adventure": {"bg": "#FDCB6E", "accent": "#E17055", "character": "#00B894", "secondary": "#74B9FF"},
        "friendship": {"bg": "#FD79A8", "accent": "#E84393", "character": "#A29BFE", "secondary": "#00CEC9"}
    }
    
    colors = theme_colors.get(theme, theme_colors["animals"])
    
    # Create more detailed SVG with user character
    svg_content = f'''<svg width="512" height="384" viewBox="0 0 512 384" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bgGrad" cx="50%" cy="30%" r="80%">
                <stop offset="0%" style="stop-color:{colors["bg"]};stop-opacity:0.9" />
                <stop offset="70%" style="stop-color:{colors["accent"]};stop-opacity:0.7" />
                <stop offset="100%" style="stop-color:{colors["secondary"]};stop-opacity:1" />
            </radialGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background -->
        <rect width="512" height="384" fill="url(#bgGrad)" rx="20"/>
        
        <!-- Ground -->
        <ellipse cx="256" cy="350" rx="200" ry="25" fill="{colors["accent"]}" opacity="0.4"/>
        
        <!-- User Character (enhanced when photo provided) -->
        <g transform="translate(200, 200)">
            <!-- Body -->
            <ellipse cx="0" cy="20" rx="25" ry="35" fill="{colors["character"]}" opacity="0.9"/>
            <!-- Head -->
            <circle cx="0" cy="-20" r="20" fill="#FDBCB4" stroke="{colors["character"]}" stroke-width="2"/>
            <!-- Eyes -->
            <circle cx="-8" cy="-25" r="3" fill="#2D3436"/>
            <circle cx="8" cy="-25" r="3" fill="#2D3436"/>
            <!-- Smile -->
            <path d="M -8,-15 Q 0,-10 8,-15" stroke="#2D3436" stroke-width="2" fill="none"/>
            <!-- Hair -->
            <ellipse cx="0" cy="-35" rx="18" ry="8" fill="#8B4513"/>
            <!-- Arms -->
            <ellipse cx="-20" cy="5" rx="8" ry="20" fill="{colors["character"]}" opacity="0.8"/>
            <ellipse cx="20" cy="5" rx="8" ry="20" fill="{colors["character"]}" opacity="0.8"/>
            <!-- Legs -->
            <ellipse cx="-10" cy="45" rx="8" ry="25" fill="{colors["character"]}" opacity="0.8"/>
            <ellipse cx="10" cy="45" rx="8" ry="25" fill="{colors["character"]}" opacity="0.8"/>
        </g>
        
        <!-- Theme elements -->
        {get_theme_elements(theme, colors)}
        
        <!-- Magical sparkles -->
        <circle cx="100" cy="100" r="4" fill="#FDCB6E" opacity="0.8" filter="url(#glow)"/>
        <circle cx="400" cy="120" r="3" fill="#FFF" opacity="0.9" filter="url(#glow)"/>
        <circle cx="450" cy="200" r="2" fill="#FDCB6E" opacity="0.7"/>
        <circle cx="80" cy="250" r="3" fill="#FFF" opacity="0.6"/>
        
        <!-- Title -->
        <text x="256" y="370" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
              text-anchor="middle" fill="#FFF" opacity="0.9">¡Tu Historia Personalizada!</text>
    </svg>'''
    
    # Convert to base64
    import base64
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

def generate_themed_svg(scene_description, theme, style):
    """Generate generic themed SVG without user character"""
    
    theme_colors = {
        "animals": {"bg": "#4ECDC4", "accent": "#45B7B8", "secondary": "#FDCB6E"},
        "fantasy": {"bg": "#A29BFE", "accent": "#6C5CE7", "secondary": "#FD79A8"},
        "adventure": {"bg": "#FDCB6E", "accent": "#E17055", "secondary": "#00B894"},
        "friendship": {"bg": "#FD79A8", "accent": "#E84393", "secondary": "#A29BFE"}
    }
    
    colors = theme_colors.get(theme, theme_colors["animals"])
    
    svg_content = f'''<svg width="512" height="384" viewBox="0 0 512 384" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <radialGradient id="bgGrad" cx="50%" cy="30%" r="80%">
                <stop offset="0%" style="stop-color:{colors["bg"]};stop-opacity:0.9" />
                <stop offset="70%" style="stop-color:{colors["accent"]};stop-opacity:0.7" />
                <stop offset="100%" style="stop-color:{colors["secondary"]};stop-opacity:1" />
            </radialGradient>
        </defs>
        
        <rect width="512" height="384" fill="url(#bgGrad)" rx="20"/>
        <ellipse cx="256" cy="350" rx="180" ry="20" fill="{colors["accent"]}" opacity="0.4"/>
        
        {get_theme_elements(theme, colors)}
        
        <circle cx="150" cy="150" r="6" fill="#FFF" opacity="0.7"/>
        <circle cx="380" cy="180" r="4" fill="#FFF" opacity="0.8"/>
        <circle cx="300" cy="120" r="3" fill="#FDCB6E" opacity="0.9"/>
        
        <text x="256" y="370" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
              text-anchor="middle" fill="#FFF" opacity="0.8">Historia Ilustrada</text>
    </svg>'''
    
    import base64
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

def get_theme_elements(theme, colors):
    """Get SVG elements specific to each theme"""
    
    elements = {
        "animals": f'''
            <!-- Trees -->
            <ellipse cx="100" cy="280" rx="20" ry="40" fill="#2D3436"/>
            <circle cx="100" cy="250" r="25" fill="#00B894"/>
            <ellipse cx="400" cy="290" rx="18" ry="35" fill="#2D3436"/>
            <circle cx="400" cy="265" r="22" fill="#00B894"/>
            
            <!-- Animals -->
            <ellipse cx="180" cy="280" rx="15" ry="10" fill="{colors["secondary"]}"/>
            <circle cx="175" cy="275" r="8" fill="{colors["secondary"]}"/>
            <circle cx="172" cy="272" r="2" fill="#2D3436"/>
        ''',
        
        "fantasy": f'''
            <!-- Castle -->
            <rect x="350" y="200" width="60" height="80" fill="#636E72"/>
            <rect x="340" y="180" width="20" height="50" fill="#636E72"/>
            <rect x="420" y="180" width="20" height="50" fill="#636E72"/>
            <polygon points="380,180 390,160 400,180" fill="{colors["secondary"]}"/>
            
            <!-- Magic stars -->
            <polygon points="200,120 205,135 220,135 208,145 213,160 200,150 187,160 192,145 180,135 195,135" fill="#FDCB6E"/>
        ''',
        
        "adventure": f'''
            <!-- Mountains -->
            <polygon points="150,250 180,180 220,250" fill="#636E72"/>
            <polygon points="300,260 340,190 380,260" fill="#636E72"/>
            
            <!-- Sun -->
            <circle cx="400" cy="100" r="25" fill="#FDCB6E"/>
            
            <!-- Path -->
            <path d="M 50 300 Q 150 280 250 300 Q 350 320 450 300" stroke="{colors["accent"]}" stroke-width="4" fill="none"/>
        ''',
        
        "friendship": f'''
            <!-- Characters -->
            <circle cx="180" cy="250" r="15" fill="{colors["secondary"]}" opacity="0.8"/>
            <circle cx="220" cy="255" r="12" fill="{colors["accent"]}" opacity="0.8"/>
            
            <!-- Heart -->
            <path d="M 200,200 C 195,195 185,195 185,205 C 185,215 200,225 200,225 C 200,225 215,215 215,205 C 215,195 205,195 200,200 Z" fill="#E74C3C"/>
            
            <!-- Connection -->
            <path d="M 180 250 Q 200 230 220 255" stroke="#FFF" stroke-width="3" fill="none" opacity="0.7"/>
        '''
    }
    
    return elements.get(theme, elements["animals"])


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 Starting DreamAIry Backend Server")
    logger.info(f"📡 Server will run on http://localhost:{port}")
    logger.info("🎭 Running in demo mode with mock AI services")
    logger.info("💡 Frontend should connect to this server")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

@app.route('/api/v1/detect-emotion', methods=['POST', 'OPTIONS'])
def detect_emotion():
    """Detect emotion from photo using AWS Rekognition"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info("🎭 ===== DETECT EMOTION ENDPOINT CALLED =====")
        data = request.get_json()
        photo_base64 = data.get("photo_base64", "")
        
        if not photo_base64:
            logger.warning("⚠️ No photo data provided")
            return jsonify({"error": "Photo data is required"}), 400
        
        logger.info(f"📸 Photo received (length: {len(photo_base64)} chars)")
        config_manager = ConfigManager()
        credentials = config_manager.get_aws_credentials()
        
        if not credentials:
            logger.warning("⚠️ AWS credentials not configured - returning failure")
            return jsonify({"success": False, "message": "AWS not configured"}), 200
        
        logger.info("✅ AWS credentials found, initializing Rekognition...")
        from admin.aws_connector import AWSConnector
        aws_connector = AWSConnector(credentials)
        photo_bytes = base64.b64decode(photo_base64.split(',')[1] if ',' in photo_base64 else photo_base64)
        
        logger.info("🔍 Calling AWS Rekognition detect_faces...")
        success, faces = aws_connector.detect_faces(photo_bytes)
        
        if not success or not faces:
            logger.warning("⚠️ No face detected in photo")
            return jsonify({"success": False, "message": "No face detected"}), 200
        
        logger.info(f"👤 Face detected! Analyzing emotions...")
        face = faces[0]
        emotions = face.get('Emotions', [])
        
        if not emotions:
            logger.warning("⚠️ No emotions detected in face")
            return jsonify({"success": False, "message": "No emotions detected"}), 200
        
        top_emotion = max(emotions, key=lambda e: e['Confidence'])
        logger.info(f"😊 Top emotion detected: {top_emotion['Type']} ({top_emotion['Confidence']:.1f}%)")
        
        emotion_map = {
            'HAPPY': {'label': 'Feliz', 'icon': '😊', 'influence': 'entertain'},
            'SAD': {'label': 'Triste', 'icon': '😢', 'influence': 'calm'},
            'ANGRY': {'label': 'Enojado', 'icon': '😠', 'influence': 'calm'},
            'CONFUSED': {'label': 'Confundido', 'icon': '😕', 'influence': 'entertain'},
            'DISGUSTED': {'label': 'Disgustado', 'icon': '🤢', 'influence': 'entertain'},
            'SURPRISED': {'label': 'Sorprendido', 'icon': '😲', 'influence': 'entertain'},
            'CALM': {'label': 'Calmado', 'icon': '😌', 'influence': 'calm'},
            'FEAR': {'label': 'Asustado', 'icon': '😨', 'influence': 'calm'}
        }
        
        emotion_type = top_emotion['Type']
        emotion_info = emotion_map.get(emotion_type, {'label': 'Neutral', 'icon': '😐', 'influence': 'entertain'})
        
        return jsonify({
            "success": True,
            "emotion": emotion_type.lower(),
            "label": emotion_info['label'],
            "icon": emotion_info['icon'],
            "confidence": top_emotion['Confidence'] / 100,
            "story_influence": emotion_info['influence'],
            "all_emotions": [{"type": e['Type'], "confidence": e['Confidence']} for e in emotions]
        })
        
    except Exception as e:
        logger.error(f"Error detecting emotion: {e}")
        return jsonify({"success": False, "message": str(e)}), 200
