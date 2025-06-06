import os
import requests
import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class NASADataProvider:
    """Integration with NASA POWER API for solar irradiance data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("NASA_API_KEY", "WekG8UA5eeLffk8QH4aBc9TytlZAbsmDD3d4Tgm")
        self.base_url = "https://power.larc.nasa.gov/api/temporal"
        self.timeout = 30
        
    def get_solar_data(self, latitude: float, longitude: float) -> Dict:
        """
        Get comprehensive solar data for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dictionary containing solar irradiance and related data
        """
        
        try:
            # Get multiple years of data for better accuracy
            monthly_data = self._get_monthly_data(latitude, longitude)
            daily_data = self._get_daily_data(latitude, longitude)
            
            # Process and combine data
            solar_data = self._process_solar_data(monthly_data, daily_data)
            
            return {
                'annual_irradiance': solar_data['annual_irradiance'],
                'monthly_irradiance': solar_data['monthly_irradiance'],
                'peak_sun_hours': solar_data['peak_sun_hours'],
                'seasonal_variation': solar_data['seasonal_variation'],
                'data_quality': solar_data['data_quality'],
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'data_source': 'NASA POWER API',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"NASA API data retrieval failed: {str(e)}")
            return self._get_fallback_solar_data(latitude, longitude)
    
    def _get_monthly_data(self, latitude: float, longitude: float) -> Dict:
        """Get monthly averaged solar irradiance data"""
        
        try:
            # Request parameters for monthly climatology data
            params = {
                'request': 'execute',
                'identifier': 'SinglePoint',
                'parameters': 'ALLSKY_SFC_SW_DWN',  # All-sky surface shortwave downward irradiance
                'community': 'RE',  # Renewable Energy community
                'longitude': longitude,
                'latitude': latitude,
                'start': '2010',  # Start year
                'end': '2022',    # End year
                'format': 'JSON'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            # Make API request
            url = f"{self.base_url}/monthly/point"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' in data and 'parameter' in data['properties']:
                return data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
            else:
                raise ValueError("Invalid response format from NASA API")
                
        except Exception as e:
            self.logger.error(f"Monthly data retrieval failed: {str(e)}")
            return {}
    
    def _get_daily_data(self, latitude: float, longitude: float) -> Dict:
        """Get recent daily solar irradiance data for validation"""
        
        try:
            # Get data for the last year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            params = {
                'request': 'execute',
                'identifier': 'SinglePoint',
                'parameters': 'ALLSKY_SFC_SW_DWN',
                'community': 'RE',
                'longitude': longitude,
                'latitude': latitude,
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'format': 'JSON'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            url = f"{self.base_url}/daily/point"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' in data and 'parameter' in data['properties']:
                return data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Daily data retrieval failed: {str(e)}")
            return {}
    
    def _process_solar_data(self, monthly_data: Dict, daily_data: Dict) -> Dict:
        """Process raw NASA data into useful metrics"""
        
        try:
            # Process monthly data
            monthly_values = []
            if monthly_data:
                # Extract monthly values (NASA provides data by year and month)
                for year_data in monthly_data.values():
                    if isinstance(year_data, dict):
                        for month, value in year_data.items():
                            if isinstance(value, (int, float)) and value > 0:
                                monthly_values.append(value)
            
            # If we have monthly data, calculate statistics
            if monthly_values:
                # Group by month and average across years
                monthly_averages = []
                months_data = {}
                
                # Reorganize data by month
                for year_data in monthly_data.values():
                    if isinstance(year_data, dict):
                        for month, value in year_data.items():
                            if isinstance(value, (int, float)) and value > 0:
                                if month not in months_data:
                                    months_data[month] = []
                                months_data[month].append(value)
                
                # Calculate monthly averages
                for month in range(1, 13):
                    month_key = str(month)
                    if month_key in months_data and months_data[month_key]:
                        avg_value = np.mean(months_data[month_key])
                        monthly_averages.append(avg_value)
                    else:
                        # Estimate based on available data or use seasonal patterns
                        monthly_averages.append(self._estimate_monthly_irradiance(month, monthly_values))
                
                # Ensure we have 12 months of data
                if len(monthly_averages) < 12:
                    monthly_averages = self._fill_missing_months(monthly_averages, monthly_values)
                
                annual_irradiance = np.sum(monthly_averages) * 30.44  # Average days per month
                
            else:
                # Use fallback estimation
                monthly_averages = self._get_estimated_monthly_irradiance()
                annual_irradiance = np.sum(monthly_averages) * 30.44
            
            # Calculate peak sun hours (irradiance / 1000 W/m²)
            peak_sun_hours = [irr / 1000 * 24 for irr in monthly_averages]
            
            # Calculate seasonal variation
            max_irradiance = max(monthly_averages)
            min_irradiance = min(monthly_averages)
            seasonal_variation = (max_irradiance - min_irradiance) / max_irradiance if max_irradiance > 0 else 0
            
            # Assess data quality
            data_quality = self._assess_data_quality(monthly_data, daily_data)
            
            return {
                'annual_irradiance': annual_irradiance,
                'monthly_irradiance': monthly_averages,
                'peak_sun_hours': peak_sun_hours,
                'seasonal_variation': seasonal_variation,
                'data_quality': data_quality
            }
            
        except Exception as e:
            self.logger.error(f"Solar data processing failed: {str(e)}")
            return self._get_default_processed_data()
    
    def _estimate_monthly_irradiance(self, month: int, available_data: List[float]) -> float:
        """Estimate monthly irradiance based on seasonal patterns"""
        
        if available_data:
            base_irradiance = np.mean(available_data)
        else:
            base_irradiance = 4.5  # kWh/m²/day default
        
        # Seasonal adjustment factors (Northern Hemisphere)
        seasonal_factors = {
            1: 0.6,   # January
            2: 0.7,   # February
            3: 0.85,  # March
            4: 1.0,   # April
            5: 1.15,  # May
            6: 1.2,   # June
            7: 1.2,   # July
            8: 1.1,   # August
            9: 0.95,  # September
            10: 0.8,  # October
            11: 0.65, # November
            12: 0.55  # December
        }
        
        return base_irradiance * seasonal_factors.get(month, 1.0)
    
    def _fill_missing_months(self, partial_data: List[float], reference_data: List[float]) -> List[float]:
        """Fill missing monthly data using interpolation and seasonal patterns"""
        
        # If we have some data, use it as reference
        if partial_data:
            avg_irradiance = np.mean(partial_data)
        elif reference_data:
            avg_irradiance = np.mean(reference_data)
        else:
            avg_irradiance = 4.5
        
        # Generate 12 months of data using seasonal patterns
        monthly_data = []
        for month in range(1, 13):
            monthly_data.append(self._estimate_monthly_irradiance(month, [avg_irradiance]))
        
        return monthly_data
    
    def _get_estimated_monthly_irradiance(self) -> List[float]:
        """Get estimated monthly irradiance for moderate climate"""
        
        # Default monthly irradiance values (kWh/m²/day) for moderate climate
        return [2.5, 3.2, 4.1, 5.2, 6.0, 6.5, 6.3, 5.8, 4.8, 3.7, 2.8, 2.3]
    
    def _assess_data_quality(self, monthly_data: Dict, daily_data: Dict) -> str:
        """Assess the quality of retrieved data"""
        
        quality_score = 0
        
        # Check if we have monthly data
        if monthly_data:
            quality_score += 40
            
            # Check data completeness
            valid_values = 0
            total_values = 0
            
            for year_data in monthly_data.values():
                if isinstance(year_data, dict):
                    for value in year_data.values():
                        total_values += 1
                        if isinstance(value, (int, float)) and value > 0:
                            valid_values += 1
            
            if total_values > 0:
                completeness = valid_values / total_values
                quality_score += int(completeness * 40)
        
        # Check if we have daily data
        if daily_data:
            quality_score += 20
        
        # Return quality rating
        if quality_score >= 80:
            return "excellent"
        elif quality_score >= 60:
            return "good"
        elif quality_score >= 40:
            return "fair"
        else:
            return "estimated"
    
    def _get_default_processed_data(self) -> Dict:
        """Return default processed data when processing fails"""
        
        monthly_irradiance = self._get_estimated_monthly_irradiance()
        
        return {
            'annual_irradiance': sum(monthly_irradiance) * 30.44,
            'monthly_irradiance': monthly_irradiance,
            'peak_sun_hours': [irr / 1000 * 24 for irr in monthly_irradiance],
            'seasonal_variation': 0.6,
            'data_quality': 'estimated'
        }
    
    def _get_fallback_solar_data(self, latitude: float, longitude: float) -> Dict:
        """Provide fallback solar data when API is unavailable"""
        
        # Estimate irradiance based on latitude
        annual_irradiance = self._estimate_irradiance_by_latitude(latitude)
        monthly_irradiance = self._distribute_annual_irradiance(annual_irradiance)
        
        return {
            'annual_irradiance': annual_irradiance,
            'monthly_irradiance': monthly_irradiance,
            'peak_sun_hours': [irr / 1000 * 24 for irr in monthly_irradiance],
            'seasonal_variation': 0.5,
            'data_quality': 'estimated',
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'data_source': 'Estimated (API unavailable)',
            'last_updated': datetime.now().isoformat()
        }
    
    def _estimate_irradiance_by_latitude(self, latitude: float) -> float:
        """Estimate annual irradiance based on latitude"""
        
        # Simplified model based on latitude
        abs_latitude = abs(latitude)
        
        if abs_latitude <= 23.5:  # Tropics
            return 1800  # kWh/m²/year
        elif abs_latitude <= 35:   # Subtropics
            return 1600
        elif abs_latitude <= 45:   # Temperate
            return 1400
        elif abs_latitude <= 60:   # Subarctic/Subantarctic
            return 1100
        else:                      # Arctic/Antarctic
            return 800
    
    def _distribute_annual_irradiance(self, annual_irradiance: float) -> List[float]:
        """Distribute annual irradiance across months with seasonal variation"""
        
        # Seasonal distribution factors (Northern Hemisphere pattern)
        monthly_factors = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 
                          0.11, 0.10, 0.09, 0.08, 0.06, 0.05]
        
        daily_annual = annual_irradiance / 365
        monthly_irradiance = [daily_annual * factor * 365 for factor in monthly_factors]
        
        return monthly_irradiance
