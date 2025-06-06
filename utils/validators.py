import os
import io
from PIL import Image
import logging
from typing import Tuple, Optional, Union
from config.constants import IMAGE_PROCESSING, VALIDATION_RULES, ERROR_MESSAGES

class ImageValidator:
    """Validator for uploaded satellite images"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_file_size = IMAGE_PROCESSING['max_file_size_mb'] * 1024 * 1024  # Convert to bytes
        self.supported_formats = IMAGE_PROCESSING['supported_formats']
        self.min_resolution = IMAGE_PROCESSING['min_resolution']
        self.max_resolution = IMAGE_PROCESSING['max_resolution']
    
    def validate_image(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded image file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        
        try:
            # Check if file exists
            if uploaded_file is None:
                return False, "No file uploaded"
            
            # Check file size
            if hasattr(uploaded_file, 'size') and uploaded_file.size > self.max_file_size:
                return False, ERROR_MESSAGES['image_upload']['file_too_large']
            
            # Check file format by extension
            file_extension = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else ''
            if file_extension not in self.supported_formats:
                return False, ERROR_MESSAGES['image_upload']['invalid_format']
            
            # Try to open and validate the image
            try:
                # Reset file pointer if it's a BytesIO object
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                
                # Open image using PIL
                image = Image.open(uploaded_file)
                
                # Verify it's a valid image
                image.verify()
                
                # Reset file pointer again for further use
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                
                # Re-open for dimension checking (verify() closes the image)
                image = Image.open(uploaded_file)
                width, height = image.size
                
                # Check minimum resolution
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    return False, ERROR_MESSAGES['image_upload']['resolution_too_low']
                
                # Check maximum resolution
                if width > self.max_resolution[0] or height > self.max_resolution[1]:
                    return False, ERROR_MESSAGES['image_upload']['resolution_too_high']
                
                # Check if image has valid color mode
                valid_modes = ['RGB', 'RGBA', 'L', 'P']
                if image.mode not in valid_modes:
                    return False, "Image format not supported for analysis"
                
                # Reset file pointer for final use
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                
                return True, "Image validation successful"
                
            except Exception as e:
                self.logger.error(f"Image validation failed: {str(e)}")
                return False, ERROR_MESSAGES['image_upload']['corrupted_file']
                
        except Exception as e:
            self.logger.error(f"Image validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"

class InputValidator:
    """Validator for user inputs and parameters"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_coordinates(self, latitude: float, longitude: float) -> Tuple[bool, str]:
        """Validate latitude and longitude coordinates"""
        
        try:
            lat_range = VALIDATION_RULES['latitude_range']
            lon_range = VALIDATION_RULES['longitude_range']
            
            if not (lat_range[0] <= latitude <= lat_range[1]):
                return False, f"Latitude must be between {lat_range[0]} and {lat_range[1]}"
            
            if not (lon_range[0] <= longitude <= lon_range[1]):
                return False, f"Longitude must be between {lon_range[0]} and {lon_range[1]}"
            
            return True, "Coordinates are valid"
            
        except Exception as e:
            self.logger.error(f"Coordinate validation error: {str(e)}")
            return False, f"Invalid coordinate format: {str(e)}"
    
    def validate_electricity_rate(self, rate: float) -> Tuple[bool, str]:
        """Validate electricity rate input"""
        
        try:
            rate_range = VALIDATION_RULES['electricity_rate_range']
            
            if not isinstance(rate, (int, float)):
                return False, "Electricity rate must be a number"
            
            if not (rate_range[0] <= rate <= rate_range[1]):
                return False, f"Electricity rate must be between ${rate_range[0]:.3f} and ${rate_range[1]:.3f} per kWh"
            
            return True, "Electricity rate is valid"
            
        except Exception as e:
            self.logger.error(f"Electricity rate validation error: {str(e)}")
            return False, f"Invalid electricity rate: {str(e)}"
    
    def validate_installation_cost(self, cost: float) -> Tuple[bool, str]:
        """Validate installation cost per watt"""
        
        try:
            cost_range = VALIDATION_RULES['installation_cost_range']
            
            if not isinstance(cost, (int, float)):
                return False, "Installation cost must be a number"
            
            if not (cost_range[0] <= cost <= cost_range[1]):
                return False, f"Installation cost must be between ${cost_range[0]:.2f} and ${cost_range[1]:.2f} per watt"
            
            return True, "Installation cost is valid"
            
        except Exception as e:
            self.logger.error(f"Installation cost validation error: {str(e)}")
            return False, f"Invalid installation cost: {str(e)}"
    
    def validate_roof_area(self, area: float) -> Tuple[bool, str]:
        """Validate roof area input"""
        
        try:
            area_range = VALIDATION_RULES['roof_area_range']
            
            if not isinstance(area, (int, float)):
                return False, "Roof area must be a number"
            
            if area <= 0:
                return False, "Roof area must be positive"
            
            if not (area_range[0] <= area <= area_range[1]):
                return False, f"Roof area must be between {area_range[0]} and {area_range[1]} square meters"
            
            return True, "Roof area is valid"
            
        except Exception as e:
            self.logger.error(f"Roof area validation error: {str(e)}")
            return False, f"Invalid roof area: {str(e)}"
    
    def validate_system_size(self, size_kw: float) -> Tuple[bool, str]:
        """Validate solar system size"""
        
        try:
            size_range = VALIDATION_RULES['system_size_range']
            
            if not isinstance(size_kw, (int, float)):
                return False, "System size must be a number"
            
            if size_kw <= 0:
                return False, "System size must be positive"
            
            if not (size_range[0] <= size_kw <= size_range[1]):
                return False, f"System size must be between {size_range[0]} and {size_range[1]} kW"
            
            return True, "System size is valid"
            
        except Exception as e:
            self.logger.error(f"System size validation error: {str(e)}")
            return False, f"Invalid system size: {str(e)}"

