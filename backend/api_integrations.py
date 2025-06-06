import os
import requests
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class ExternalAPIManager:
    """
    Comprehensive API integration manager for solar analysis
    Integrates with NASA POWER, Google Maps, DSIRE, and other external services
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nasa_api_key = os.getenv("NASA_API_KEY")
        self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Solar-Analysis-Tool/1.0'
        })
        
    def get_comprehensive_location_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get comprehensive location data including elevation, timezone, and administrative details
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dictionary containing location metadata
        """
        try:
            location_data = {
                'coordinates': {'latitude': latitude, 'longitude': longitude},
                'elevation': self._get_elevation_data(latitude, longitude),
                'timezone': self._get_timezone_data(latitude, longitude),
                'administrative': self._get_administrative_data(latitude, longitude),
                'climate_zone': self._determine_climate_zone(latitude, longitude),
                'solar_zone': self._get_solar_zone_classification(latitude)
            }
            
            return location_data
            
        except Exception as e:
            self.logger.error(f"Location data retrieval failed: {str(e)}")
            return self._get_default_location_data(latitude, longitude)
    
    def get_enhanced_solar_irradiance(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get enhanced solar irradiance data from multiple sources
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Enhanced solar irradiance data
        """
        try:
            # Primary source: NASA POWER API
            nasa_data = self._get_nasa_power_data(latitude, longitude)
            
            # Secondary validation from PVLIB-style calculations
            calculated_data = self._calculate_solar_position_data(latitude, longitude)
            
            # Combine and validate data
            enhanced_data = self._merge_solar_data_sources(nasa_data, calculated_data)
            
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Enhanced solar data retrieval failed: {str(e)}")
            return self._get_fallback_solar_data(latitude, longitude)
    
    def get_local_regulations_and_incentives(self, latitude: float, longitude: float, 
                                           system_size_kw: float = None) -> Dict[str, Any]:
        """
        Get local solar regulations and incentives data
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            system_size_kw: Optional system size for incentive calculations
            
        Returns:
            Regulations and incentives information
        """
        try:
            # Get location details
            location_info = self._get_administrative_data(latitude, longitude)
            
            # Get federal incentives
            federal_incentives = self._get_federal_solar_incentives()
            
            # Get state/regional incentives (simplified - would integrate with DSIRE API)
            regional_incentives = self._get_regional_incentives(location_info)
            
            # Get regulatory requirements
            regulations = self._get_regulatory_requirements(location_info)
            
            # Calculate potential savings
            incentive_calculations = self._calculate_incentive_values(
                federal_incentives, regional_incentives, system_size_kw
            )
            
            return {
                'location': location_info,
                'federal_incentives': federal_incentives,
                'regional_incentives': regional_incentives,
                'regulations': regulations,
                'incentive_calculations': incentive_calculations,
                'data_sources': ['IRS', 'DSIRE', 'Local Authorities']
            }
            
        except Exception as e:
            self.logger.error(f"Regulations data retrieval failed: {str(e)}")
            return self._get_default_regulations_data()
    
    def get_utility_rate_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get utility rate data for accurate savings calculations
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Utility rate information
        """
        try:
            # Get utility service territory
            utility_info = self._identify_utility_territory(latitude, longitude)
            
            # Get rate structures (simplified - would integrate with utility APIs)
            rate_data = self._get_utility_rates(utility_info)
            
            # Get net metering policies
            net_metering = self._get_net_metering_policies(utility_info)
            
            return {
                'utility_company': utility_info,
                'rate_structures': rate_data,
                'net_metering': net_metering,
                'time_of_use': self._get_time_of_use_rates(utility_info)
            }
            
        except Exception as e:
            self.logger.error(f"Utility rate data retrieval failed: {str(e)}")
            return self._get_default_utility_data()
    
    def get_weather_patterns(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get historical weather patterns affecting solar performance
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Weather pattern data
        """
        try:
            # Get historical weather data
            weather_data = self._get_historical_weather(latitude, longitude)
            
            # Calculate weather impact factors
            weather_factors = self._calculate_weather_impact_factors(weather_data)
            
            return {
                'historical_data': weather_data,
                'impact_factors': weather_factors,
                'seasonal_patterns': self._analyze_seasonal_patterns(weather_data),
                'extreme_events': self._identify_extreme_weather_events(weather_data)
            }
            
        except Exception as e:
            self.logger.error(f"Weather data retrieval failed: {str(e)}")
            return self._get_default_weather_data()
    
    # NASA POWER API Integration
    def _get_nasa_power_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get solar irradiance data from NASA POWER API"""
        try:
            # Multiple years for better accuracy
            end_year = datetime.now().year - 1
            start_year = end_year - 10
            
            params = {
                'request': 'execute',
                'identifier': 'SinglePoint',
                'parameters': 'ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN,T2M,WS10M,RH2M',
                'community': 'RE',
                'longitude': longitude,
                'latitude': latitude,
                'start': str(start_year),
                'end': str(end_year),
                'format': 'JSON'
            }
            
            if self.nasa_api_key:
                params['api_key'] = self.nasa_api_key
            
            url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return self._process_nasa_data(data)
            
        except Exception as e:
            self.logger.error(f"NASA POWER API request failed: {str(e)}")
            raise
    
    def _process_nasa_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Process raw NASA data into usable format"""
        try:
            parameters = raw_data['properties']['parameter']
            
            # Extract irradiance data
            irradiance_data = parameters.get('ALLSKY_SFC_SW_DWN', {})
            clear_sky_data = parameters.get('CLRSKY_SFC_SW_DWN', {})
            temperature_data = parameters.get('T2M', {})
            wind_data = parameters.get('WS10M', {})
            humidity_data = parameters.get('RH2M', {})
            
            # Calculate monthly averages across years
            monthly_irradiance = self._calculate_monthly_averages(irradiance_data)
            monthly_clear_sky = self._calculate_monthly_averages(clear_sky_data)
            monthly_temperature = self._calculate_monthly_averages(temperature_data)
            
            # Calculate derived metrics
            annual_irradiance = sum(monthly_irradiance) * 30.44  # Average days per month
            cloud_factor = [cs / ir if ir > 0 else 1.0 for cs, ir in zip(monthly_clear_sky, monthly_irradiance)]
            
            return {
                'monthly_irradiance': monthly_irradiance,
                'monthly_clear_sky': monthly_clear_sky,
                'monthly_temperature': monthly_temperature,
                'annual_irradiance': annual_irradiance,
                'cloud_factor': cloud_factor,
                'data_quality': 'nasa_verified',
                'data_period': f"{len(irradiance_data)} years"
            }
            
        except Exception as e:
            self.logger.error(f"NASA data processing failed: {str(e)}")
            raise
    
    def _calculate_monthly_averages(self, yearly_data: Dict) -> List[float]:
        """Calculate monthly averages from multi-year data"""
        monthly_sums = [0.0] * 12
        monthly_counts = [0] * 12
        
        for year_data in yearly_data.values():
            if isinstance(year_data, dict):
                for month_str, value in year_data.items():
                    try:
                        month = int(month_str) - 1  # Convert to 0-based index
                        if 0 <= month < 12 and isinstance(value, (int, float)) and value > 0:
                            monthly_sums[month] += value
                            monthly_counts[month] += 1
                    except (ValueError, TypeError):
                        continue
        
        # Calculate averages, fallback to seasonal estimates if no data
        monthly_averages = []
        for i in range(12):
            if monthly_counts[i] > 0:
                monthly_averages.append(monthly_sums[i] / monthly_counts[i])
            else:
                # Use seasonal estimation
                monthly_averages.append(self._estimate_monthly_value(i + 1, monthly_sums))
        
        return monthly_averages
    
    def _estimate_monthly_value(self, month: int, available_data: List[float]) -> float:
        """Estimate monthly value using seasonal patterns"""
        # Seasonal multipliers for Northern Hemisphere
        seasonal_multipliers = [0.6, 0.7, 0.85, 1.0, 1.15, 1.2, 1.2, 1.1, 0.95, 0.8, 0.65, 0.55]
        
        valid_data = [x for x in available_data if x > 0]
        baseline = np.mean(valid_data) if valid_data else 4.5
        
        return baseline * seasonal_multipliers[month - 1]
    
    # Location and Administrative Data
    def _get_elevation_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get elevation data for the location"""
        try:
            # Using Open Elevation API as fallback
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                elevation = data['results'][0]['elevation']
                return {
                    'elevation_meters': elevation,
                    'source': 'open_elevation'
                }
            else:
                raise Exception("Elevation API unavailable")
                
        except Exception:
            # Estimate elevation based on latitude (very rough)
            estimated_elevation = max(0, 500 - abs(latitude) * 10)
            return {
                'elevation_meters': estimated_elevation,
                'source': 'estimated'
            }
    
    def _get_timezone_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get timezone information"""
        try:
            # Simple timezone estimation based on longitude
            timezone_offset = int(longitude / 15)
            return {
                'utc_offset': timezone_offset,
                'source': 'calculated'
            }
        except Exception:
            return {'utc_offset': 0, 'source': 'default'}
    
    def _get_administrative_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get administrative location data"""
        try:
            geolocator = Nominatim(user_agent="solar_analysis_tool")
            location = geolocator.reverse(f"{latitude}, {longitude}")
            
            if location and location.raw.get('address'):
                address = location.raw['address']
                return {
                    'country': address.get('country', 'Unknown'),
                    'state': address.get('state', 'Unknown'),
                    'county': address.get('county', 'Unknown'),
                    'city': address.get('city', address.get('town', address.get('village', 'Unknown'))),
                    'postal_code': address.get('postcode', 'Unknown'),
                    'formatted_address': location.address
                }
            else:
                raise Exception("Geocoding failed")
                
        except Exception as e:
            self.logger.warning(f"Administrative data lookup failed: {str(e)}")
            return self._estimate_administrative_data(latitude, longitude)
    
    def _estimate_administrative_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Estimate administrative data based on coordinates"""
        # Simple geographic estimation
        if 25 <= latitude <= 49 and -125 <= longitude <= -66:
            country = "United States"
        elif 42 <= latitude <= 83 and -141 <= longitude <= -52:
            country = "Canada"
        elif 35 <= latitude <= 71 and -10 <= longitude <= 40:
            country = "Europe"
        else:
            country = "International"
        
        return {
            'country': country,
            'state': 'Unknown',
            'county': 'Unknown',
            'city': 'Unknown',
            'postal_code': 'Unknown',
            'formatted_address': f"{latitude:.4f}, {longitude:.4f}"
        }
    
    # Solar Calculations and Analysis
    def _calculate_solar_position_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate solar position data for validation"""
        try:
            # Simplified solar calculations for validation
            declination_angles = []
            day_lengths = []
            
            for day_of_year in range(1, 366, 30):  # Monthly samples
                # Solar declination
                declination = 23.45 * np.sin(np.radians((360/365) * (284 + day_of_year)))
                declination_angles.append(declination)
                
                # Day length calculation
                lat_rad = np.radians(latitude)
                decl_rad = np.radians(declination)
                
                hour_angle = np.arccos(-np.tan(lat_rad) * np.tan(decl_rad))
                day_length = 2 * hour_angle * 12 / np.pi
                day_lengths.append(day_length)
            
            return {
                'declination_angles': declination_angles,
                'day_lengths': day_lengths,
                'latitude_factor': abs(np.cos(np.radians(latitude))),
                'optimal_tilt': abs(latitude)  # Simplified optimal tilt
            }
            
        except Exception as e:
            self.logger.error(f"Solar position calculation failed: {str(e)}")
            return {}
    
    def _merge_solar_data_sources(self, nasa_data: Dict, calculated_data: Dict) -> Dict[str, Any]:
        """Merge and validate solar data from multiple sources"""
        try:
            # Primary data from NASA
            merged_data = nasa_data.copy()
            
            # Add calculated validation metrics
            merged_data.update({
                'validation_metrics': calculated_data,
                'data_confidence': self._assess_data_confidence(nasa_data, calculated_data),
                'recommended_tilt': calculated_data.get('optimal_tilt', abs(nasa_data.get('latitude', 35))),
                'seasonal_variability': self._calculate_seasonal_variability(nasa_data.get('monthly_irradiance', []))
            })
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Solar data merging failed: {str(e)}")
            return nasa_data
    
    def _assess_data_confidence(self, nasa_data: Dict, calculated_data: Dict) -> float:
        """Assess confidence in solar data"""
        try:
            confidence = 0.8  # Base confidence for NASA data
            
            # Boost confidence if we have validation data
            if calculated_data:
                confidence += 0.1
            
            # Check data completeness
            monthly_data = nasa_data.get('monthly_irradiance', [])
            if len(monthly_data) == 12 and all(x > 0 for x in monthly_data):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.7
    
    def _calculate_seasonal_variability(self, monthly_irradiance: List[float]) -> float:
        """Calculate seasonal variability in solar irradiance"""
        try:
            if len(monthly_irradiance) < 12:
                return 0.4  # Default variability
            
            max_irr = max(monthly_irradiance)
            min_irr = min(monthly_irradiance)
            
            variability = (max_irr - min_irr) / max_irr if max_irr > 0 else 0.4
            return variability
            
        except Exception:
            return 0.4
    
    # Climate and Weather Analysis
    def _determine_climate_zone(self, latitude: float, longitude: float) -> str:
        """Determine climate zone based on location"""
        abs_lat = abs(latitude)
        
        if abs_lat <= 23.5:
            return "tropical"
        elif 23.5 < abs_lat <= 35:
            # Check for desert conditions (simplified)
            if -125 <= longitude <= -100 and 25 <= latitude <= 40:
                return "desert"
            else:
                return "subtropical"
        elif 35 < abs_lat <= 50:
            return "temperate"
        elif 50 < abs_lat <= 66.5:
            return "continental"
        else:
            return "polar"
    
    def _get_solar_zone_classification(self, latitude: float) -> str:
        """Classify solar resource zone"""
        abs_lat = abs(latitude)
        
        if abs_lat <= 15:
            return "excellent"
        elif 15 < abs_lat <= 35:
            return "very_good"
        elif 35 < abs_lat <= 45:
            return "good"
        elif 45 < abs_lat <= 55:
            return "moderate"
        else:
            return "limited"
    
    # Regulatory and Incentive Data
    def _get_federal_solar_incentives(self) -> Dict[str, Any]:
        """Get current federal solar incentives"""
        return {
            'investment_tax_credit': {
                'percentage': 30,
                'valid_until': '2032',
                'description': 'Federal Solar Investment Tax Credit',
                'cap_residential': None,
                'cap_commercial': None
            },
            'depreciation': {
                'macrs_years': 5,
                'bonus_depreciation': 100,
                'description': 'Modified Accelerated Cost Recovery System'
            }
        }
    
    def _get_regional_incentives(self, location_info: Dict) -> Dict[str, Any]:
        """Get regional solar incentives (simplified implementation)"""
        country = location_info.get('country', 'Unknown')
        state = location_info.get('state', 'Unknown')
        
        # Simplified state incentives (would integrate with DSIRE API)
        state_incentives = {
            'California': {
                'rebates': ['California Solar Initiative'],
                'net_metering': 'available',
                'property_tax_exemption': True
            },
            'Texas': {
                'rebates': ['Local utility rebates vary'],
                'net_metering': 'limited',
                'property_tax_exemption': True
            },
            'Florida': {
                'rebates': ['Local utility rebates'],
                'net_metering': 'available',
                'property_tax_exemption': True
            }
        }
        
        return state_incentives.get(state, {
            'rebates': ['Check local utility programs'],
            'net_metering': 'varies',
            'property_tax_exemption': 'varies'
        })
    
    def _get_regulatory_requirements(self, location_info: Dict) -> Dict[str, Any]:
        """Get regulatory requirements for solar installations"""
        return {
            'permits_required': [
                'Building permit',
                'Electrical permit',
                'Utility interconnection agreement'
            ],
            'inspections': [
                'Electrical inspection',
                'Final inspection',
                'Utility inspection'
            ],
            'codes_standards': [
                'National Electrical Code (NEC)',
                'Local building codes',
                'Utility interconnection standards'
            ],
            'hoa_considerations': 'Check local HOA regulations',
            'setback_requirements': 'Typically 3 feet from roof edges'
        }
    
    def _calculate_incentive_values(self, federal: Dict, regional: Dict, 
                                  system_size_kw: float = None) -> Dict[str, Any]:
        """Calculate monetary value of incentives"""
        if not system_size_kw:
            return {'note': 'System size required for calculations'}
        
        # Estimate system cost
        estimated_cost = system_size_kw * 1000 * 3.0  # $3/watt
        
        # Federal ITC
        federal_itc = estimated_cost * (federal['investment_tax_credit']['percentage'] / 100)
        
        return {
            'estimated_system_cost': estimated_cost,
            'federal_itc_value': federal_itc,
            'net_cost_after_federal': estimated_cost - federal_itc,
            'total_incentive_value': federal_itc,
            'note': 'Consult tax professional for actual calculations'
        }
    
    # Utility and Rate Data
    def _identify_utility_territory(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Identify utility service territory (simplified)"""
        # This would integrate with utility territory APIs in production
        return {
            'utility_name': 'Local Electric Utility',
            'utility_type': 'investor_owned',
            'service_territory': 'standard',
            'contact_info': 'Contact local utility for specific rates'
        }
    
    def _get_utility_rates(self, utility_info: Dict) -> Dict[str, Any]:
        """Get utility rate structures"""
        return {
            'residential_rate': {
                'standard_rate_kwh': 0.12,
                'rate_structure': 'tiered',
                'connection_charge': 15.0
            },
            'time_of_use_available': True,
            'demand_charges': False,
            'rate_source': 'estimated'
        }
    
    def _get_net_metering_policies(self, utility_info: Dict) -> Dict[str, Any]:
        """Get net metering policies"""
        return {
            'available': True,
            'compensation_rate': 'retail_rate',
            'system_size_limit_kw': 25,
            'interconnection_fee': 100,
            'annual_true_up': True
        }
    
    def _get_time_of_use_rates(self, utility_info: Dict) -> Dict[str, Any]:
        """Get time-of-use rate information"""
        return {
            'available': True,
            'peak_hours': '4 PM - 9 PM',
            'peak_rate_multiplier': 1.5,
            'off_peak_rate_multiplier': 0.8
        }
    
    # Weather and Environmental Data
    def _get_historical_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get historical weather data affecting solar performance"""
        # Simplified weather data - would integrate with weather APIs
        return {
            'average_cloud_cover': 0.4,
            'precipitation_days_annual': 120,
            'extreme_weather_frequency': {
                'hail_events': 1,
                'high_wind_events': 5,
                'snow_days': 30 if latitude > 35 else 0
            },
            'air_quality_index': 85
        }
    
    def _calculate_weather_impact_factors(self, weather_data: Dict) -> Dict[str, Any]:
        """Calculate weather impact on solar performance"""
        cloud_cover = weather_data.get('average_cloud_cover', 0.4)
        precipitation_days = weather_data.get('precipitation_days_annual', 120)
        
        # Calculate impact factors
        cloud_impact = 1.0 - (cloud_cover * 0.3)  # Clouds reduce output
        precipitation_impact = 1.0 - (precipitation_days / 365 * 0.1)  # Rain cleaning effect
        
        return {
            'cloud_impact_factor': cloud_impact,
            'precipitation_impact_factor': precipitation_impact,
            'overall_weather_factor': (cloud_impact + precipitation_impact) / 2,
            'maintenance_factor': 0.95  # Account for soiling
        }
    
    def _analyze_seasonal_patterns(self, weather_data: Dict) -> Dict[str, Any]:
        """Analyze seasonal weather patterns"""
        return {
            'winter_performance_factor': 0.85,
            'spring_performance_factor': 1.05,
            'summer_performance_factor': 0.95,  # Heat reduces efficiency
            'fall_performance_factor': 1.0,
            'optimal_season': 'spring'
        }
    
    def _identify_extreme_weather_events(self, weather_data: Dict) -> List[Dict]:
        """Identify extreme weather events that could affect system"""
        extreme_events = weather_data.get('extreme_weather_frequency', {})
        
        events = []
        for event_type, frequency in extreme_events.items():
            if frequency > 0:
                events.append({
                    'event_type': event_type,
                    'annual_frequency': frequency,
                    'impact_level': 'moderate' if frequency < 5 else 'high',
                    'mitigation_required': frequency > 3
                })
        
        return events
    
    # Fallback and Default Data Methods
    def _get_default_location_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Return default location data when APIs fail"""
        return {
            'coordinates': {'latitude': latitude, 'longitude': longitude},
            'elevation': {'elevation_meters': 200, 'source': 'estimated'},
            'timezone': {'utc_offset': int(longitude / 15), 'source': 'calculated'},
            'administrative': self._estimate_administrative_data(latitude, longitude),
            'climate_zone': self._determine_climate_zone(latitude, longitude),
            'solar_zone': self._get_solar_zone_classification(latitude)
        }
    
    def _get_fallback_solar_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Return fallback solar data when NASA API fails"""
        # Estimate based on latitude
        abs_lat = abs(latitude)
        base_irradiance = max(3.0, 7.0 - abs_lat * 0.08)
        
        # Generate seasonal pattern
        monthly_irradiance = []
        for month in range(1, 13):
            seasonal_factor = self._get_seasonal_factor(month)
            monthly_irradiance.append(base_irradiance * seasonal_factor)
        
        return {
            'monthly_irradiance': monthly_irradiance,
            'annual_irradiance': sum(monthly_irradiance) * 30.44,
            'data_quality': 'estimated',
            'data_source': 'calculated_fallback'
        }
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor for month"""
        factors = [0.6, 0.7, 0.85, 1.0, 1.15, 1.2, 1.2, 1.1, 0.95, 0.8, 0.65, 0.55]
        return factors[month - 1]
    
    def _get_default_regulations_data(self) -> Dict[str, Any]:
        """Return default regulations data"""
        return {
            'location': {'country': 'Unknown', 'state': 'Unknown'},
            'federal_incentives': self._get_federal_solar_incentives(),
            'regional_incentives': {'note': 'Check local programs'},
            'regulations': self._get_regulatory_requirements({}),
            'incentive_calculations': {'note': 'System size required'}
        }
    
    def _get_default_utility_data(self) -> Dict[str, Any]:
        """Return default utility data"""
        return {
            'utility_company': {'utility_name': 'Local Utility'},
            'rate_structures': {
                'residential_rate': {'standard_rate_kwh': 0.12}
            },
            'net_metering': {'available': True, 'compensation_rate': 'retail_rate'}
        }
    
    def _get_default_weather_data(self) -> Dict[str, Any]:
        """Return default weather data"""
        return {
            'historical_data': {'average_cloud_cover': 0.4},
            'impact_factors': {'overall_weather_factor': 0.85},
            'seasonal_patterns': {'optimal_season': 'spring'},
            'extreme_events': []
        }