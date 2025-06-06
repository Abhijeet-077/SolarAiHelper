import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class LLMGenerator:
    """Integration with Google LLM API for generating structured solar recommendations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_api()
        
    def _setup_api(self):
        """Initialize Google LLM API"""
        try:
            api_key = os.getenv("GOOGLE_LLM_API_KEY")
            if not api_key:
                raise ValueError("Google LLM API key not found")
            
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 2048,
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            self.logger.info("Google LLM API initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google LLM API: {str(e)}")
            self.model = None
    
    def generate_recommendations(self, roof_metrics: Dict, solar_potential: Dict, 
                               latitude: float, longitude: float) -> Dict[str, str]:
        """
        Generate comprehensive solar installation recommendations
        
        Args:
            roof_metrics: Roof analysis results
            solar_potential: Solar potential calculations
            latitude: Location latitude
            longitude: Location longitude
        
        Returns:
            Dictionary containing structured recommendations
        """
        
        if not self.model:
            return self._get_fallback_recommendations()
        
        try:
            # Prepare context data
            context = self._prepare_context(roof_metrics, solar_potential, latitude, longitude)
            
            # Generate installation plan
            installation_plan = self._generate_installation_plan(context)
            
            # Generate optimization tips
            optimization_tips = self._generate_optimization_tips(context)
            
            # Generate compliance information
            compliance_info = self._generate_compliance_info(context, latitude, longitude)
            
            # Generate maintenance plan
            maintenance_plan = self._generate_maintenance_plan(context)
            
            return {
                'installation_plan': installation_plan,
                'optimization_tips': optimization_tips,
                'compliance_info': compliance_info,
                'maintenance_plan': maintenance_plan,
                'generation_successful': True
            }
            
        except Exception as e:
            self.logger.error(f"LLM recommendation generation failed: {str(e)}")
            return self._get_fallback_recommendations()
    
    def _prepare_context(self, roof_metrics: Dict, solar_potential: Dict, 
                        latitude: float, longitude: float) -> str:
        """Prepare context string for LLM prompts"""
        
        context = f"""
        ROOF ANALYSIS DATA:
        - Total roof area: {roof_metrics['total_area']:.1f} m²
        - Usable area: {roof_metrics['usable_area']:.1f} m²
        - Orientation: {roof_metrics['orientation']}
        - Slope: {roof_metrics['slope']:.1f}°
        - Shading factor: {roof_metrics['shading_factor']:.2f}
        - Obstructions: {roof_metrics['obstruction_count']} detected
        
        SOLAR POTENTIAL DATA:
        - System size: {solar_potential['system_size_kw']:.1f} kW
        - Annual energy: {solar_potential['annual_energy_kwh']:.0f} kWh
        - Annual savings: ${solar_potential['annual_savings']:.0f}
        - Total cost: ${solar_potential['total_cost']:.0f}
        - Payback period: {solar_potential['payback_years']:.1f} years
        - ROI: {solar_potential['roi_percent']:.1f}%
        
        LOCATION:
        - Latitude: {latitude:.4f}
        - Longitude: {longitude:.4f}
        """
        
        return context
    
    def _generate_installation_plan(self, context: str) -> str:
        """Generate detailed installation plan"""
        
        prompt = f"""
        Based on the following rooftop solar analysis data, provide a detailed installation plan:

        {context}

        Please provide:
        1. Recommended panel configuration and layout
        2. Optimal panel type and specifications
        3. Inverter recommendations
        4. Mounting system suggestions
        5. Electrical considerations
        6. Installation timeline

        Format the response as clear, actionable recommendations for a solar installer.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Installation plan generation failed: {str(e)}")
            return self._get_default_installation_plan()
    
    def _generate_optimization_tips(self, context: str) -> str:
        """Generate system optimization recommendations"""
        
        prompt = f"""
        Based on the following solar system data, provide specific optimization recommendations:

        {context}

        Please provide optimization tips for:
        1. Maximizing energy production
        2. Improving system efficiency
        3. Optimal panel placement considering obstructions
        4. Seasonal adjustments
        5. Energy storage considerations
        6. Grid connection optimization

        Focus on practical, implementable suggestions that will improve system performance.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Optimization tips generation failed: {str(e)}")
            return self._get_default_optimization_tips()
    
    def _generate_compliance_info(self, context: str, latitude: float, longitude: float) -> str:
        """Generate regulatory compliance information"""
        
        # Determine general region for regulatory context
        region = self._determine_region(latitude, longitude)
        
        prompt = f"""
        Based on the following solar installation data and location, provide regulatory compliance information:

        {context}
        
        Region: {region}

        Please provide information about:
        1. Required permits and approvals
        2. Building code requirements
        3. Electrical code compliance
        4. Utility interconnection requirements
        5. Safety standards and inspections
        6. Net metering regulations
        7. Available incentives and rebates

        Focus on general regulatory requirements and suggest consulting local authorities for specific details.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Compliance info generation failed: {str(e)}")
            return self._get_default_compliance_info(region)
    
    def _generate_maintenance_plan(self, context: str) -> str:
        """Generate maintenance recommendations"""
        
        prompt = f"""
        Based on the following solar system specifications, create a comprehensive maintenance plan:

        {context}

        Please provide:
        1. Regular maintenance schedule (monthly, quarterly, annual)
        2. Cleaning recommendations
        3. Performance monitoring guidelines
        4. Common issues to watch for
        5. Professional inspection recommendations
        6. Warranty considerations
        7. System longevity tips

        Format as a practical maintenance guide for the system owner.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Maintenance plan generation failed: {str(e)}")
            return self._get_default_maintenance_plan()
    
    def _determine_region(self, latitude: float, longitude: float) -> str:
        """Determine general region for regulatory context"""
        
        # Simple region determination based on coordinates
        if 25 <= latitude <= 49 and -125 <= longitude <= -66:
            return "United States"
        elif 42 <= latitude <= 83 and -141 <= longitude <= -52:
            return "Canada"
        elif 35 <= latitude <= 71 and -10 <= longitude <= 40:
            return "Europe"
        elif -44 <= latitude <= -10 and 113 <= longitude <= 154:
            return "Australia"
        else:
            return "International"
    
    def _get_fallback_recommendations(self) -> Dict[str, str]:
        """Provide fallback recommendations when LLM is unavailable"""
        
        return {
            'installation_plan': self._get_default_installation_plan(),
            'optimization_tips': self._get_default_optimization_tips(),
            'compliance_info': self._get_default_compliance_info("General"),
            'maintenance_plan': self._get_default_maintenance_plan(),
            'generation_successful': False
        }
    
    def _get_default_installation_plan(self) -> str:
        """Default installation plan when LLM is unavailable"""
        
        return """
        ## Recommended Installation Plan

        ### Panel Configuration
        - Install high-efficiency monocrystalline panels (300-400W each)
        - Arrange panels in optimal orientation facing south when possible
        - Maintain proper spacing for maintenance access
        - Consider micro-inverters for panel-level optimization

        ### System Components
        - **Inverter**: String inverter or power optimizers recommended
        - **Mounting**: Rail-based mounting system appropriate for roof type
        - **Monitoring**: Include production monitoring system
        - **Safety**: Install rapid shutdown devices as required

        ### Installation Process
        1. Obtain necessary permits and approvals
        2. Schedule utility interconnection application
        3. Install mounting system and electrical components
        4. Mount solar panels and complete wiring
        5. System commissioning and testing
        6. Final inspection and utility connection

        *Note: This is a general plan. Consult with certified solar installers for detailed specifications.*
        """
    
    def _get_default_optimization_tips(self) -> str:
        """Default optimization tips when LLM is unavailable"""
        
        return """
        ## System Optimization Recommendations

        ### Energy Production Maximization
        - Ensure panels face optimal direction (south in Northern Hemisphere)
        - Minimize shading from trees, buildings, or other obstructions
        - Clean panels regularly to maintain efficiency
        - Consider seasonal tilt adjustments where applicable

        ### Efficiency Improvements
        - Install power optimizers or micro-inverters for panel-level MPPT
        - Use high-efficiency panels to maximize production per square foot
        - Ensure proper ventilation around panels to prevent overheating
        - Monitor system performance regularly

        ### System Design
        - Size system appropriately for energy usage patterns
        - Consider battery storage for energy independence
        - Plan for future energy needs and potential expansion
        - Optimize string sizing for inverter specifications

        ### Performance Monitoring
        - Install comprehensive monitoring system
        - Set up alerts for performance issues
        - Track energy production vs. consumption
        - Schedule regular professional inspections
        """
    
    def _get_default_compliance_info(self, region: str) -> str:
        """Default compliance information when LLM is unavailable"""
        
        return f"""
        ## Regulatory Compliance Guidelines ({region})

        ### Required Permits
        - Building permit for structural modifications
        - Electrical permit for system installation
        - Utility interconnection agreement
        - HOA approval if applicable

        ### Code Requirements
        - National Electrical Code (NEC) compliance
        - Local building code requirements
        - Fire safety setbacks and access pathways
        - Structural load calculations

        ### Safety Standards
        - UL-listed equipment requirements
        - Rapid shutdown compliance
        - Grounding and bonding requirements
        - Arc fault circuit interrupter (AFCI) protection

        ### Utility Requirements
        - Net metering application
        - Interconnection standards compliance
        - Production metering installation
        - Utility notification procedures

        ### Inspections
        - Electrical inspection by local authority
        - Structural inspection if required
        - Utility inspection before interconnection
        - Final system commissioning

        *Note: Requirements vary by location. Consult local authorities and certified installers for specific regulations.*
        """
    
    def _get_default_maintenance_plan(self) -> str:
        """Default maintenance plan when LLM is unavailable"""
        
        return """
        ## Solar System Maintenance Plan

        ### Monthly Tasks
        - Visual inspection of panels for damage or debris
        - Check inverter status indicators
        - Review production monitoring data
        - Clear any visible obstructions

        ### Quarterly Tasks
        - Clean panels if needed (rain usually sufficient)
        - Inspect mounting hardware for tightness
        - Check electrical connections for corrosion
        - Trim vegetation that may cause shading

        ### Annual Tasks
        - Professional system inspection
        - Detailed performance analysis
        - Inverter maintenance as recommended
        - Documentation review and updates

        ### Performance Monitoring
        - Track daily/monthly energy production
        - Compare actual vs. expected performance
        - Monitor for gradual performance degradation
        - Set up alerts for system issues

        ### Professional Services
        - Annual professional inspection recommended
        - Electrical testing every 3-5 years
        - Inverter replacement after 10-15 years
        - Panel warranty claims if performance degrades

        ### System Longevity
        - Panels typically last 25+ years
        - Inverters may need replacement after 10-15 years
        - Monitor system performance regularly
        - Address issues promptly to prevent damage

        *Maintain all warranty documentation and service records.*
        """
