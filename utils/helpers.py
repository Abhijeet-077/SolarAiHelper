import re
import math
import logging
from typing import Union, Optional, List, Dict, Any
from datetime import datetime, timedelta
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

def format_currency(amount: Union[int, float], currency: str = "USD", include_symbol: bool = True) -> str:
    """
    Format a number as currency
    
    Args:
        amount: The amount to format
        currency: Currency code (default: USD)
        include_symbol: Whether to include currency symbol
    
    Returns:
        Formatted currency string
    """
    try:
        if not isinstance(amount, (int, float)):
            return "$0"
        
        # Handle negative amounts
        is_negative = amount < 0
        amount = abs(amount)
        
        # Format with thousands separators
        if amount >= 1000000:
            formatted = f"${amount:,.0f}"
        elif amount >= 1000:
            formatted = f"${amount:,.0f}"
        else:
            formatted = f"${amount:.2f}"
        
        # Add negative sign if needed
        if is_negative:
            formatted = "-" + formatted
        
        return formatted
        
    except Exception as e:
        logger.error(f"Currency formatting error: {str(e)}")
        return "$0"

def format_number(number: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format a number with appropriate decimal places and thousands separators
    
    Args:
        number: The number to format
        decimal_places: Number of decimal places to show
    
    Returns:
        Formatted number string
    """
    try:
        if not isinstance(number, (int, float)):
            return "0"
        
        if math.isnan(number) or math.isinf(number):
            return "0"
        
        # Handle very large numbers
        if abs(number) >= 1000000:
            return f"{number:,.0f}"
        elif abs(number) >= 1000:
            return f"{number:,.{decimal_places}f}"
        else:
            return f"{number:.{decimal_places}f}"
            
    except Exception as e:
        logger.error(f"Number formatting error: {str(e)}")
        return "0"

def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format a value as a percentage
    
    Args:
        value: The value to format (0.25 = 25%)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    try:
        if not isinstance(value, (int, float)):
            return "0%"
        
        percentage = value * 100
        return f"{percentage:.{decimal_places}f}%"
        
    except Exception as e:
        logger.error(f"Percentage formatting error: {str(e)}")
        return "0%"

def format_energy(kwh: Union[int, float], unit: str = "kWh") -> str:
    """
    Format energy values with appropriate units
    
    Args:
        kwh: Energy value in kWh
        unit: Unit to display
    
    Returns:
        Formatted energy string
    """
    try:
        if not isinstance(kwh, (int, float)):
            return f"0 {unit}"
        
        if kwh >= 1000000:
            return f"{kwh/1000000:.1f} GWh"
        elif kwh >= 1000:
            return f"{kwh/1000:.1f} MWh"
        else:
            return f"{kwh:.0f} {unit}"
            
    except Exception as e:
        logger.error(f"Energy formatting error: {str(e)}")
        return f"0 {unit}"

def format_area(area_m2: Union[int, float], unit: str = "m²") -> str:
    """
    Format area values
    
    Args:
        area_m2: Area in square meters
        unit: Unit to display
    
    Returns:
        Formatted area string
    """
    try:
        if not isinstance(area_m2, (int, float)):
            return f"0 {unit}"
        
        if area_m2 >= 10000:  # 1 hectare
            return f"{area_m2/10000:.2f} ha"
        else:
            return f"{area_m2:.1f} {unit}"
            
    except Exception as e:
        logger.error(f"Area formatting error: {str(e)}")
        return f"0 {unit}"

def format_power(watts: Union[int, float]) -> str:
    """
    Format power values with appropriate units
    
    Args:
        watts: Power in watts
    
    Returns:
        Formatted power string
    """
    try:
        if not isinstance(watts, (int, float)):
            return "0 W"
        
        if watts >= 1000000:
            return f"{watts/1000000:.1f} MW"
        elif watts >= 1000:
            return f"{watts/1000:.1f} kW"
        else:
            return f"{watts:.0f} W"
            
    except Exception as e:
        logger.error(f"Power formatting error: {str(e)}")
        return "0 W"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    try:
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r
        
    except Exception as e:
        logger.error(f"Distance calculation error: {str(e)}")
        return 0.0

def interpolate_monthly_data(data_points: List[float], target_months: int = 12) -> List[float]:
    """
    Interpolate data to create monthly values
    
    Args:
        data_points: Available data points
        target_months: Number of months to generate
    
    Returns:
        List of interpolated monthly values
    """
    try:
        if not data_points or len(data_points) == 0:
            return [0.0] * target_months
        
        if len(data_points) >= target_months:
            return data_points[:target_months]
        
        # Simple linear interpolation
        result = []
        step = len(data_points) / target_months
        
        for i in range(target_months):
            index = i * step
            lower_idx = int(index)
            upper_idx = min(lower_idx + 1, len(data_points) - 1)
            
            if lower_idx == upper_idx:
                result.append(data_points[lower_idx])
            else:
                # Linear interpolation
                weight = index - lower_idx
                value = data_points[lower_idx] * (1 - weight) + data_points[upper_idx] * weight
                result.append(value)
        
        return result
        
    except Exception as e:
        logger.error(f"Interpolation error: {str(e)}")
        return [0.0] * target_months

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], 
                default: Union[int, float] = 0) -> float:
    """
    Safely divide two numbers, returning default if division by zero
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value if division by zero
    
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception as e:
        logger.error(f"Safe divide error: {str(e)}")
        return default

def calculate_monthly_averages(annual_data: Dict[str, Dict[str, float]]) -> List[float]:
    """
    Calculate monthly averages from annual data
    
    Args:
        annual_data: Dictionary with year keys and month-value dictionaries
    
    Returns:
        List of 12 monthly average values
    """
    try:
        monthly_sums = {}
        monthly_counts = {}
        
        # Initialize months 1-12
        for month in range(1, 13):
            monthly_sums[month] = 0.0
            monthly_counts[month] = 0
        
        # Process each year
        for year_data in annual_data.values():
            if isinstance(year_data, dict):
                for month_str, value in year_data.items():
                    try:
                        month = int(month_str)
                        if 1 <= month <= 12 and isinstance(value, (int, float)) and value > 0:
                            monthly_sums[month] += value
                            monthly_counts[month] += 1
                    except (ValueError, TypeError):
                        continue
        
        # Calculate averages
        monthly_averages = []
        for month in range(1, 13):
            if monthly_counts[month] > 0:
                average = monthly_sums[month] / monthly_counts[month]
                monthly_averages.append(average)
            else:
                # Use seasonal estimate if no data
                monthly_averages.append(estimate_monthly_value(month, monthly_averages))
        
        return monthly_averages
        
    except Exception as e:
        logger.error(f"Monthly average calculation error: {str(e)}")
        return [0.0] * 12

def estimate_monthly_value(month: int, existing_data: List[float]) -> float:
    """
    Estimate a monthly value based on seasonal patterns
    
    Args:
        month: Month number (1-12)
        existing_data: Any existing monthly data for reference
    
    Returns:
        Estimated monthly value
    """
    try:
        # Seasonal multipliers for Northern Hemisphere
        seasonal_multipliers = [
            0.6,   # January
            0.7,   # February
            0.85,  # March
            1.0,   # April
            1.15,  # May
            1.2,   # June
            1.2,   # July
            1.1,   # August
            0.95,  # September
            0.8,   # October
            0.65,  # November
            0.55   # December
        ]
        
        if existing_data and len(existing_data) > 0:
            # Use average of existing data as baseline
            valid_data = [x for x in existing_data if x > 0]
            baseline = np.mean(valid_data) if valid_data else 4.5
        else:
            baseline = 4.5  # Default baseline for solar irradiance
        
        month_index = month - 1  # Convert to 0-based index
        if 0 <= month_index < len(seasonal_multipliers):
            return baseline * seasonal_multipliers[month_index]
        else:
            return baseline
            
    except Exception as e:
        logger.error(f"Monthly value estimation error: {str(e)}")
        return 4.5

def clean_text_for_report(text: str) -> str:
    """
    Clean text for use in PDF reports
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text suitable for PDF generation
    """
    try:
        if not isinstance(text, str):
            return ""
        
        # Remove problematic characters
        text = text.replace('\u2019', "'")  # Replace smart quotes
        text = text.replace('\u2018', "'")
        text = text.replace('\u201c', '"')
        text = text.replace('\u201d', '"')
        text = text.replace('\u2013', '-')  # Replace em dash
        text = text.replace('\u2014', '-')
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Ensure reasonable length
        if len(text) > 5000:
            text = text[:4997] + "..."
        
        return text
        
    except Exception as e:
        logger.error(f"Text cleaning error: {str(e)}")
        return ""

def validate_and_clamp(value: Union[int, float], min_val: Union[int, float], 
                      max_val: Union[int, float], default: Union[int, float]) -> float:
    """
    Validate a value and clamp it to a range
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default: Default value if validation fails
    
    Returns:
        Clamped value or default
    """
    try:
        if not isinstance(value, (int, float)):
            return default
        
        if math.isnan(value) or math.isinf(value):
            return default
        
        return max(min_val, min(max_val, value))
        
    except Exception as e:
        logger.error(f"Value validation error: {str(e)}")
        return default

def create_summary_stats(data: List[Union[int, float]]) -> Dict[str, float]:
    """
    Create summary statistics for a dataset
    
    Args:
        data: List of numeric values
    
    Returns:
        Dictionary with summary statistics
    """
    try:
        if not data or len(data) == 0:
            return {
                'count': 0,
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std': 0.0
            }
        
        # Filter valid numeric values
        valid_data = [x for x in data if isinstance(x, (int, float)) and not (math.isnan(x) or math.isinf(x))]
        
        if not valid_data:
            return {
                'count': 0,
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std': 0.0
            }
        
        valid_data = np.array(valid_data)
        
        return {
            'count': len(valid_data),
            'mean': float(np.mean(valid_data)),
            'median': float(np.median(valid_data)),
            'min': float(np.min(valid_data)),
            'max': float(np.max(valid_data)),
            'std': float(np.std(valid_data))
        }
        
    except Exception as e:
        logger.error(f"Summary statistics error: {str(e)}")
        return {
            'count': 0,
            'mean': 0.0,
            'median': 0.0,
            'min': 0.0,
            'max': 0.0,
            'std': 0.0
        }

def generate_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Generate a timestamp string
    
    Args:
        format_str: Datetime format string
    
    Returns:
        Formatted timestamp string
    """
    try:
        return datetime.now().strftime(format_str)
    except Exception as e:
        logger.error(f"Timestamp generation error: {str(e)}")
        return "unknown_time"

def parse_location_string(location_str: str) -> Optional[tuple]:
    """
    Parse a location string to extract coordinates
    
    Args:
        location_str: String containing coordinates (e.g., "37.7749, -122.4194")
    
    Returns:
        Tuple of (latitude, longitude) or None if parsing fails
    """
    try:
        if not isinstance(location_str, str):
            return None
        
        # Remove whitespace and split by comma
        parts = [part.strip() for part in location_str.split(',')]
        
        if len(parts) != 2:
            return None
        
        lat = float(parts[0])
        lon = float(parts[1])
        
        # Basic validation
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Location parsing error: {str(e)}")
        return None

def round_to_significant_figures(value: Union[int, float], sig_figs: int = 3) -> float:
    """
    Round a number to specified significant figures
    
    Args:
        value: Number to round
        sig_figs: Number of significant figures
    
    Returns:
        Rounded number
    """
    try:
        if not isinstance(value, (int, float)) or value == 0:
            return 0.0
        
        if math.isnan(value) or math.isinf(value):
            return 0.0
        
        # Calculate the order of magnitude
        magnitude = math.floor(math.log10(abs(value)))
        
        # Calculate the factor to scale the number
        factor = 10 ** (sig_figs - 1 - magnitude)
        
        # Round and scale back
        return round(value * factor) / factor
        
    except Exception as e:
        logger.error(f"Significant figures rounding error: {str(e)}")
        return 0.0

def create_color_palette(count: int, base_color: str = "blue") -> List[str]:
    """
    Create a color palette for charts
    
    Args:
        count: Number of colors needed
        base_color: Base color name
    
    Returns:
        List of color codes
    """
    try:
        # Predefined color palettes
        color_palettes = {
            'blue': ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a'],
            'green': ['#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5'],
            'orange': ['#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896'],
            'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        }
        
        palette = color_palettes.get(base_color, color_palettes['default'])
        
        # Extend palette if needed
        if count > len(palette):
            # Generate additional colors by varying brightness
            base_colors = palette
            extended_palette = base_colors.copy()
            
            while len(extended_palette) < count:
                for color in base_colors:
                    if len(extended_palette) >= count:
                        break
                    # Simple color variation (this is a basic approach)
                    extended_palette.append(color + "80")  # Add transparency
            
            return extended_palette[:count]
        
        return palette[:count]
        
    except Exception as e:
        logger.error(f"Color palette generation error: {str(e)}")
        return ['#1f77b4'] * count  # Return default blue for all
