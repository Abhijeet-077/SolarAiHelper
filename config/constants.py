"""
Configuration constants for the solar analysis application
"""

# Solar panel specifications
PANEL_SPECS = {
    'monocrystalline': {
        'power_watts': 400,
        'efficiency': 0.20,
        'area_m2': 2.0,
        'cost_premium': 1.0,
        'lifespan_years': 25,
        'degradation_rate': 0.005  # 0.5% per year
    },
    'polycrystalline': {
        'power_watts': 350,
        'efficiency': 0.17,
        'area_m2': 2.0,
        'cost_premium': 0.85,
        'lifespan_years': 25,
        'degradation_rate': 0.006  # 0.6% per year
    },
    'thin_film': {
        'power_watts': 250,
        'efficiency': 0.12,
        'area_m2': 2.0,
        'cost_premium': 0.70,
        'lifespan_years': 20,
        'degradation_rate': 0.008  # 0.8% per year
    },
    'bifacial': {
        'power_watts': 450,
        'efficiency': 0.22,
        'area_m2': 2.0,
        'cost_premium': 1.20,
        'lifespan_years': 30,
        'degradation_rate': 0.004  # 0.4% per year
    }
}

# System losses (typical values for solar installations)
SYSTEM_LOSSES = {
    'inverter_efficiency': 0.96,      # 96% inverter efficiency
    'dc_losses': 0.98,                # 2% DC system losses (wiring, connections)
    'ac_losses': 0.99,                # 1% AC system losses
    'soiling_losses': 0.95,           # 5% losses due to dust and soiling
    'temperature_coefficient': 0.004, # 0.4% power loss per °C above 25°C
    'mismatch_losses': 0.98,          # 2% losses due to panel mismatch
    'snow_losses': 0.99               # 1% annual losses due to snow (varies by location)
}

# Financial parameters
FINANCIAL_PARAMS = {
    'federal_tax_credit': 0.30,           # 30% federal solar investment tax credit
    'electricity_rate_escalation': 0.03,  # 3% annual electricity rate increase
    'discount_rate': 0.04,                # 4% discount rate for NPV calculations
    'system_lifespan_years': 25,          # Standard system analysis period
    'inverter_replacement_year': 15,      # Typical inverter replacement timeline
    'inverter_replacement_cost': 0.20     # 20% of original system cost
}

# Climate zones and typical irradiance values (kWh/m²/day)
CLIMATE_ZONES = {
    'tropical': {
        'annual_irradiance': 5.5,
        'seasonal_variation': 0.2,
        'description': 'High irradiance year-round'
    },
    'desert': {
        'annual_irradiance': 6.5,
        'seasonal_variation': 0.3,
        'description': 'Very high irradiance, low precipitation'
    },
    'temperate': {
        'annual_irradiance': 4.5,
        'seasonal_variation': 0.5,
        'description': 'Moderate irradiance with seasonal variation'
    },
    'continental': {
        'annual_irradiance': 4.0,
        'seasonal_variation': 0.6,
        'description': 'Lower irradiance with high seasonal variation'
    },
    'coastal': {
        'annual_irradiance': 4.8,
        'seasonal_variation': 0.4,
        'description': 'Moderate irradiance with marine influence'
    }
}

# Image processing parameters
IMAGE_PROCESSING = {
    'max_file_size_mb': 10,               # Maximum upload file size
    'supported_formats': ['jpg', 'jpeg', 'png'],
    'min_resolution': (500, 500),         # Minimum image resolution
    'max_resolution': (4000, 4000),       # Maximum image resolution
    'default_scale_meters_per_pixel': 0.1, # Default scale assumption
    'confidence_threshold': 0.3           # Minimum confidence for analysis
}

# UI configuration
UI_CONFIG = {
    'max_system_size_kw': 50,             # Maximum residential system size
    'min_system_size_kw': 1,              # Minimum system size
    'default_electricity_rate': 0.12,     # Default electricity rate ($/kWh)
    'default_installation_cost': 3.0,     # Default installation cost ($/W)
    'currency_format': 'USD',
    'number_precision': 1
}

