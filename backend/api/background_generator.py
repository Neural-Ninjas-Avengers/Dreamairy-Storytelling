from flask import Blueprint, request, jsonify
import logging
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from services.ai_image_service import generate_image_sync

background_bp = Blueprint('background', __name__)
logger = logging.getLogger(__name__)

@background_bp.route('/generate-magical-background', methods=['POST'])
def generate_magical_background():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Enhanced prompt for professional forest backgrounds
        enhanced_prompt = f"{prompt}, ultra high quality, professional photography, cinematic lighting, 8K resolution, nature documentary style, realistic textures, depth of field"
        
        # Try AI image generation first, fallback to SVG
        try:
            image_url = generate_image_sync(enhanced_prompt, "professional_landscape")
            if image_url:
                return jsonify({
                    'success': True,
                    'image_url': image_url,
                    'provider': 'ai_service'
                })
        except Exception as e:
            logger.warning(f"AI generation failed: {e}")
        
        # Fallback to professional SVG
        image_url = generate_professional_forest_svg()
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'provider': 'svg_generator'
        })
            
    except Exception as e:
        logger.error(f"Error generating magical background: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@background_bp.route('/placeholder/<int:width>/<int:height>', methods=['GET'])
def placeholder_image(width, height):
    """Generate placeholder image"""
    try:
        # Create simple placeholder image
        img = Image.new('RGB', (width, height), color='#87CEEB')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"{width}x{height}"
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='white', font=font)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image_url': f'data:image/png;base64,{img_data}'
        })
        
    except Exception as e:
        logger.error(f"Error generating placeholder: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_professional_forest_svg():
    """Generate professional forest SVG background"""
    svg_content = '''<svg width="1200" height="800" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="skyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:1" />
                <stop offset="70%" style="stop-color:#98D8E8;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#B0E0E6;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="groundGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#8FBC8F;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#6B8E23;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#556B2F;stop-opacity:1" />
            </linearGradient>
            <radialGradient id="sunGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:#FFD700;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#FFA500;stop-opacity:0.3" />
            </radialGradient>
        </defs>
        
        <!-- Sky -->
        <rect width="1200" height="500" fill="url(#skyGradient)"/>
        
        <!-- Sun rays -->
        <circle cx="900" cy="150" r="80" fill="url(#sunGradient)"/>
        
        <!-- Background trees -->
        <ellipse cx="200" cy="400" rx="80" ry="200" fill="#2F4F2F" opacity="0.7"/>
        <ellipse cx="350" cy="380" rx="60" ry="180" fill="#228B22" opacity="0.6"/>
        <ellipse cx="500" cy="420" rx="90" ry="220" fill="#2F4F2F" opacity="0.8"/>
        <ellipse cx="700" cy="390" rx="70" ry="190" fill="#228B22" opacity="0.7"/>
        <ellipse cx="850" cy="410" rx="85" ry="210" fill="#2F4F2F" opacity="0.6"/>
        <ellipse cx="1000" cy="400" rx="75" ry="200" fill="#228B22" opacity="0.8"/>
        
        <!-- Foreground trees -->
        <ellipse cx="100" cy="450" rx="100" ry="250" fill="#1C3A1C"/>
        <ellipse cx="300" cy="430" rx="80" ry="220" fill="#2F4F2F"/>
        <ellipse cx="600" cy="460" rx="110" ry="260" fill="#1C3A1C"/>
        <ellipse cx="900" cy="440" rx="90" ry="240" fill="#2F4F2F"/>
        <ellipse cx="1100" cy="450" rx="95" ry="250" fill="#1C3A1C"/>
        
        <!-- Ground -->
        <rect y="500" width="1200" height="300" fill="url(#groundGradient)"/>
        
        <!-- Light rays through trees -->
        <polygon points="850,0 870,0 920,500 900,500" fill="#FFD700" opacity="0.2"/>
        <polygon points="920,0 940,0 990,500 970,500" fill="#FFD700" opacity="0.15"/>
        
        <!-- Mist effect -->
        <ellipse cx="600" cy="500" rx="400" ry="50" fill="#FFFFFF" opacity="0.3"/>
        <ellipse cx="300" cy="520" rx="200" ry="30" fill="#FFFFFF" opacity="0.2"/>
        <ellipse cx="900" cy="510" rx="300" ry="40" fill="#FFFFFF" opacity="0.25"/>
    </svg>'''
    
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"