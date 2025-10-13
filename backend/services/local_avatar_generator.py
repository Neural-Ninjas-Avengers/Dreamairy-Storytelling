#!/usr/bin/env python3
"""
Local Avatar Generation Engine
Creates cartoon-style avatars locally when AWS services are unavailable or blocked
"""

import base64
import io
import logging
import json
import random
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import colorsys

logger = logging.getLogger(__name__)

class LocalAvatarGenerator:
    """
    Local avatar generation using PIL and algorithmic approaches
    Creates cartoon-style avatars from photos or characteristics
    """
    
    def __init__(self):
        self.avatar_size = (512, 512)
        self.face_colors = [
            "#FDBCB4",  # Light skin
            "#F1C27D",  # Medium light skin
            "#E0AC69",  # Medium skin
            "#C68642",  # Medium dark skin
            "#8D5524"   # Dark skin
        ]
        
        self.hair_colors = [
            "#8B4513",  # Brown
            "#D2691E",  # Light brown
            "#FFD700",  # Blonde
            "#000000",  # Black
            "#A0522D",  # Auburn
            "#FF6347"   # Red
        ]
        
        self.eye_colors = [
            "#8B4513",  # Brown
            "#4682B4",  # Blue
            "#228B22",  # Green
            "#2F4F4F",  # Gray
            "#800080"   # Purple (fantasy)
        ]
        
        self.clothing_colors = [
            "#FF6B6B",  # Red
            "#4ECDC4",  # Teal
            "#45B7D1",  # Blue
            "#96CEB4",  # Green
            "#FFEAA7",  # Yellow
            "#DDA0DD",  # Plum
            "#F39C12"   # Orange
        ]
    
    def generate_avatar_from_photo(self, photo_base64: str, age: int, style: str = "cartoon") -> Tuple[bool, str, str]:
        """
        Generate avatar from photo using local processing
        
        Args:
            photo_base64: Base64 encoded photo
            age: Target age for avatar
            style: Avatar style (cartoon, anime, etc.)
            
        Returns:
            (success, avatar_base64, message)
        """
        try:
            logger.info(f"🎨 Generating local avatar from photo for age {age}")
            
            # Extract characteristics from photo
            characteristics = self._extract_photo_characteristics(photo_base64)
            
            # Generate avatar based on characteristics
            avatar_image = self._create_avatar_from_characteristics(characteristics, age, style)
            
            # Convert to base64
            avatar_base64 = self._image_to_base64(avatar_image)
            
            logger.info("✅ Local avatar generated successfully from photo")
            return True, f"data:image/png;base64,{avatar_base64}", "Avatar generated locally from photo"
            
        except Exception as e:
            logger.error(f"Local avatar generation from photo failed: {e}")
            return False, "", str(e)
    
    def generate_template_avatar(self, age: int, characteristics: Optional[Dict] = None, 
                               theme: str = "fantasy") -> Tuple[bool, str, str]:
        """
        Generate template-based avatar without photo
        
        Args:
            age: Target age
            characteristics: Optional characteristics dict
            theme: Theme for avatar generation
            
        Returns:
            (success, avatar_base64, message)
        """
        try:
            logger.info(f"🎨 Generating template avatar for age {age}, theme {theme}")
            
            # Use provided characteristics or generate random ones
            if not characteristics:
                characteristics = self._generate_random_characteristics(age, theme)
            
            # Create avatar
            avatar_image = self._create_avatar_from_characteristics(characteristics, age, "cartoon")
            
            # Convert to base64
            avatar_base64 = self._image_to_base64(avatar_image)
            
            logger.info("✅ Template avatar generated successfully")
            return True, f"data:image/png;base64,{avatar_base64}", "Template avatar generated locally"
            
        except Exception as e:
            logger.error(f"Template avatar generation failed: {e}")
            return False, "", str(e)
    
    def _extract_photo_characteristics(self, photo_base64: str) -> Dict:
        """Extract basic characteristics from photo for avatar generation"""
        try:
            # Remove data URL prefix if present
            if photo_base64.startswith('data:image'):
                photo_base64 = photo_base64.split(',')[1]
            
            # Decode image
            image_bytes = base64.b64decode(photo_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Basic color analysis
            characteristics = self._analyze_image_colors(image)
            
            # Add some randomization for variety
            characteristics.update({
                "style_variation": random.randint(1, 3),
                "expression": random.choice(["happy", "cheerful", "friendly", "excited"]),
                "accessories": random.choice([None, "hat", "glasses", "bow"])
            })
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"Photo characteristic extraction failed: {e}")
            # Return default characteristics
            return self._generate_random_characteristics(7, "fantasy")
    
    def _analyze_image_colors(self, image: Image.Image) -> Dict:
        """Analyze image colors to determine avatar characteristics"""
        try:
            # Resize for faster processing
            small_image = image.resize((100, 100))
            
            # Get dominant colors
            colors = small_image.getcolors(maxcolors=256*256*256)
            if not colors:
                return self._generate_random_characteristics(7, "fantasy")
            
            # Sort by frequency
            colors.sort(key=lambda x: x[0], reverse=True)
            
            # Analyze top colors
            dominant_colors = [color[1] for color in colors[:5]]
            
            # Determine characteristics based on colors
            characteristics = {
                "face_color": self._find_closest_face_color(dominant_colors),
                "hair_color": self._find_closest_hair_color(dominant_colors),
                "eye_color": random.choice(self.eye_colors),
                "clothing_color": self._find_closest_clothing_color(dominant_colors)
            }
            
            return characteristics
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {e}")
            return self._generate_random_characteristics(7, "fantasy")
    
    def _find_closest_face_color(self, colors: List[Tuple]) -> str:
        """Find closest face color from image colors"""
        # Simple heuristic: look for skin-tone colors
        for color in colors:
            r, g, b = color
            # Check if color is in skin tone range
            if 150 < r < 255 and 100 < g < 200 and 80 < b < 180:
                # Find closest predefined face color
                return min(self.face_colors, key=lambda fc: self._color_distance(color, self._hex_to_rgb(fc)))
        
        # Default to medium skin tone
        return self.face_colors[1]
    
    def _find_closest_hair_color(self, colors: List[Tuple]) -> str:
        """Find closest hair color from image colors"""
        # Look for darker colors that could be hair
        dark_colors = [c for c in colors if sum(c) < 400]  # Darker colors
        
        if dark_colors:
            darkest = min(dark_colors, key=lambda c: sum(c))
            return min(self.hair_colors, key=lambda hc: self._color_distance(darkest, self._hex_to_rgb(hc)))
        
        # Default to brown
        return self.hair_colors[0]
    
    def _find_closest_clothing_color(self, colors: List[Tuple]) -> str:
        """Find closest clothing color from image colors"""
        # Look for vibrant colors
        vibrant_colors = [c for c in colors if max(c) - min(c) > 50]  # Colors with good contrast
        
        if vibrant_colors:
            most_vibrant = max(vibrant_colors, key=lambda c: max(c) - min(c))
            return min(self.clothing_colors, key=lambda cc: self._color_distance(most_vibrant, self._hex_to_rgb(cc)))
        
        # Default to blue
        return self.clothing_colors[2]
    
    def _color_distance(self, color1: Tuple, color2: Tuple) -> float:
        """Calculate distance between two RGB colors"""
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _generate_random_characteristics(self, age: int, theme: str) -> Dict:
        """Generate random characteristics for avatar"""
        characteristics = {
            "face_color": random.choice(self.face_colors),
            "hair_color": random.choice(self.hair_colors),
            "eye_color": random.choice(self.eye_colors),
            "clothing_color": random.choice(self.clothing_colors),
            "expression": "happy",
            "style_variation": random.randint(1, 3)
        }
        
        # Age-specific adjustments
        if age <= 5:
            characteristics["face_shape"] = "round"
            characteristics["eye_size"] = "large"
            characteristics["accessories"] = random.choice([None, "bow", "hat"])
        elif age <= 8:
            characteristics["face_shape"] = "oval"
            characteristics["eye_size"] = "medium"
            characteristics["accessories"] = random.choice([None, "glasses", "hat"])
        else:
            characteristics["face_shape"] = "oval"
            characteristics["eye_size"] = "medium"
            characteristics["accessories"] = random.choice([None, "glasses", "headband"])
        
        # Theme-specific adjustments
        if theme == "fantasy":
            characteristics["magical_element"] = random.choice(["sparkles", "stars", "crown"])
        elif theme == "adventure":
            characteristics["adventure_element"] = random.choice(["hat", "compass", "map"])
        
        return characteristics
    
    def _create_avatar_from_characteristics(self, characteristics: Dict, age: int, style: str) -> Image.Image:
        """Create avatar image from characteristics"""
        try:
            # Create base image
            avatar = Image.new('RGBA', self.avatar_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(avatar)
            
            # Calculate proportions based on age
            if age <= 5:
                head_size = 180
                body_size = 120
                eye_size = 25
            elif age <= 8:
                head_size = 160
                body_size = 140
                eye_size = 20
            else:
                head_size = 150
                body_size = 160
                eye_size = 18
            
            center_x, center_y = self.avatar_size[0] // 2, self.avatar_size[1] // 2
            
            # Draw body
            self._draw_body(draw, center_x, center_y + 100, body_size, characteristics)
            
            # Draw head
            self._draw_head(draw, center_x, center_y - 50, head_size, characteristics)
            
            # Draw hair
            self._draw_hair(draw, center_x, center_y - 50, head_size, characteristics)
            
            # Draw eyes
            self._draw_eyes(draw, center_x, center_y - 60, eye_size, characteristics)
            
            # Draw mouth
            self._draw_mouth(draw, center_x, center_y - 20, characteristics)
            
            # Draw accessories if any
            if characteristics.get("accessories"):
                self._draw_accessories(draw, center_x, center_y - 50, head_size, characteristics)
            
            # Add magical elements for fantasy theme
            if characteristics.get("magical_element"):
                self._draw_magical_elements(draw, avatar, characteristics)
            
            # Apply style effects
            avatar = self._apply_style_effects(avatar, style)
            
            return avatar
            
        except Exception as e:
            logger.error(f"Avatar creation failed: {e}")
            # Return simple fallback avatar
            return self._create_simple_fallback_avatar(age)
    
    def _draw_body(self, draw: ImageDraw.Draw, x: int, y: int, size: int, characteristics: Dict):
        """Draw avatar body"""
        clothing_color = characteristics.get("clothing_color", self.clothing_colors[0])
        
        # Draw shirt/dress
        body_rect = [x - size//2, y - size//3, x + size//2, y + size//2]
        draw.ellipse(body_rect, fill=clothing_color, outline="#000000", width=2)
        
        # Draw arms
        arm_width = size // 6
        arm_length = size // 2
        
        # Left arm
        left_arm = [x - size//2 - arm_width//2, y - size//6, 
                   x - size//2 + arm_width//2, y + arm_length]
        draw.ellipse(left_arm, fill=clothing_color, outline="#000000", width=2)
        
        # Right arm
        right_arm = [x + size//2 - arm_width//2, y - size//6,
                    x + size//2 + arm_width//2, y + arm_length]
        draw.ellipse(right_arm, fill=clothing_color, outline="#000000", width=2)
    
    def _draw_head(self, draw: ImageDraw.Draw, x: int, y: int, size: int, characteristics: Dict):
        """Draw avatar head"""
        face_color = characteristics.get("face_color", self.face_colors[0])
        
        # Draw face
        face_rect = [x - size//2, y - size//2, x + size//2, y + size//2]
        draw.ellipse(face_rect, fill=face_color, outline="#000000", width=3)
    
    def _draw_hair(self, draw: ImageDraw.Draw, x: int, y: int, size: int, characteristics: Dict):
        """Draw avatar hair"""
        hair_color = characteristics.get("hair_color", self.hair_colors[0])
        
        # Simple hair style - top portion of head
        hair_rect = [x - size//2 - 10, y - size//2 - 20, x + size//2 + 10, y + size//6]
        draw.ellipse(hair_rect, fill=hair_color, outline="#000000", width=2)
    
    def _draw_eyes(self, draw: ImageDraw.Draw, x: int, y: int, size: int, characteristics: Dict):
        """Draw avatar eyes"""
        eye_color = characteristics.get("eye_color", self.eye_colors[0])
        
        # Left eye
        left_eye_white = [x - size - 5, y - size//2, x - size//2 + 5, y + size//2]
        draw.ellipse(left_eye_white, fill="#FFFFFF", outline="#000000", width=2)
        
        left_eye_iris = [x - size + 2, y - size//2 + 2, x - size//2 + 2, y + size//2 - 2]
        draw.ellipse(left_eye_iris, fill=eye_color, outline="#000000", width=1)
        
        # Right eye
        right_eye_white = [x + size//2 - 5, y - size//2, x + size + 5, y + size//2]
        draw.ellipse(right_eye_white, fill="#FFFFFF", outline="#000000", width=2)
        
        right_eye_iris = [x + size//2 - 2, y - size//2 + 2, x + size - 2, y + size//2 - 2]
        draw.ellipse(right_eye_iris, fill=eye_color, outline="#000000", width=1)
    
    def _draw_mouth(self, draw: ImageDraw.Draw, x: int, y: int, characteristics: Dict):
        """Draw avatar mouth"""
        expression = characteristics.get("expression", "happy")
        
        if expression in ["happy", "cheerful", "excited"]:
            # Smiling mouth
            mouth_rect = [x - 15, y - 5, x + 15, y + 10]
            draw.arc(mouth_rect, start=0, end=180, fill="#000000", width=3)
        else:
            # Neutral mouth
            draw.line([x - 10, y, x + 10, y], fill="#000000", width=3)
    
    def _draw_accessories(self, draw: ImageDraw.Draw, x: int, y: int, size: int, characteristics: Dict):
        """Draw avatar accessories"""
        accessory = characteristics.get("accessories")
        
        if accessory == "hat":
            # Simple hat
            hat_rect = [x - size//2 - 10, y - size//2 - 40, x + size//2 + 10, y - size//2 - 10]
            draw.ellipse(hat_rect, fill="#FF6B6B", outline="#000000", width=2)
        
        elif accessory == "glasses":
            # Simple glasses
            # Left lens
            left_lens = [x - size//2, y - size//3, x - 10, y - 5]
            draw.ellipse(left_lens, fill=None, outline="#000000", width=3)
            
            # Right lens
            right_lens = [x + 10, y - size//3, x + size//2, y - 5]
            draw.ellipse(right_lens, fill=None, outline="#000000", width=3)
            
            # Bridge
            draw.line([x - 10, y - size//4, x + 10, y - size//4], fill="#000000", width=3)
        
        elif accessory == "bow":
            # Simple bow
            bow_rect = [x - 20, y - size//2 - 10, x + 20, y - size//2 + 10]
            draw.ellipse(bow_rect, fill="#FF69B4", outline="#000000", width=2)
    
    def _draw_magical_elements(self, draw: ImageDraw.Draw, avatar: Image.Image, characteristics: Dict):
        """Draw magical elements for fantasy theme"""
        magical_element = characteristics.get("magical_element")
        
        if magical_element == "sparkles":
            # Add sparkle effects
            for _ in range(10):
                x = random.randint(50, avatar.width - 50)
                y = random.randint(50, avatar.height - 50)
                star_size = random.randint(3, 8)
                
                # Draw simple star
                points = []
                for i in range(5):
                    angle = i * 72 * 3.14159 / 180
                    px = x + star_size * 0.8 * (1 if i % 2 == 0 else 0.4) * (1 if i < 2.5 else -1)
                    py = y + star_size * 0.8 * (1 if i % 2 == 0 else 0.4) * (1 if 1 < i < 4 else -1)
                    points.extend([px, py])
                
                draw.polygon(points, fill="#FFD700", outline="#FFA500")
    
    def _apply_style_effects(self, avatar: Image.Image, style: str) -> Image.Image:
        """Apply style-specific effects to avatar"""
        try:
            if style == "cartoon":
                # Enhance colors for cartoon look
                enhancer = ImageEnhance.Color(avatar)
                avatar = enhancer.enhance(1.2)
                
                # Slight contrast boost
                contrast_enhancer = ImageEnhance.Contrast(avatar)
                avatar = contrast_enhancer.enhance(1.1)
            
            elif style == "anime":
                # Softer, more pastel colors
                enhancer = ImageEnhance.Color(avatar)
                avatar = enhancer.enhance(0.9)
                
                # Slight blur for softer look
                avatar = avatar.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            return avatar
            
        except Exception as e:
            logger.warning(f"Style effects failed: {e}")
            return avatar
    
    def _create_simple_fallback_avatar(self, age: int) -> Image.Image:
        """Create very simple fallback avatar"""
        avatar = Image.new('RGBA', self.avatar_size, (135, 206, 235, 255))  # Sky blue background
        draw = ImageDraw.Draw(avatar)
        
        center_x, center_y = self.avatar_size[0] // 2, self.avatar_size[1] // 2
        
        # Simple smiley face
        face_size = 150
        face_rect = [center_x - face_size//2, center_y - face_size//2, 
                    center_x + face_size//2, center_y + face_size//2]
        draw.ellipse(face_rect, fill="#FDBCB4", outline="#000000", width=3)
        
        # Eyes
        eye_size = 15
        draw.ellipse([center_x - 30, center_y - 30, center_x - 30 + eye_size, center_y - 30 + eye_size], 
                    fill="#000000")
        draw.ellipse([center_x + 15, center_y - 30, center_x + 15 + eye_size, center_y - 30 + eye_size], 
                    fill="#000000")
        
        # Smile
        mouth_rect = [center_x - 25, center_y, center_x + 25, center_y + 25]
        draw.arc(mouth_rect, start=0, end=180, fill="#000000", width=3)
        
        return avatar
    
    def create_stylized_photo_avatar(self, photo_base64: str, age: int, style: str = "cartoon") -> Tuple[bool, str, str]:
        """
        Create stylized avatar directly from photo using artistic filters
        
        Args:
            photo_base64: Base64 encoded photo
            age: Target age
            style: Stylization style
            
        Returns:
            (success, stylized_avatar_base64, message)
        """
        try:
            logger.info(f"🎨 Creating stylized photo avatar for age {age}")
            
            # Decode photo
            if photo_base64.startswith('data:image'):
                photo_base64 = photo_base64.split(',')[1]
            
            image_bytes = base64.b64decode(photo_base64)
            photo = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if photo.mode != 'RGB':
                photo = photo.convert('RGB')
            
            # Apply stylization based on style
            if style == "cartoon":
                stylized = self._apply_cartoon_stylization(photo, age)
            elif style == "anime":
                stylized = self._apply_anime_stylization(photo, age)
            elif style == "watercolor":
                stylized = self._apply_watercolor_stylization(photo, age)
            else:
                stylized = self._apply_cartoon_stylization(photo, age)
            
            # Resize to standard avatar size
            stylized = stylized.resize(self.avatar_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            avatar_base64 = self._image_to_base64(stylized)
            
            logger.info("✅ Stylized photo avatar created successfully")
            return True, f"data:image/png;base64,{avatar_base64}", f"Photo stylized as {style} avatar"
            
        except Exception as e:
            logger.error(f"Stylized photo avatar creation failed: {e}")
            return False, "", str(e)
    
    def _apply_cartoon_stylization(self, photo: Image.Image, age: int) -> Image.Image:
        """Apply cartoon-style effects to photo"""
        try:
            # Step 1: Enhance colors for cartoon look
            color_enhancer = ImageEnhance.Color(photo)
            vibrant = color_enhancer.enhance(1.3)
            
            # Step 2: Increase contrast
            contrast_enhancer = ImageEnhance.Contrast(vibrant)
            contrasted = contrast_enhancer.enhance(1.2)
            
            # Step 3: Apply slight blur to reduce photo-realism
            blurred = contrasted.filter(ImageFilter.GaussianBlur(radius=1.0))
            
            # Step 4: Enhance brightness for cheerful look
            brightness_enhancer = ImageEnhance.Brightness(blurred)
            bright = brightness_enhancer.enhance(1.1)
            
            # Step 5: Apply edge enhancement for cartoon effect
            edge_enhanced = bright.filter(ImageFilter.EDGE_ENHANCE)
            
            # Step 6: Age-specific adjustments
            if age <= 5:
                # Extra bright and colorful for young children
                final_color_enhancer = ImageEnhance.Color(edge_enhanced)
                final = final_color_enhancer.enhance(1.2)
            else:
                final = edge_enhanced
            
            return final
            
        except Exception as e:
            logger.warning(f"Cartoon stylization failed: {e}")
            return photo
    
    def _apply_anime_stylization(self, photo: Image.Image, age: int) -> Image.Image:
        """Apply anime-style effects to photo"""
        try:
            # Step 1: Soften colors
            color_enhancer = ImageEnhance.Color(photo)
            soft_colors = color_enhancer.enhance(0.9)
            
            # Step 2: Apply gaussian blur for softer look
            soft = soft_colors.filter(ImageFilter.GaussianBlur(radius=1.5))
            
            # Step 3: Enhance brightness
            brightness_enhancer = ImageEnhance.Brightness(soft)
            bright = brightness_enhancer.enhance(1.15)
            
            # Step 4: Slight contrast reduction for dreamy effect
            contrast_enhancer = ImageEnhance.Contrast(bright)
            dreamy = contrast_enhancer.enhance(0.9)
            
            return dreamy
            
        except Exception as e:
            logger.warning(f"Anime stylization failed: {e}")
            return photo
    
    def _apply_watercolor_stylization(self, photo: Image.Image, age: int) -> Image.Image:
        """Apply watercolor-style effects to photo"""
        try:
            # Step 1: Apply blur for watercolor effect
            watercolor = photo.filter(ImageFilter.GaussianBlur(radius=2.0))
            
            # Step 2: Enhance colors
            color_enhancer = ImageEnhance.Color(watercolor)
            colorful = color_enhancer.enhance(1.4)
            
            # Step 3: Reduce contrast for soft watercolor look
            contrast_enhancer = ImageEnhance.Contrast(colorful)
            soft = contrast_enhancer.enhance(0.8)
            
            # Step 4: Increase brightness
            brightness_enhancer = ImageEnhance.Brightness(soft)
            bright = brightness_enhancer.enhance(1.2)
            
            return bright
            
        except Exception as e:
            logger.warning(f"Watercolor stylization failed: {e}")
            return photo
    
    def create_hybrid_avatar(self, photo_base64: str, age: int, theme: str = "fantasy") -> Tuple[bool, str, str]:
        """
        Create hybrid avatar combining photo analysis with generated elements
        
        Args:
            photo_base64: Base64 encoded photo
            age: Target age
            theme: Avatar theme
            
        Returns:
            (success, hybrid_avatar_base64, message)
        """
        try:
            logger.info(f"🎨 Creating hybrid avatar for age {age}, theme {theme}")
            
            # Extract characteristics from photo
            characteristics = self._extract_photo_characteristics(photo_base64)
            
            # Create base avatar from characteristics
            base_avatar = self._create_avatar_from_characteristics(characteristics, age, "cartoon")
            
            # Apply photo-based enhancements
            if photo_base64:
                # Create stylized version of photo
                success, stylized_data, _ = self.create_stylized_photo_avatar(photo_base64, age, "cartoon")
                
                if success:
                    # Extract stylized photo
                    stylized_base64 = stylized_data.split(',')[1]
                    stylized_bytes = base64.b64decode(stylized_base64)
                    stylized_photo = Image.open(io.BytesIO(stylized_bytes))
                    
                    # Blend generated avatar with stylized photo
                    blended = self._blend_avatar_with_photo(base_avatar, stylized_photo, age)
                    
                    # Convert to base64
                    avatar_base64 = self._image_to_base64(blended)
                    
                    logger.info("✅ Hybrid avatar created successfully")
                    return True, f"data:image/png;base64,{avatar_base64}", "Hybrid avatar combining photo and generated elements"
            
            # Fallback to generated avatar only
            avatar_base64 = self._image_to_base64(base_avatar)
            return True, f"data:image/png;base64,{avatar_base64}", "Generated avatar based on photo characteristics"
            
        except Exception as e:
            logger.error(f"Hybrid avatar creation failed: {e}")
            return False, "", str(e)
    
    def _blend_avatar_with_photo(self, avatar: Image.Image, photo: Image.Image, age: int) -> Image.Image:
        """Blend generated avatar with stylized photo"""
        try:
            # Resize photo to match avatar
            photo_resized = photo.resize(avatar.size, Image.Resampling.LANCZOS)
            
            # Create blend based on age (younger children get more cartoon-like blend)
            if age <= 5:
                # More cartoon, less photo
                blend_ratio = 0.3  # 30% photo, 70% cartoon
            elif age <= 8:
                # Balanced blend
                blend_ratio = 0.4  # 40% photo, 60% cartoon
            else:
                # More photo-like
                blend_ratio = 0.5  # 50% photo, 50% cartoon
            
            # Blend images
            blended = Image.blend(avatar.convert('RGBA'), photo_resized.convert('RGBA'), blend_ratio)
            
            # Apply final cartoon enhancement
            final = self._apply_cartoon_stylization(blended.convert('RGB'), age)
            
            return final
            
        except Exception as e:
            logger.warning(f"Avatar blending failed: {e}")
            return avatar
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """Get list of available stylization styles"""
        return [
            {
                "id": "cartoon",
                "name": "Cartoon Style",
                "description": "Bright, colorful cartoon-style avatar",
                "best_for": "All ages, especially younger children"
            },
            {
                "id": "anime",
                "name": "Anime Style", 
                "description": "Soft, dreamy anime-inspired avatar",
                "best_for": "Older children and teens"
            },
            {
                "id": "watercolor",
                "name": "Watercolor Style",
                "description": "Soft, artistic watercolor effect",
                "best_for": "Gentle, artistic look for all ages"
            },
            {
                "id": "hybrid",
                "name": "Hybrid Style",
                "description": "Combines photo with generated elements",
                "best_for": "Personalized yet stylized appearance"
            }
        ]
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG', optimize=True)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Global instance for easy access
local_avatar_generator = LocalAvatarGenerator()