# Environmental factors
ENVIRONMENTAL_FACTORS = {
    'co2_emissions_factor_lbs_per_kwh': 0.85,    # Average US grid emissions
    'co2_per_gallon_gasoline_lbs': 19.6,         # CO2 emissions per gallon of gasoline
    'co2_absorption_per_tree_lbs_per_year': 48,  # CO2 absorption per mature tree
    'average_car_emissions_tons_per_year': 4.6,  # Average passenger vehicle emissions
    'coal_emissions_lbs_per_kwh': 2.23           # CO2 emissions per kWh from coal
}

# API configuration
API_CONFIG = {
    'nasa_power_base_url': 'https://power.larc.nasa.gov/api/temporal',
    'google_llm_model': 'gemini-1.5-flash',
    'request_timeout_seconds': 30,
    'max_retries': 3,
    'retry_delay_seconds': 2
}

# Validation rules
VALIDATION_RULES = {
    'latitude_range': (-90, 90),
    'longitude_range': (-180, 180),
    'electricity_rate_range': (0.01, 1.0),      # $/kWh
    'installation_cost_range': (1.0, 10.0),     # $/W
    'roof_area_range': (10, 10000),             # m²
    'system_size_range': (1, 100)              # kW
}

# Error messages
ERROR_MESSAGES = {
    'image_upload': {
        'invalid_format': 'Please upload a valid image file (JPG, JPEG, or PNG).',
        'file_too_large': f'File size must be less than {IMAGE_PROCESSING["max_file_size_mb"]} MB.',
        'resolution_too_low': 'Image resolution is too low for accurate analysis.',
        'resolution_too_high': 'Please upload a smaller image file.',
        'corrupted_file': 'The uploaded file appears to be corrupted.'
    },
    'analysis': {
        'processing_failed': 'Image analysis failed. Please try with a different image.',
        'low_confidence': 'Analysis confidence is low. Results may be inaccurate.',
        'no_roof_detected': 'Unable to detect roof area in the image.',
        'insufficient_area': 'Detected roof area is too small for solar installation.'
    },
    'api': {
        'nasa_unavailable': 'Solar data service is temporarily unavailable.',
        'llm_unavailable': 'AI recommendation service is temporarily unavailable.',
        'rate_limit': 'Service rate limit exceeded. Please try again later.',
        'invalid_location': 'Invalid location coordinates provided.'
    },
    'calculation': {
        'invalid_parameters': 'Invalid calculation parameters provided.',
        'insufficient_data': 'Insufficient data for accurate calculations.',
        'unrealistic_results': 'Calculated results appear unrealistic.'
    }
}

# Success messages
SUCCESS_MESSAGES = {
    'analysis_complete': 'Solar analysis completed successfully!',
    'report_generated': 'PDF report generated successfully!',
    'data_retrieved': 'Solar data retrieved successfully!',
    'image_processed': 'Image processed successfully!'
}

# Regional regulatory information (simplified)
REGULATORY_INFO = {
    'united_states': {
        'federal_incentives': ['Investment Tax Credit (ITC)', 'MACRS Depreciation'],
        'common_permits': ['Building Permit', 'Electrical Permit', 'Utility Interconnection'],
        'codes': ['National Electrical Code (NEC)', 'International Building Code (IBC)'],
        'net_metering': 'Available in most states with varying policies'
    },
    'canada': {
        'federal_incentives': ['Canada Greener Homes Grant'],
        'common_permits': ['Building Permit', 'Electrical Permit', 'Utility Connection'],
        'codes': ['Canadian Electrical Code', 'National Building Code'],
        'net_metering': 'Available in most provinces'
    },
    'international': {
        'federal_incentives': ['Varies by country'],
        'common_permits': ['Local building and electrical permits required'],
        'codes': ['Local electrical and building codes apply'],
        'net_metering': 'Availability varies by location'
    }
}

# Default fallback values
DEFAULT_VALUES = {
    'roof_area_m2': 120,
    'usable_area_m2': 90,
    'roof_orientation': 'south',
    'roof_slope_degrees': 25,
    'shading_factor': 0.15,
    'annual_irradiance_kwh_m2': 1460,  # 4 kWh/m²/day average
    'system_size_kw': 6,
    'annual_energy_kwh': 7200,
    'electricity_rate_kwh': 0.12,
    'installation_cost_per_watt': 3.0
}
