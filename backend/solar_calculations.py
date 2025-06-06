import math
import numpy as np
import logging
from typing import Dict, List, Optional
from config.constants import PANEL_SPECS, SYSTEM_LOSSES, FINANCIAL_PARAMS

class SolarCalculator:
    """Comprehensive solar potential and financial calculations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_potential(self, roof_metrics: Dict, solar_data: Dict, 
                          panel_type: str, electricity_rate: float, 
                          installation_cost_per_watt: float) -> Dict:
        """
        Calculate complete solar potential including energy and financial analysis
        
        Args:
            roof_metrics: Roof analysis results
            solar_data: Solar irradiance data from NASA
            panel_type: Selected panel type
            electricity_rate: Local electricity rate ($/kWh)
            installation_cost_per_watt: Installation cost per watt
        
        Returns:
            Dictionary containing solar potential calculations
        """
        
        try:
            # Get panel specifications
            panel_specs = PANEL_SPECS.get(panel_type, PANEL_SPECS['monocrystalline'])
            
            # Calculate system size
            system_size_kw = self._calculate_system_size(roof_metrics, panel_specs)
            
            # Calculate energy production
            annual_energy_kwh = self._calculate_annual_energy(
                system_size_kw, solar_data, roof_metrics, panel_specs
            )
            
            # Calculate financial metrics
            financial_metrics = self._calculate_financial_metrics(
                system_size_kw, annual_energy_kwh, electricity_rate, 
                installation_cost_per_watt
            )
            
            # Calculate environmental impact
            environmental_impact = self._calculate_environmental_impact(annual_energy_kwh)
            
            return {
                'system_size_kw': system_size_kw,
                'panel_count': int(system_size_kw * 1000 / panel_specs['power_watts']),
                'annual_energy_kwh': annual_energy_kwh,
                'monthly_energy_kwh': annual_energy_kwh / 12,
                'daily_energy_kwh': annual_energy_kwh / 365,
                'capacity_factor': self._calculate_capacity_factor(
                    annual_energy_kwh, system_size_kw
                ),
                **financial_metrics,
                **environmental_impact,
                'system_specifications': {
                    'panel_type': panel_type,
                    'panel_power': panel_specs['power_watts'],
                    'panel_efficiency': panel_specs['efficiency'],
                    'system_losses': SYSTEM_LOSSES
                }
            }
            
        except Exception as e:
            self.logger.error(f"Solar potential calculation failed: {str(e)}")
            return self._get_default_potential()
    
    def _calculate_system_size(self, roof_metrics: Dict, panel_specs: Dict) -> float:
        """Calculate optimal system size in kW"""
        
        try:
            usable_area = roof_metrics['usable_area']  # m²
            panel_area = panel_specs['area_m2']
            panel_power = panel_specs['power_watts']
            
            # Calculate number of panels that can fit
            max_panels = int(usable_area / panel_area)
            
            # Apply spacing factor (typically 70-80% of theoretical maximum)
            spacing_factor = 0.75
            actual_panels = int(max_panels * spacing_factor)
            
            # Calculate system size in kW
            system_size_kw = (actual_panels * panel_power) / 1000
            
            # Cap at reasonable residential system size (50kW max)
            system_size_kw = min(system_size_kw, 50.0)
            
            return max(1.0, system_size_kw)  # Minimum 1kW system
            
        except Exception as e:
            self.logger.error(f"System size calculation failed: {str(e)}")
            return 5.0  # Default 5kW system
    
    def _calculate_annual_energy(self, system_size_kw: float, solar_data: Dict, 
                               roof_metrics: Dict, panel_specs: Dict) -> float:
        """Calculate annual energy production in kWh"""
        
        try:
            # Get average daily solar irradiance (kWh/m²/day)
            if 'annual_irradiance' in solar_data:
                daily_irradiance = solar_data['annual_irradiance'] / 365
            elif 'monthly_irradiance' in solar_data:
                daily_irradiance = np.mean(solar_data['monthly_irradiance'])
            else:
                # Default irradiance for moderate climate
                daily_irradiance = 4.5  # kWh/m²/day
            
            # Apply orientation factor
            orientation_factor = self._get_orientation_factor(roof_metrics['orientation'])
            
            # Apply tilt factor
            tilt_factor = self._get_tilt_factor(roof_metrics['slope'])
            
            # Apply shading factor
            shading_factor = 1.0 - roof_metrics['shading_factor']
            
            # System performance ratio (accounts for losses)
            performance_ratio = (
                SYSTEM_LOSSES['inverter_efficiency'] * 
                SYSTEM_LOSSES['dc_losses'] * 
                SYSTEM_LOSSES['ac_losses'] * 
                SYSTEM_LOSSES['soiling_losses']
            )
            
            # Calculate annual energy production
            annual_energy_kwh = (
                system_size_kw * 
                daily_irradiance * 
                orientation_factor * 
                tilt_factor * 
                shading_factor * 
                performance_ratio * 
                365
            )
            
            return max(0, annual_energy_kwh)
            
        except Exception as e:
            self.logger.error(f"Energy calculation failed: {str(e)}")
            return system_size_kw * 1200  # Default 1200 kWh/kW/year
    
    def _get_orientation_factor(self, orientation: str) -> float:
        """Get energy production factor based on roof orientation"""
        
        orientation_factors = {
            'south': 1.00,
            'southeast': 0.95,
            'southwest': 0.95,
            'east': 0.85,
            'west': 0.85,
            'northeast': 0.75,
            'northwest': 0.75,
            'north': 0.60
        }
        
        return orientation_factors.get(orientation.lower(), 0.85)
    
    def _get_tilt_factor(self, slope_degrees: float) -> float:
        """Get energy production factor based on roof tilt"""
        
        # Optimal tilt is typically close to latitude
        # This is a simplified model - optimal tilt varies by location
        if slope_degrees < 10:
            return 0.90  # Too flat
        elif slope_degrees <= 15:
            return 0.95
        elif slope_degrees <= 25:
            return 1.00  # Optimal range
        elif slope_degrees <= 35:
            return 0.98
        elif slope_degrees <= 45:
            return 0.95
        else:
            return 0.85  # Too steep
    
    def _calculate_capacity_factor(self, annual_energy_kwh: float, system_size_kw: float) -> float:
        """Calculate system capacity factor"""
        
        if system_size_kw == 0:
            return 0.0
        
        # Capacity factor = actual energy / theoretical maximum energy
        theoretical_max = system_size_kw * 8760  # kWh (24 hours * 365 days)
        capacity_factor = annual_energy_kwh / theoretical_max
        
        return min(1.0, max(0.0, capacity_factor))
    
    def _calculate_financial_metrics(self, system_size_kw: float, annual_energy_kwh: float,
                                   electricity_rate: float, installation_cost_per_watt: float) -> Dict:
        """Calculate comprehensive financial metrics"""
        
        try:
            # Calculate costs
            total_cost = system_size_kw * 1000 * installation_cost_per_watt
            
            # Apply federal tax incentive (30% as of 2024)
            federal_incentive = total_cost * FINANCIAL_PARAMS['federal_tax_credit']
            net_cost = total_cost - federal_incentive
            
            # Calculate savings
            annual_savings = annual_energy_kwh * electricity_rate
            
            # Account for electricity rate escalation
            escalation_rate = FINANCIAL_PARAMS['electricity_rate_escalation']
            
            # Calculate NPV and payback
            payback_years = self._calculate_payback_period(
                net_cost, annual_savings, escalation_rate
            )
            
            # Calculate 25-year lifetime value
            lifetime_savings = self._calculate_lifetime_savings(
                annual_savings, escalation_rate, 25
            )
            
            # Calculate ROI
            roi_percent = ((lifetime_savings - net_cost) / net_cost) * 100 if net_cost > 0 else 0
            
            # Monthly savings (first year)
            monthly_savings = annual_savings / 12
            
            return {
                'total_cost': total_cost,
                'federal_incentive': federal_incentive,
                'net_cost': net_cost,
                'annual_savings': annual_savings,
                'monthly_savings': monthly_savings,
                'payback_years': payback_years,
                'lifetime_savings': lifetime_savings,
                'roi_percent': roi_percent,
                'cost_per_watt': installation_cost_per_watt,
                'savings_per_kwh': electricity_rate
            }
            
        except Exception as e:
            self.logger.error(f"Financial calculation failed: {str(e)}")
            return self._get_default_financial_metrics()
    
    def _calculate_payback_period(self, initial_cost: float, annual_savings: float, 
                                escalation_rate: float) -> float:
        """Calculate simple payback period with escalation"""
        
        if annual_savings <= 0:
            return 99.0  # No payback
        
        cumulative_savings = 0
        year = 0
        current_annual_savings = annual_savings
        
        while cumulative_savings < initial_cost and year < 50:
            year += 1
            cumulative_savings += current_annual_savings
            current_annual_savings *= (1 + escalation_rate)
        
        return min(year, 50.0)
    
    def _calculate_lifetime_savings(self, annual_savings: float, escalation_rate: float, 
                                  years: int) -> float:
        """Calculate total savings over system lifetime"""
        
        total_savings = 0
        current_annual_savings = annual_savings
        
        for year in range(years):
            total_savings += current_annual_savings
            current_annual_savings *= (1 + escalation_rate)
        
        return total_savings
    
    def _calculate_environmental_impact(self, annual_energy_kwh: float) -> Dict:
        """Calculate environmental benefits of solar system"""
        
        try:
            # CO2 emissions factor (lbs CO2/kWh) - varies by region
            # Using average US grid emissions factor
            co2_factor_lbs_per_kwh = 0.85
            
            # Annual CO2 offset
            annual_co2_offset_lbs = annual_energy_kwh * co2_factor_lbs_per_kwh
            annual_co2_offset_tons = annual_co2_offset_lbs / 2000
            
            # 25-year lifetime offset
            lifetime_co2_offset_tons = annual_co2_offset_tons * 25
            
            # Equivalent trees planted (1 tree absorbs ~48 lbs CO2/year)
            equivalent_trees = annual_co2_offset_lbs / 48
            
            # Equivalent cars off road (average car emits ~4.6 tons CO2/year)
            equivalent_cars = annual_co2_offset_tons / 4.6
            
            return {
                'annual_co2_offset_lbs': annual_co2_offset_lbs,
                'annual_co2_offset_tons': annual_co2_offset_tons,
                'lifetime_co2_offset_tons': lifetime_co2_offset_tons,
                'equivalent_trees_planted': equivalent_trees,
                'equivalent_cars_removed': equivalent_cars
            }
            
        except Exception as e:
            self.logger.error(f"Environmental impact calculation failed: {str(e)}")
            return {
                'annual_co2_offset_lbs': 0,
                'annual_co2_offset_tons': 0,
                'lifetime_co2_offset_tons': 0,
                'equivalent_trees_planted': 0,
                'equivalent_cars_removed': 0
            }
    
    def _get_default_potential(self) -> Dict:
        """Return default solar potential when calculations fail"""
        
        return {
            'system_size_kw': 5.0,
            'panel_count': 16,
            'annual_energy_kwh': 6000,
            'monthly_energy_kwh': 500,
            'daily_energy_kwh': 16.4,
            'capacity_factor': 0.14,
            **self._get_default_financial_metrics(),
            'annual_co2_offset_lbs': 5100,
            'annual_co2_offset_tons': 2.55,
            'lifetime_co2_offset_tons': 63.75,
            'equivalent_trees_planted': 106,
            'equivalent_cars_removed': 0.55,
            'system_specifications': {
                'panel_type': 'monocrystalline',
                'panel_power': 400,
                'panel_efficiency': 0.20,
                'system_losses': SYSTEM_LOSSES
            }
        }
    
    def _get_default_financial_metrics(self) -> Dict:
        """Return default financial metrics when calculations fail"""
        
        return {
            'total_cost': 15000,
            'federal_incentive': 4500,
            'net_cost': 10500,
            'annual_savings': 1200,
            'monthly_savings': 100,
            'payback_years': 8.8,
            'lifetime_savings': 30000,
            'roi_percent': 185.7,
            'cost_per_watt': 3.0,
            'savings_per_kwh': 0.20
        }