class APIValidator:
    """Validator for API responses and data quality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_nasa_response(self, response_data: dict) -> Tuple[bool, str]:
        """Validate NASA API response data"""
        
        try:
            if not isinstance(response_data, dict):
                return False, "Invalid NASA API response format"
            
            # Check for required fields
            if 'properties' not in response_data:
                return False, "Missing properties in NASA API response"
            
            if 'parameter' not in response_data['properties']:
                return False, "Missing parameter data in NASA API response"
            
            # Check for solar irradiance data
            parameters = response_data['properties']['parameter']
            if 'ALLSKY_SFC_SW_DWN' not in parameters:
                return False, "Missing solar irradiance data in NASA API response"
            
            # Validate data values
            irradiance_data = parameters['ALLSKY_SFC_SW_DWN']
            if not isinstance(irradiance_data, dict):
                return False, "Invalid irradiance data format"
            
            # Check for reasonable values
            valid_values = []
            for year_data in irradiance_data.values():
                if isinstance(year_data, dict):
                    for value in year_data.values():
                        if isinstance(value, (int, float)) and 0 < value < 15:  # Reasonable daily irradiance range
                            valid_values.append(value)
            
            if len(valid_values) < 5:  # Need at least some valid data points
                return False, "Insufficient valid irradiance data"
            
            return True, "NASA API response is valid"
            
        except Exception as e:
            self.logger.error(f"NASA API validation error: {str(e)}")
            return False, f"NASA API validation failed: {str(e)}"
    
    def validate_llm_response(self, response_text: str) -> Tuple[bool, str]:
        """Validate LLM API response"""
        
        try:
            if not isinstance(response_text, str):
                return False, "LLM response must be text"
            
            if len(response_text.strip()) < 50:
                return False, "LLM response is too short"
            
            if len(response_text) > 10000:
                return False, "LLM response is too long"
            
            # Check for common error indicators
            error_indicators = [
                "error occurred",
                "cannot process",
                "invalid request",
                "service unavailable"
            ]
            
            response_lower = response_text.lower()
            for indicator in error_indicators:
                if indicator in response_lower:
                    return False, f"LLM response contains error: {indicator}"
            
            return True, "LLM response is valid"
            
        except Exception as e:
            self.logger.error(f"LLM response validation error: {str(e)}")
            return False, f"LLM response validation failed: {str(e)}"
    
    def validate_calculation_results(self, results: dict) -> Tuple[bool, str]:
        """Validate solar calculation results for reasonableness"""
        
        try:
            if not isinstance(results, dict):
                return False, "Results must be a dictionary"
            
            # Required fields
            required_fields = [
                'system_size_kw', 'annual_energy_kwh', 'total_cost', 
                'annual_savings', 'payback_years'
            ]
            
            for field in required_fields:
                if field not in results:
                    return False, f"Missing required field: {field}"
                
                value = results[field]
                if not isinstance(value, (int, float)) or value < 0:
                    return False, f"Invalid value for {field}: {value}"
            
            # Reasonableness checks
            system_size = results['system_size_kw']
            annual_energy = results['annual_energy_kwh']
            total_cost = results['total_cost']
            annual_savings = results['annual_savings']
            payback_years = results['payback_years']
            
            # System size should be reasonable for residential
            if system_size > 100:
                return False, f"System size too large: {system_size} kW"
            
            # Energy production should be reasonable (800-2000 kWh/kW/year typical)
            energy_per_kw = annual_energy / system_size if system_size > 0 else 0
            if energy_per_kw < 500 or energy_per_kw > 3000:
                return False, f"Energy production per kW unrealistic: {energy_per_kw:.1f} kWh/kW/year"
            
            # Cost should be reasonable ($1-10 per watt)
            cost_per_watt = total_cost / (system_size * 1000) if system_size > 0 else 0
            if cost_per_watt < 0.5 or cost_per_watt > 15:
                return False, f"Cost per watt unrealistic: ${cost_per_watt:.2f}/W"
            
            # Payback period should be reasonable (1-50 years)
            if payback_years < 1 or payback_years > 50:
                return False, f"Payback period unrealistic: {payback_years:.1f} years"
            
            return True, "Calculation results are valid"
            
        except Exception as e:
            self.logger.error(f"Calculation validation error: {str(e)}")
            return False, f"Calculation validation failed: {str(e)}"

class EnvironmentValidator:
    """Validator for environment variables and API keys"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_api_keys(self) -> Tuple[bool, str]:
        """Validate that required API keys are available"""
        
        try:
            # Check Google LLM API key
            google_key = os.getenv("GOOGLE_LLM_API_KEY")
            if not google_key:
                self.logger.warning("Google LLM API key not found in environment")
                return False, "Google LLM API key not configured"
            
            if len(google_key) < 20:  # Basic length check
                return False, "Google LLM API key appears invalid"
            
            # Check NASA API key
            nasa_key = os.getenv("NASA_API_KEY")
            if not nasa_key:
                self.logger.warning("NASA API key not found in environment")
                return False, "NASA API key not configured"
            
            if len(nasa_key) < 20:  # Basic length check
                return False, "NASA API key appears invalid"
            
            return True, "API keys are configured"
            
        except Exception as e:
            self.logger.error(f"API key validation error: {str(e)}")
            return False, f"API key validation failed: {str(e)}"
    
    def validate_environment(self) -> Tuple[bool, str]:
        """Validate overall environment setup"""
        
        try:
            issues = []
            
            # Check API keys
            api_valid, api_msg = self.validate_api_keys()
            if not api_valid:
                issues.append(f"API configuration: {api_msg}")
            
            # Check Python environment
            try:
                import cv2
                import numpy as np
                import pandas as pd
                import plotly
                import google.generativeai as genai
                from reportlab.platypus import SimpleDocTemplate
            except ImportError as e:
                issues.append(f"Missing required package: {str(e)}")
            
            if issues:
                return False, "; ".join(issues)
            
            return True, "Environment validation successful"
            
        except Exception as e:
            self.logger.error(f"Environment validation error: {str(e)}")
            return False, f"Environment validation failed: {str(e)}"

# Utility functions for common validation tasks
def is_valid_image_format(filename: str) -> bool:
    """Check if filename has a valid image format"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in IMAGE_PROCESSING['supported_formats']

def is_reasonable_coordinates(latitude: float, longitude: float) -> bool:
    """Quick check for reasonable coordinate values"""
    try:
        lat_range = VALIDATION_RULES['latitude_range']
        lon_range = VALIDATION_RULES['longitude_range']
        
        return (lat_range[0] <= latitude <= lat_range[1] and 
                lon_range[0] <= longitude <= lon_range[1])
    except:
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage"""
    import re
    
    if not filename:
        return "unknown_file"
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace unsafe characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename
