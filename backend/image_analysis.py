import cv2
import numpy as np
import logging
from typing import Dict, List

class RoofAnalyzer:
    """Computer vision pipeline for analyzing rooftop characteristics from satellite imagery"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_roof(self, image_path: str) -> Dict:
        """
        Analyze roof characteristics from satellite image
        
        Args:
            image_path: Path to the satellite image
            
        Returns:
            Dictionary containing roof analysis results
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Image is already loaded in BGR format for OpenCV processing
            
            # Perform roof detection and analysis
            roof_contours = self._detect_roof_area(image)
            roof_metrics = self._calculate_roof_metrics(image, roof_contours)
            orientation = self._estimate_roof_orientation(roof_contours)
            slope = self._estimate_roof_slope(image, roof_contours)
            shading_factor = self._analyze_shading(image)
            obstructions = self._detect_obstructions(image, roof_contours)
            
            return {
                'total_area': roof_metrics['total_area'],
                'usable_area': roof_metrics['usable_area'],
                'orientation': orientation,
                'slope': slope,
                'shading_factor': shading_factor,
                'obstruction_count': len(obstructions),
                'obstructions': obstructions,
                'confidence_score': roof_metrics['confidence'],
                'analysis_metadata': {
                    'image_dimensions': image.shape[:2],
                    'processing_successful': True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Roof analysis failed: {str(e)}")
            # Return default values with low confidence
            return self._get_default_roof_metrics()
    
    def _detect_roof_area(self, image: np.ndarray) -> List[np.ndarray]:
        """Detect roof areas using computer vision techniques"""
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Use adaptive thresholding to handle varying lighting
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Apply morphological operations to clean up the image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by area (assuming roof is a significant portion of image)
            min_area = (image.shape[0] * image.shape[1]) * 0.1  # At least 10% of image
            max_area = (image.shape[0] * image.shape[1]) * 0.8  # At most 80% of image
            
            roof_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    # Additional filtering based on shape characteristics
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        # Roofs are typically not too circular (0.1 to 0.9 range)
                        if 0.1 < circularity < 0.9:
                            roof_contours.append(contour)
            
            # If no good contours found, create a default rectangular contour
            if not roof_contours:
                h, w = image.shape[:2]
                default_contour = np.array([
                    [[w//4, h//4]], [[3*w//4, h//4]], 
                    [[3*w//4, 3*h//4]], [[w//4, 3*h//4]]
                ])
                roof_contours.append(default_contour)
            
            return roof_contours
            
        except Exception as e:
            self.logger.error(f"Roof detection failed: {str(e)}")
            # Return default contour
            h, w = image.shape[:2]
            default_contour = np.array([
                [[w//4, h//4]], [[3*w//4, h//4]], 
                [[3*w//4, 3*h//4]], [[w//4, 3*h//4]]
            ])
            return [default_contour]
    
    def _calculate_roof_metrics(self, image: np.ndarray, contours: List[np.ndarray]) -> Dict:
        """Calculate roof area and other metrics"""
        
        try:
            if not contours:
                raise ValueError("No contours provided")
            
            # Assume typical residential roof - estimate scale from image size
            # This is a simplified approach - in practice, you'd need actual scale information
            image_height, image_width = image.shape[:2]
            
            # Estimate scale: assume image covers roughly 50m x 50m area
            meters_per_pixel_x = 50.0 / image_width
            meters_per_pixel_y = 50.0 / image_height
            
            total_area_pixels = 0
            for contour in contours:
                area_pixels = cv2.contourArea(contour)
                total_area_pixels += area_pixels
            
            # Convert to square meters
            total_area_m2 = total_area_pixels * meters_per_pixel_x * meters_per_pixel_y
            
            # Calculate usable area (accounting for setbacks, obstructions, etc.)
            # Typically 70-85% of total roof area is usable for solar panels
            usable_percentage = 0.75  # Conservative estimate
            usable_area_m2 = total_area_m2 * usable_percentage
            
            # Confidence score based on contour quality
            confidence = min(1.0, len(contours) * 0.3 + 0.4)
            
            return {
                'total_area': total_area_m2,
                'usable_area': usable_area_m2,
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Metric calculation failed: {str(e)}")
            # Return conservative estimates
            return {
                'total_area': 100.0,  # 100 m² default
                'usable_area': 75.0,   # 75 m² usable
                'confidence': 0.3
            }
    
    def _estimate_roof_orientation(self, contours: List[np.ndarray]) -> str:
        """Estimate primary roof orientation"""
        
        try:
            if not contours:
                return "south"  # Default optimal orientation
            
            # Get the largest contour (main roof section)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Fit a rectangle to estimate orientation
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Convert angle to cardinal direction
            # Normalize angle to 0-360 degrees
            if angle < -45:
                angle += 90
            
            # Map angle to orientation
            if -22.5 <= angle <= 22.5:
                return "south"
            elif 22.5 < angle <= 67.5:
                return "southwest"
            elif 67.5 < angle <= 112.5:
                return "west"
            elif 112.5 < angle <= 157.5:
                return "northwest"
            elif 157.5 < angle <= 202.5:
                return "north"
            elif 202.5 < angle <= 247.5:
                return "northeast"
            elif 247.5 < angle <= 292.5:
                return "east"
            else:
                return "southeast"
                
        except Exception as e:
            self.logger.error(f"Orientation estimation failed: {str(e)}")
            return "south"  # Default to optimal orientation
    
    def _estimate_roof_slope(self, image: np.ndarray, contours: List[np.ndarray]) -> float:
        """Estimate roof slope in degrees"""
        
        try:
            # For satellite imagery, slope estimation is challenging
            # We'll use image analysis techniques to estimate based on shadows and perspective
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate gradient to detect slope indicators
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Analyze gradient within roof area
            if contours:
                mask = np.zeros(gray.shape, np.uint8)
                cv2.fillPoly(mask, contours, (255,))
                roof_gradients = gradient_magnitude[mask > 0]

                # Use gradient statistics to estimate slope
                mean_gradient = np.mean(roof_gradients)

                # Map gradient to slope (empirical relationship)
                # Higher gradients suggest steeper roofs
                slope_degrees = min(45.0, max(5.0, float(mean_gradient * 0.5)))
            else:
                slope_degrees = 25.0  # Average residential roof slope
                
            return slope_degrees
            
        except Exception as e:
            self.logger.error(f"Slope estimation failed: {str(e)}")
            return 25.0  # Default slope
    
    def _analyze_shading(self, image: np.ndarray) -> float:
        """Analyze shading factors from the image"""
        
        try:
            # Convert to HSV for better shadow detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create mask for dark areas (potential shadows)
            lower_shadow = np.array([0, 0, 0])
            upper_shadow = np.array([180, 255, 100])  # Low value channel for shadows
            shadow_mask = cv2.inRange(hsv, lower_shadow, upper_shadow)
            
            # Calculate percentage of image that's in shadow
            total_pixels = image.shape[0] * image.shape[1]
            shadow_pixels = np.sum(shadow_mask > 0)
            shadow_percentage = shadow_pixels / total_pixels
            
            # Convert to shading factor (0 = no shading, 1 = completely shaded)
            # Invert the logic: less shadow = better for solar
            shading_factor = min(0.8, shadow_percentage * 2)  # Cap at 80% shading
            
            return shading_factor
            
        except Exception as e:
            self.logger.error(f"Shading analysis failed: {str(e)}")
            return 0.2  # Default minimal shading
    
    def _detect_obstructions(self, image: np.ndarray, roof_contours: List[np.ndarray]) -> List[Dict]:
        """Detect potential obstructions on the roof"""
        
        try:
            obstructions = []
            
            # Create mask for roof area
            if roof_contours:
                mask = np.zeros(image.shape[:2], np.uint8)
                cv2.fillPoly(mask, roof_contours, (255,))
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect circular objects (potential vents, chimneys)
                circles = cv2.HoughCircles(
                    gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                    param1=50, param2=30, minRadius=5, maxRadius=50
                )
                
                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    for (x, y, r) in circles:
                        # Check if circle is within roof area
                        if mask[y, x] > 0:
                            obstructions.append({
                                'type': 'circular_obstruction',
                                'position': {'x': int(x), 'y': int(y)},
                                'size': int(r),
                                'estimated_area_m2': (r * 0.1) ** 2 * np.pi  # Rough conversion
                            })
                
                # Detect rectangular objects using contour analysis
                edges = cv2.Canny(gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 50 < area < 5000:  # Filter by reasonable obstruction size
                        # Check if contour is within roof area
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            
                            if mask[cy, cx] > 0:
                                # Approximate contour to check if it's rectangular-ish
                                epsilon = 0.02 * cv2.arcLength(contour, True)
                                approx = cv2.approxPolyDP(contour, epsilon, True)
                                
                                if len(approx) >= 4:  # Roughly rectangular
                                    obstructions.append({
                                        'type': 'rectangular_obstruction',
                                        'position': {'x': cx, 'y': cy},
                                        'vertices': len(approx),
                                        'estimated_area_m2': area * 0.01  # Rough conversion
                                    })
            
            return obstructions[:10]  # Limit to 10 obstructions
            
        except Exception as e:
            self.logger.error(f"Obstruction detection failed: {str(e)}")
            return []
    
    def _get_default_roof_metrics(self) -> Dict:
        """Return default roof metrics when analysis fails"""
        
        return {
            'total_area': 120.0,
            'usable_area': 90.0,
            'orientation': 'south',
            'slope': 25.0,
            'shading_factor': 0.15,
            'obstruction_count': 2,
            'obstructions': [
                {
                    'type': 'estimated_obstruction',
                    'position': {'x': 0, 'y': 0},
                    'estimated_area_m2': 2.0
                }
            ],
            'confidence_score': 0.2,
            'analysis_metadata': {
                'image_dimensions': (0, 0),
                'processing_successful': False,
                'fallback_used': True
            }
        }
