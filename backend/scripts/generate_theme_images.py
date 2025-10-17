"""
Script para generar imágenes temáticas para los botones de selección de historia
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import boto3
import json
import base64
from backend.admin.config_manager import ConfigManager

# Cargar configuración AWS
config_manager = ConfigManager()
config = config_manager.load_config()

if not config.get('aws_enabled'):
    print("❌ AWS no está habilitado. Por favor configura las credenciales en el panel de admin.")
    sys.exit(1)

# Configurar cliente de Bedrock con credenciales
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=config.get('aws_region', 'us-east-1'),
    aws_access_key_id=config.get('aws_access_key_id'),
    aws_secret_access_key=config.get('aws_secret_access_key')
)

# Definir los temas y sus prompts
THEMES = {
    'animals': {
        'title': 'Animales',
        'prompt': 'A whimsical, colorful illustration of cute friendly animals in a magical forest, including a rabbit, fox, deer, and birds, children book style, soft pastel colors, dreamy atmosphere, suitable for kids aged 3-10'
    },
    'space': {
        'title': 'Espacio',
        'prompt': 'A vibrant illustration of outer space with colorful planets, stars, rockets, and astronauts, children book style, bright colors, magical and adventurous atmosphere, suitable for kids aged 3-10'
    },
    'pirates': {
        'title': 'Piratas',
        'prompt': 'A fun, colorful illustration of a pirate ship sailing on blue ocean waves with treasure chest, friendly pirates, tropical island in background, children book style, bright colors, adventurous atmosphere, suitable for kids aged 3-10'
    },
    'dinosaurs': {
        'title': 'Dinosaurios',
        'prompt': 'A playful illustration of friendly colorful dinosaurs in a prehistoric jungle with palm trees and volcanoes, children book style, vibrant colors, fun and exciting atmosphere, suitable for kids aged 3-10'
    },
    'magic': {
        'title': 'Magia',
        'prompt': 'A magical illustration with wizards, fairies, unicorns, sparkles, and enchanted castle, children book style, pastel and glowing colors, mystical and dreamy atmosphere, suitable for kids aged 3-10'
    },
    'superheroes': {
        'title': 'Superhéroes',
        'prompt': 'A dynamic illustration of friendly superheroes flying over a colorful city, with capes and masks, children book style, bold bright colors, heroic and exciting atmosphere, suitable for kids aged 3-10'
    }
}

def generate_image(theme_id, prompt):
    """Genera una imagen usando Amazon Bedrock (Stable Diffusion)"""
    
    body = json.dumps({
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1.0
            },
            {
                "text": "scary, dark, violent, inappropriate, realistic, photographic, adult content",
                "weight": -1.0
            }
        ],
        "cfg_scale": 10,
        "seed": 42,
        "steps": 50,
        "width": 512,
        "height": 512,
        "style_preset": "digital-art"
    })
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId='stability.stable-diffusion-xl-v1',
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        
        # Obtener la imagen en base64
        image_base64 = response_body['artifacts'][0]['base64']
        
        # Guardar la imagen
        output_dir = Path(__file__).parent.parent.parent / 'frontend' / 'public' / 'theme-images'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f'{theme_id}.png'
        
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(image_base64))
        
        print(f"✅ Imagen generada: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error generando imagen para {theme_id}: {str(e)}")
        return None

def main():
    """Genera todas las imágenes temáticas"""
    print("🎨 Generando imágenes temáticas para los botones...")
    print()
    
    for theme_id, theme_data in THEMES.items():
        print(f"Generando: {theme_data['title']} ({theme_id})...")
        generate_image(theme_id, theme_data['prompt'])
        print()
    
    print("✨ ¡Todas las imágenes generadas!")
    print("📁 Las imágenes están en: frontend/public/theme-images/")

if __name__ == '__main__':
    main()
