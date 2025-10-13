"""Image processing utilities for Rekognition integration."""

import io
import logging
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Utilities for processing images for emotion detection."""
    
    def __init__(self):
        self.max_image_size = (1024, 1024)  # Max size for processing
        self.min_image_size = (64, 64)      # Min size for face detection
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF']
    
    def validate_image(self, image_data: bytes) -> bool:
        """Validate that image data is in a supported format."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in self.supported_formats:
                logger.warning(f"Unsupported image format: {image.format}")
                return False
            
            # Check size
            width, height = image.size
            if width < self.min_image_size[0] or height < self.min_image_size[1]:
                logger.warning(f"Image too small: {width}x{height}")
                return False
            
            # Check if image has content
            if width * height < 100:  # Very small image
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess image for optimal emotion detection."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            # Enhance image quality
            image = self._enhance_image_quality(image)
            
            # Convert back to bytes
            output_io = io.BytesIO()
            image.save(output_io, format='JPEG', quality=85, optimize=True)
            return output_io.getvalue()
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_data  # Return original on failure
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better face detection."""
        try:
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Enhance sharpness slightly
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Reduce noise with a mild blur
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            return image
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image
    
    def extract_face_region(self, image_data: bytes, face_bbox: Dict[str, float]) -> Optional[bytes]:
        """Extract face region from image based on bounding box."""
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Convert relative coordinates to absolute
            left = int(face_bbox['Left'] * width)
            top = int(face_bbox['Top'] * height)
            right = int((face_bbox['Left'] + face_bbox['Width']) * width)
            bottom = int((face_bbox['Top'] + face_bbox['Height']) * height)
            
            # Add some padding around the face
            padding = 20
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(width, right + padding)
            bottom = min(height, bottom + padding)
            
            # Crop the face region
            face_image = image.crop((left, top, right, bottom))
            
            # Convert to bytes
            output_io = io.BytesIO()
            face_image.save(output_io, format='JPEG', quality=90)
            return output_io.getvalue()
            
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return None
    
    def analyze_image_quality(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image quality metrics."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Calculate basic quality metrics
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Estimate blur using Laplacian variance
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # Simple blur detection using gradient magnitude
            grad_x = np.abs(np.diff(gray, axis=1))
            grad_y = np.abs(np.diff(gray, axis=0))
            sharpness = np.mean(grad_x) + np.mean(grad_y)
            
            return {
                "width": image.size[0],
                "height": image.size[1],
                "brightness": float(brightness),
                "contrast": float(contrast),
                "sharpness": float(sharpness),
                "format": image.format,
                "mode": image.mode
            }
            
        except Exception as e:
            logger.error(f"Image quality analysis failed: {e}")
            return {}
    
    def create_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (150, 150)) -> bytes:
        """Create a thumbnail of the image."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            output_io = io.BytesIO()
            image.save(output_io, format='JPEG', quality=80)
            return output_io.getvalue()
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            return image_data
    
    def detect_lighting_conditions(self, image_data: bytes) -> Dict[str, Any]:
        """Detect lighting conditions in the image."""
        try:
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image)
            
            # Convert to grayscale for analysis
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # Analyze brightness distribution
            brightness_mean = np.mean(gray)
            brightness_std = np.std(gray)
            
            # Classify lighting conditions
            if brightness_mean < 50:
                lighting = "dark"
            elif brightness_mean > 200:
                lighting = "bright"
            else:
                lighting = "normal"
            
            # Check for backlighting (high contrast)
            if brightness_std > 60:
                backlighting = True
            else:
                backlighting = False
            
            return {
                "lighting": lighting,
                "brightness_mean": float(brightness_mean),
                "brightness_std": float(brightness_std),
                "backlighting": backlighting,
                "quality_score": min(1.0, (255 - abs(brightness_mean - 128)) / 127)
            }
            
        except Exception as e:
            logger.error(f"Lighting analysis failed: {e}")
            return {"lighting": "unknown", "quality_score": 0.5}
    
    def prepare_for_rekognition(self, image_data: bytes) -> bytes:
        """Prepare image specifically for AWS Rekognition."""
        try:
            # Validate and preprocess
            if not self.validate_image(image_data):
                raise ValueError("Invalid image format")
            
            processed_image = self.preprocess_image(image_data)
            
            # Ensure image is not too large for Rekognition (5MB limit)
            if len(processed_image) > 5 * 1024 * 1024:  # 5MB
                # Reduce quality to fit size limit
                image = Image.open(io.BytesIO(processed_image))
                output_io = io.BytesIO()
                
                # Try different quality levels
                for quality in [70, 60, 50, 40]:
                    output_io.seek(0)
                    output_io.truncate()
                    image.save(output_io, format='JPEG', quality=quality, optimize=True)
                    
                    if len(output_io.getvalue()) <= 5 * 1024 * 1024:
                        break
                
                processed_image = output_io.getvalue()
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Rekognition preparation failed: {e}")
            return image_data