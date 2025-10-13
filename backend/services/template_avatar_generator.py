#!/usr/bin/env python3
"""
Template-Based Avatar Generator
Creates high-quality SVG avatars using predefined templates and customization options
"""

import base64
import logging
import random
import json
from typing import Dict, List, Tuple, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class TemplateAvatarGenerator:
    """
    Template-based avatar generation system
    Creates customizable SVG avatars using predefined templates
    """
    
    def __init__(self):
        self.avatar_size = (512, 512)
        
        # Color palettes
        self.skin_tones = {
            "light": "#FDBCB4",
            "medium_light": "#F1C27D", 
            "medium": "#E0AC69",
            "medium_dark": "#C68642",
            "dark": "#8D5524"
        }
        
        self.hair_colors = {
            "blonde": "#FFD700",
            "light_brown": "#D2691E",
            "brown": "#8B4513",
            "dark_brown": "#654321",
            "black": "#2C1810",
            "red": "#B22222",
            "auburn": "#A0522D"
        }
        
        self.eye_colors = {
            "brown": "#8B4513",
            "blue": "#4682B4", 
            "green": "#228B22",
            "hazel": "#8E7618",
            "gray": "#708090"
        }
        
        self.clothing_colors = {
            "red": "#FF6B6B",
            "blue": "#4ECDC4",
            "green": "#96CEB4",
            "yellow": "#FFEAA7",
            "purple": "#DDA0DD",
            "orange": "#F39C12",
            "pink": "#FF69B4"
        }
        
        # Age-based templates
        self.age_templates = {
            "toddler": {  # 3-5 years
                "head_ratio": 0.4,
                "body_ratio": 0.6,
                "eye_size": 0.08,
                "features": "rounded",
                "proportions": "chubby"
            },
            "child": {  # 6-8 years
                "head_ratio": 0.35,
                "body_ratio": 0.65,
                "eye_size": 0.06,
                "features": "soft",
                "proportions": "normal"
            },
            "preteen": {  # 9-12 years
                "head_ratio": 0.3,
                "body_ratio": 0.7,
                "eye_size": 0.05,
                "features": "defined",
                "proportions": "slim"
            }
        }
        
        # Theme-based accessories and elements
        self.theme_elements = {
            "fantasy": {
                "accessories": ["crown", "magic_wand", "fairy_wings", "sparkles"],
                "backgrounds": ["castle", "forest", "rainbow", "clouds"],
                "colors": ["magical_purple", "fairy_pink", "enchanted_blue"]
            },
            "adventure": {
                "accessories": ["explorer_hat", "compass", "backpack", "map"],
                "backgrounds": ["mountains", "jungle", "desert", "ocean"],
                "colors": ["earth_brown", "adventure_green", "sky_blue"]
            },
            "animals": {
                "accessories": ["animal_ears", "tail", "paw_prints", "whiskers"],
                "backgrounds": ["forest", "meadow", "zoo", "farm"],
                "colors": ["nature_green", "animal_brown", "flower_colors"]
            },
            "space": {
                "accessories": ["space_helmet", "rocket", "stars", "planets"],
                "backgrounds": ["space", "moon", "stars", "galaxy"],
                "colors": ["space_blue", "star_yellow", "planet_colors"]
            }
        }
    
    def generate_template_avatar(self, age: int, characteristics: Optional[Dict] = None, 
                               theme: str = "fantasy", style: str = "cute") -> Tuple[bool, str, str]:
        """
        Generate template-based avatar
        
        Args:
            age: Child's age
            characteristics: Optional customization characteristics
            theme: Avatar theme
            style: Avatar style
            
        Returns:
            (success, avatar_svg_base64, message)
        """
        try:
            logger.info(f"🎨 Generating template avatar for age {age}, theme {theme}")
            
            # Determine age category
            age_category = self._get_age_category(age)
            template = self.age_templates[age_category]
            
            # Use provided characteristics or generate defaults
            if not characteristics:
                characteristics = self._generate_default_characteristics(age, theme)
            
            # Create SVG avatar
            svg_content = self._create_svg_avatar(template, characteristics, theme, style, age)
            
            # Convert to base64
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            avatar_data_url = f"data:image/svg+xml;base64,{svg_base64}"
            
            logger.info("✅ Template avatar generated successfully")
            return True, avatar_data_url, f"Template avatar created for {age_category} with {theme} theme"
            
        except Exception as e:
            logger.error(f"Template avatar generation failed: {e}")
            return False, "", str(e)
    
    def generate_customizable_avatar(self, customization_options: Dict) -> Tuple[bool, str, str]:
        """
        Generate avatar with specific customization options
        
        Args:
            customization_options: Detailed customization parameters
            
        Returns:
            (success, avatar_svg_base64, message)
        """
        try:
            age = customization_options.get("age", 7)
            theme = customization_options.get("theme", "fantasy")
            style = customization_options.get("style", "cute")
            
            logger.info(f"🎨 Generating customizable avatar with specific options")
            
            # Validate and process customization options
            processed_options = self._process_customization_options(customization_options)
            
            # Generate avatar
            age_category = self._get_age_category(age)
            template = self.age_templates[age_category]
            
            svg_content = self._create_svg_avatar(template, processed_options, theme, style, age)
            
            # Convert to base64
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            avatar_data_url = f"data:image/svg+xml;base64,{svg_base64}"
            
            logger.info("✅ Customizable avatar generated successfully")
            return True, avatar_data_url, "Custom avatar created with specified options"
            
        except Exception as e:
            logger.error(f"Customizable avatar generation failed: {e}")
            return False, "", str(e)
    
    def _get_age_category(self, age: int) -> str:
        """Determine age category for template selection"""
        if age <= 5:
            return "toddler"
        elif age <= 8:
            return "child"
        else:
            return "preteen"
    
    def _generate_default_characteristics(self, age: int, theme: str) -> Dict:
        """Generate default characteristics based on age and theme"""
        characteristics = {
            "skin_tone": random.choice(list(self.skin_tones.keys())),
            "hair_color": random.choice(list(self.hair_colors.keys())),
            "eye_color": random.choice(list(self.eye_colors.keys())),
            "clothing_color": random.choice(list(self.clothing_colors.keys())),
            "expression": "happy",
            "hair_style": self._get_age_appropriate_hair_style(age),
            "clothing_style": self._get_theme_appropriate_clothing(theme)
        }
        
        # Add theme-specific elements
        theme_data = self.theme_elements.get(theme, self.theme_elements["fantasy"])
        characteristics["accessory"] = random.choice(theme_data["accessories"])
        characteristics["background"] = random.choice(theme_data["backgrounds"])
        
        return characteristics
    
    def _get_age_appropriate_hair_style(self, age: int) -> str:
        """Get age-appropriate hair style"""
        if age <= 5:
            return random.choice(["short_curly", "pigtails", "bob"])
        elif age <= 8:
            return random.choice(["medium_straight", "braids", "ponytail", "short_wavy"])
        else:
            return random.choice(["long_straight", "medium_wavy", "short_modern", "braided"])
    
    def _get_theme_appropriate_clothing(self, theme: str) -> str:
        """Get theme-appropriate clothing style"""
        clothing_styles = {
            "fantasy": ["dress", "tunic", "robe", "princess_dress"],
            "adventure": ["t_shirt", "explorer_outfit", "casual", "sporty"],
            "animals": ["animal_costume", "casual", "nature_outfit"],
            "space": ["space_suit", "futuristic", "sci_fi_outfit"]
        }
        
        styles = clothing_styles.get(theme, clothing_styles["fantasy"])
        return random.choice(styles)
    
    def _process_customization_options(self, options: Dict) -> Dict:
        """Process and validate customization options"""
        processed = {}
        
        # Skin tone
        processed["skin_tone"] = options.get("skin_tone", "medium")
        if processed["skin_tone"] not in self.skin_tones:
            processed["skin_tone"] = "medium"
        
        # Hair color
        processed["hair_color"] = options.get("hair_color", "brown")
        if processed["hair_color"] not in self.hair_colors:
            processed["hair_color"] = "brown"
        
        # Eye color
        processed["eye_color"] = options.get("eye_color", "brown")
        if processed["eye_color"] not in self.eye_colors:
            processed["eye_color"] = "brown"
        
        # Clothing color
        processed["clothing_color"] = options.get("clothing_color", "blue")
        if processed["clothing_color"] not in self.clothing_colors:
            processed["clothing_color"] = "blue"
        
        # Other options
        processed["expression"] = options.get("expression", "happy")
        processed["hair_style"] = options.get("hair_style", "medium_straight")
        processed["clothing_style"] = options.get("clothing_style", "casual")
        processed["accessory"] = options.get("accessory", None)
        processed["background"] = options.get("background", "simple")
        
        return processed
    
    def _create_svg_avatar(self, template: Dict, characteristics: Dict, 
                          theme: str, style: str, age: int) -> str:
        """Create SVG avatar content"""
        try:
            # Create SVG root element
            svg = Element('svg')
            svg.set('width', str(self.avatar_size[0]))
            svg.set('height', str(self.avatar_size[1]))
            svg.set('viewBox', f'0 0 {self.avatar_size[0]} {self.avatar_size[1]}')
            svg.set('xmlns', 'http://www.w3.org/2000/svg')
            
            # Add definitions for gradients and filters
            defs = SubElement(svg, 'defs')
            self._add_svg_definitions(defs, characteristics, theme)
            
            # Add background
            self._add_background(svg, characteristics, theme)
            
            # Calculate proportions
            center_x = self.avatar_size[0] // 2
            center_y = self.avatar_size[1] // 2
            
            head_size = int(self.avatar_size[1] * template["head_ratio"])
            body_size = int(self.avatar_size[1] * template["body_ratio"])
            
            # Add body
            self._add_body(svg, center_x, center_y + 80, body_size, characteristics, template)
            
            # Add head
            self._add_head(svg, center_x, center_y - 40, head_size, characteristics, template)
            
            # Add hair
            self._add_hair(svg, center_x, center_y - 40, head_size, characteristics, template)
            
            # Add facial features
            self._add_eyes(svg, center_x, center_y - 50, template["eye_size"], characteristics)
            self._add_nose(svg, center_x, center_y - 30, characteristics)
            self._add_mouth(svg, center_x, center_y - 10, characteristics)
            
            # Add accessories
            if characteristics.get("accessory"):
                self._add_accessory(svg, center_x, center_y - 40, head_size, characteristics, theme)
            
            # Add theme-specific decorations
            self._add_theme_decorations(svg, theme, style)
            
            # Convert to string
            svg_string = tostring(svg, encoding='unicode')
            
            # Clean up and format
            svg_string = self._format_svg_string(svg_string)
            
            return svg_string
            
        except Exception as e:
            logger.error(f"SVG avatar creation failed: {e}")
            return self._create_fallback_svg(age)
    
    def _add_svg_definitions(self, defs: Element, characteristics: Dict, theme: str):
        """Add SVG definitions for gradients and effects"""
        # Skin gradient
        skin_gradient = SubElement(defs, 'radialGradient')
        skin_gradient.set('id', 'skinGradient')
        skin_gradient.set('cx', '50%')
        skin_gradient.set('cy', '30%')
        
        skin_color = self.skin_tones[characteristics.get("skin_tone", "medium")]
        
        stop1 = SubElement(skin_gradient, 'stop')
        stop1.set('offset', '0%')
        stop1.set('stop-color', self._lighten_color(skin_color, 0.1))
        
        stop2 = SubElement(skin_gradient, 'stop')
        stop2.set('offset', '100%')
        stop2.set('stop-color', skin_color)
        
        # Hair gradient
        hair_gradient = SubElement(defs, 'radialGradient')
        hair_gradient.set('id', 'hairGradient')
        hair_gradient.set('cx', '50%')
        hair_gradient.set('cy', '20%')
        
        hair_color = self.hair_colors[characteristics.get("hair_color", "brown")]
        
        stop1 = SubElement(hair_gradient, 'stop')
        stop1.set('offset', '0%')
        stop1.set('stop-color', self._lighten_color(hair_color, 0.2))
        
        stop2 = SubElement(hair_gradient, 'stop')
        stop2.set('offset', '100%')
        stop2.set('stop-color', hair_color)
        
        # Shadow filter
        shadow_filter = SubElement(defs, 'filter')
        shadow_filter.set('id', 'shadow')
        
        shadow_blur = SubElement(shadow_filter, 'feGaussianBlur')
        shadow_blur.set('in', 'SourceAlpha')
        shadow_blur.set('stdDeviation', '3')
        
        shadow_offset = SubElement(shadow_filter, 'feOffset')
        shadow_offset.set('dx', '2')
        shadow_offset.set('dy', '2')
        shadow_offset.set('result', 'offset')
        
        shadow_merge = SubElement(shadow_filter, 'feMerge')
        SubElement(shadow_merge, 'feMergeNode').set('in', 'offset')
        SubElement(shadow_merge, 'feMergeNode').set('in', 'SourceGraphic')
    
    def _add_background(self, svg: Element, characteristics: Dict, theme: str):
        """Add background to SVG"""
        background = characteristics.get("background", "simple")
        
        if background == "simple":
            # Simple gradient background
            bg_rect = SubElement(svg, 'rect')
            bg_rect.set('width', '100%')
            bg_rect.set('height', '100%')
            bg_rect.set('fill', 'url(#bgGradient)')
            
            # Add background gradient to defs
            defs = svg.find('defs')
            bg_gradient = SubElement(defs, 'linearGradient')
            bg_gradient.set('id', 'bgGradient')
            bg_gradient.set('x1', '0%')
            bg_gradient.set('y1', '0%')
            bg_gradient.set('x2', '0%')
            bg_gradient.set('y2', '100%')
            
            stop1 = SubElement(bg_gradient, 'stop')
            stop1.set('offset', '0%')
            stop1.set('stop-color', '#87CEEB')  # Sky blue
            
            stop2 = SubElement(bg_gradient, 'stop')
            stop2.set('offset', '100%')
            stop2.set('stop-color', '#98FB98')  # Pale green
        
        elif background == "castle":
            self._add_castle_background(svg)
        elif background == "forest":
            self._add_forest_background(svg)
        elif background == "space":
            self._add_space_background(svg)
    
    def _add_body(self, svg: Element, x: int, y: int, size: int, 
                 characteristics: Dict, template: Dict):
        """Add body to avatar"""
        clothing_color = self.clothing_colors[characteristics.get("clothing_color", "blue")]
        clothing_style = characteristics.get("clothing_style", "casual")
        
        if clothing_style == "dress":
            # Draw dress
            dress = SubElement(svg, 'ellipse')
            dress.set('cx', str(x))
            dress.set('cy', str(y))
            dress.set('rx', str(size // 2))
            dress.set('ry', str(size // 3))
            dress.set('fill', clothing_color)
            dress.set('stroke', '#000000')
            dress.set('stroke-width', '2')
            dress.set('filter', 'url(#shadow)')
        else:
            # Draw shirt/top
            shirt = SubElement(svg, 'rect')
            shirt.set('x', str(x - size // 3))
            shirt.set('y', str(y - size // 4))
            shirt.set('width', str(size // 3 * 2))
            shirt.set('height', str(size // 2))
            shirt.set('rx', '10')
            shirt.set('fill', clothing_color)
            shirt.set('stroke', '#000000')
            shirt.set('stroke-width', '2')
            shirt.set('filter', 'url(#shadow)')
        
        # Add arms
        arm_color = clothing_color if clothing_style == "long_sleeve" else self.skin_tones[characteristics.get("skin_tone", "medium")]
        
        # Left arm
        left_arm = SubElement(svg, 'ellipse')
        left_arm.set('cx', str(x - size // 2))
        left_arm.set('cy', str(y))
        left_arm.set('rx', str(size // 8))
        left_arm.set('ry', str(size // 3))
        left_arm.set('fill', arm_color)
        left_arm.set('stroke', '#000000')
        left_arm.set('stroke-width', '2')
        
        # Right arm
        right_arm = SubElement(svg, 'ellipse')
        right_arm.set('cx', str(x + size // 2))
        right_arm.set('cy', str(y))
        right_arm.set('rx', str(size // 8))
        right_arm.set('ry', str(size // 3))
        right_arm.set('fill', arm_color)
        right_arm.set('stroke', '#000000')
        right_arm.set('stroke-width', '2')
    
    def _add_head(self, svg: Element, x: int, y: int, size: int, 
                 characteristics: Dict, template: Dict):
        """Add head to avatar"""
        # Head shape based on age and template
        if template["features"] == "rounded":
            # More circular for younger children
            head = SubElement(svg, 'circle')
            head.set('cx', str(x))
            head.set('cy', str(y))
            head.set('r', str(size // 2))
        else:
            # More oval for older children
            head = SubElement(svg, 'ellipse')
            head.set('cx', str(x))
            head.set('cy', str(y))
            head.set('rx', str(size // 2))
            head.set('ry', str(int(size // 2 * 1.1)))
        
        head.set('fill', 'url(#skinGradient)')
        head.set('stroke', '#000000')
        head.set('stroke-width', '3')
        head.set('filter', 'url(#shadow)')
    
    def _add_hair(self, svg: Element, x: int, y: int, size: int, 
                 characteristics: Dict, template: Dict):
        """Add hair to avatar"""
        hair_style = characteristics.get("hair_style", "medium_straight")
        
        if hair_style == "short_curly":
            # Curly hair with multiple circles
            for i in range(5):
                curl = SubElement(svg, 'circle')
                curl_x = x + random.randint(-size//3, size//3)
                curl_y = y - size//2 + random.randint(-10, 10)
                curl.set('cx', str(curl_x))
                curl.set('cy', str(curl_y))
                curl.set('r', str(size//8))
                curl.set('fill', 'url(#hairGradient)')
                curl.set('stroke', '#000000')
                curl.set('stroke-width', '2')
        
        elif hair_style == "pigtails":
            # Main hair
            main_hair = SubElement(svg, 'ellipse')
            main_hair.set('cx', str(x))
            main_hair.set('cy', str(y - size//3))
            main_hair.set('rx', str(size//2))
            main_hair.set('ry', str(size//4))
            main_hair.set('fill', 'url(#hairGradient)')
            main_hair.set('stroke', '#000000')
            main_hair.set('stroke-width', '2')
            
            # Left pigtail
            left_pigtail = SubElement(svg, 'circle')
            left_pigtail.set('cx', str(x - size//2))
            left_pigtail.set('cy', str(y - size//4))
            left_pigtail.set('r', str(size//6))
            left_pigtail.set('fill', 'url(#hairGradient)')
            left_pigtail.set('stroke', '#000000')
            left_pigtail.set('stroke-width', '2')
            
            # Right pigtail
            right_pigtail = SubElement(svg, 'circle')
            right_pigtail.set('cx', str(x + size//2))
            right_pigtail.set('cy', str(y - size//4))
            right_pigtail.set('r', str(size//6))
            right_pigtail.set('fill', 'url(#hairGradient)')
            right_pigtail.set('stroke', '#000000')
            right_pigtail.set('stroke-width', '2')
        
        else:
            # Default medium hair
            hair = SubElement(svg, 'ellipse')
            hair.set('cx', str(x))
            hair.set('cy', str(y - size//3))
            hair.set('rx', str(int(size//2 * 1.1)))
            hair.set('ry', str(size//3))
            hair.set('fill', 'url(#hairGradient)')
            hair.set('stroke', '#000000')
            hair.set('stroke-width', '2')
    
    def _add_eyes(self, svg: Element, x: int, y: int, eye_size: float, characteristics: Dict):
        """Add eyes to avatar"""
        eye_color = self.eye_colors[characteristics.get("eye_color", "brown")]
        eye_radius = int(self.avatar_size[0] * eye_size)
        
        # Left eye
        left_eye_white = SubElement(svg, 'circle')
        left_eye_white.set('cx', str(x - eye_radius * 2))
        left_eye_white.set('cy', str(y))
        left_eye_white.set('r', str(eye_radius))
        left_eye_white.set('fill', '#FFFFFF')
        left_eye_white.set('stroke', '#000000')
        left_eye_white.set('stroke-width', '2')
        
        left_eye_iris = SubElement(svg, 'circle')
        left_eye_iris.set('cx', str(x - eye_radius * 2))
        left_eye_iris.set('cy', str(y))
        left_eye_iris.set('r', str(eye_radius // 2))
        left_eye_iris.set('fill', eye_color)
        
        left_eye_pupil = SubElement(svg, 'circle')
        left_eye_pupil.set('cx', str(x - eye_radius * 2))
        left_eye_pupil.set('cy', str(y))
        left_eye_pupil.set('r', str(eye_radius // 4))
        left_eye_pupil.set('fill', '#000000')
        
        # Right eye
        right_eye_white = SubElement(svg, 'circle')
        right_eye_white.set('cx', str(x + eye_radius * 2))
        right_eye_white.set('cy', str(y))
        right_eye_white.set('r', str(eye_radius))
        right_eye_white.set('fill', '#FFFFFF')
        right_eye_white.set('stroke', '#000000')
        right_eye_white.set('stroke-width', '2')
        
        right_eye_iris = SubElement(svg, 'circle')
        right_eye_iris.set('cx', str(x + eye_radius * 2))
        right_eye_iris.set('cy', str(y))
        right_eye_iris.set('r', str(eye_radius // 2))
        right_eye_iris.set('fill', eye_color)
        
        right_eye_pupil = SubElement(svg, 'circle')
        right_eye_pupil.set('cx', str(x + eye_radius * 2))
        right_eye_pupil.set('cy', str(y))
        right_eye_pupil.set('r', str(eye_radius // 4))
        right_eye_pupil.set('fill', '#000000')
    
    def _add_nose(self, svg: Element, x: int, y: int, characteristics: Dict):
        """Add nose to avatar"""
        # Simple nose - small ellipse
        nose = SubElement(svg, 'ellipse')
        nose.set('cx', str(x))
        nose.set('cy', str(y))
        nose.set('rx', '3')
        nose.set('ry', '5')
        nose.set('fill', self._darken_color(self.skin_tones[characteristics.get("skin_tone", "medium")], 0.1))
    
    def _add_mouth(self, svg: Element, x: int, y: int, characteristics: Dict):
        """Add mouth to avatar"""
        expression = characteristics.get("expression", "happy")
        
        if expression == "happy":
            # Smiling mouth
            mouth = SubElement(svg, 'path')
            mouth.set('d', f'M {x-15} {y} Q {x} {y+10} {x+15} {y}')
            mouth.set('stroke', '#000000')
            mouth.set('stroke-width', '3')
            mouth.set('fill', 'none')
        else:
            # Neutral mouth
            mouth = SubElement(svg, 'line')
            mouth.set('x1', str(x - 10))
            mouth.set('y1', str(y))
            mouth.set('x2', str(x + 10))
            mouth.set('y2', str(y))
            mouth.set('stroke', '#000000')
            mouth.set('stroke-width', '3')
    
    def _add_accessory(self, svg: Element, x: int, y: int, head_size: int, 
                      characteristics: Dict, theme: str):
        """Add accessories based on theme"""
        accessory = characteristics.get("accessory")
        
        if accessory == "crown":
            # Simple crown
            crown = SubElement(svg, 'polygon')
            points = f"{x-30},{y-head_size//2-10} {x-15},{y-head_size//2-25} {x},{y-head_size//2-30} {x+15},{y-head_size//2-25} {x+30},{y-head_size//2-10}"
            crown.set('points', points)
            crown.set('fill', '#FFD700')
            crown.set('stroke', '#000000')
            crown.set('stroke-width', '2')
        
        elif accessory == "hat":
            # Simple hat
            hat = SubElement(svg, 'ellipse')
            hat.set('cx', str(x))
            hat.set('cy', str(y - head_size//2 - 20))
            hat.set('rx', str(head_size//2 + 10))
            hat.set('ry', '15')
            hat.set('fill', '#8B4513')
            hat.set('stroke', '#000000')
            hat.set('stroke-width', '2')
    
    def _add_theme_decorations(self, svg: Element, theme: str, style: str):
        """Add theme-specific decorations"""
        if theme == "fantasy":
            # Add sparkles
            for i in range(5):
                sparkle = SubElement(svg, 'polygon')
                x = random.randint(50, self.avatar_size[0] - 50)
                y = random.randint(50, self.avatar_size[1] - 50)
                size = random.randint(3, 8)
                
                points = f"{x},{y-size} {x+size//2},{y-size//2} {x+size},{y} {x+size//2},{y+size//2} {x},{y+size} {x-size//2},{y+size//2} {x-size},{y} {x-size//2},{y-size//2}"
                sparkle.set('points', points)
                sparkle.set('fill', '#FFD700')
                sparkle.set('opacity', '0.7')
    
    def _add_castle_background(self, svg: Element):
        """Add castle background"""
        # Simple castle silhouette
        castle = SubElement(svg, 'rect')
        castle.set('x', '350')
        castle.set('y', '200')
        castle.set('width', '100')
        castle.set('height', '150')
        castle.set('fill', '#708090')
        castle.set('opacity', '0.3')
    
    def _add_forest_background(self, svg: Element):
        """Add forest background"""
        # Simple trees
        for i in range(3):
            tree_x = 100 + i * 150
            tree = SubElement(svg, 'ellipse')
            tree.set('cx', str(tree_x))
            tree.set('cy', '300')
            tree.set('rx', '40')
            tree.set('ry', '60')
            tree.set('fill', '#228B22')
            tree.set('opacity', '0.3')
    
    def _add_space_background(self, svg: Element):
        """Add space background"""
        # Stars
        for i in range(10):
            star = SubElement(svg, 'circle')
            star.set('cx', str(random.randint(50, self.avatar_size[0] - 50)))
            star.set('cy', str(random.randint(50, self.avatar_size[1] - 50)))
            star.set('r', '2')
            star.set('fill', '#FFFFFF')
            star.set('opacity', '0.8')
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor"""
        # Simple color lightening
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def _format_svg_string(self, svg_string: str) -> str:
        """Format SVG string for better readability"""
        # Basic formatting - could be enhanced
        return svg_string.replace('><', '>\n<')
    
    def _create_fallback_svg(self, age: int) -> str:
        """Create simple fallback SVG"""
        return f'''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <rect width="512" height="512" fill="#87CEEB"/>
            <circle cx="256" cy="200" r="80" fill="#FDBCB4" stroke="#000" stroke-width="3"/>
            <circle cx="236" cy="180" r="8" fill="#000"/>
            <circle cx="276" cy="180" r="8" fill="#000"/>
            <path d="M 236 210 Q 256 225 276 210" stroke="#000" stroke-width="3" fill="none"/>
            <ellipse cx="256" cy="120" rx="90" ry="40" fill="#8B4513"/>
            <rect x="206" y="280" width="100" height="120" rx="10" fill="#4ECDC4" stroke="#000" stroke-width="2"/>
            <text x="256" y="450" font-family="Arial" font-size="16" text-anchor="middle" fill="#000">Age {age} Avatar</text>
        </svg>'''
    
    def get_customization_options(self) -> Dict:
        """Get available customization options"""
        return {
            "skin_tones": list(self.skin_tones.keys()),
            "hair_colors": list(self.hair_colors.keys()),
            "eye_colors": list(self.eye_colors.keys()),
            "clothing_colors": list(self.clothing_colors.keys()),
            "themes": list(self.theme_elements.keys()),
            "expressions": ["happy", "neutral", "excited", "calm"],
            "hair_styles": ["short_curly", "pigtails", "bob", "medium_straight", "braids", "ponytail", "long_straight"],
            "clothing_styles": ["casual", "dress", "formal", "sporty", "costume"]
        }

# Global instance for easy access
template_avatar_generator = TemplateAvatarGenerator()