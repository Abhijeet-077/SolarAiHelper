"""
Security utilities for API key management and environment variable validation.
Provides secure handling of sensitive configuration with validation and fallbacks.
"""

import os
import logging
import warnings
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
import re

class SecurityManager:
    """
    Centralized security manager for API keys and sensitive configuration.
    Provides validation, fallbacks, and secure access to environment variables.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_environment()
        self._validate_security_setup()
    
    def _load_environment(self):
        """Load environment variables from .env file if it exists."""
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key and value and not os.getenv(key):
                                os.environ[key] = value
                self.logger.info("Environment variables loaded from .env file")
            except Exception as e:
                self.logger.warning(f"Could not load .env file: {e}")
        else:
            self.logger.warning("No .env file found. Using system environment variables only.")
    
    def _validate_security_setup(self):
        """Validate security configuration and warn about potential issues."""
        issues = []
        
        # Check for .env file in gitignore
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                if '.env' not in gitignore_content:
                    issues.append("⚠️  .env file not found in .gitignore")
        else:
            issues.append("⚠️  No .gitignore file found")
        
        # Check for example file
        if not Path('.env.example').exists():
            issues.append("⚠️  No .env.example file found")
        
        if issues:
            self.logger.warning("Security setup issues found:")
            for issue in issues:
                self.logger.warning(f"  {issue}")
    
    def get_api_key(self, key_name: str, required: bool = True, 
                   min_length: int = 10) -> Optional[str]:
        """
        Securely retrieve and validate API key from environment.
        
        Args:
            key_name: Name of the environment variable
            required: Whether the key is required for operation
            min_length: Minimum expected length for validation
            
        Returns:
            API key if valid, None if not found/invalid
        """
        key_value = os.getenv(key_name)
        
        if not key_value:
            if required:
                self.logger.error(f"🔑 Required API key '{key_name}' not found in environment")
                self.logger.error(f"   Please set {key_name} in your .env file or environment")
                return None
            else:
                self.logger.info(f"Optional API key '{key_name}' not configured")
                return None
        
        # Basic validation
        if len(key_value) < min_length:
            self.logger.error(f"🔑 API key '{key_name}' appears invalid (too short)")
            return None
        
        # Check for placeholder values
        placeholder_patterns = [
            'your_.*_key_here',
            'replace_with_.*',
            'enter_your_.*',
            'api_key_here',
            'xxx.*',
            'test.*key'
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, key_value, re.IGNORECASE):
                self.logger.error(f"🔑 API key '{key_name}' appears to be a placeholder value")
                return None
        
        self.logger.debug(f"✅ API key '{key_name}' validated successfully")
        return key_value
    
    def get_config_value(self, key_name: str, default: Any = None, 
                        value_type: type = str) -> Any:
        """
        Get configuration value with type conversion and fallback.
        
        Args:
            key_name: Environment variable name
            default: Default value if not found
            value_type: Expected type for conversion
            
        Returns:
            Configuration value with proper type
        """
        value = os.getenv(key_name)
        
        if value is None:
            if default is not None:
                self.logger.debug(f"Using default value for '{key_name}': {default}")
                return default
            return None
        
        # Type conversion
        try:
            if value_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif value_type == int:
                return int(value)
            elif value_type == float:
                return float(value)
            else:
                return value
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid value for '{key_name}': {value}. Using default: {default}")
            return default
    
    def validate_all_api_keys(self) -> Tuple[bool, Dict[str, str]]:
        """
        Validate all required API keys for the application.
        
        Returns:
            Tuple of (all_valid, status_dict)
        """
        status = {}
        all_valid = True
        
        # Required API keys
        required_keys = {
            'GOOGLE_LLM_API_KEY': {'min_length': 20, 'description': 'Google Generative AI'},
            'NASA_API_KEY': {'min_length': 15, 'description': 'NASA POWER API'}
        }
        
        # Optional API keys
        optional_keys = {
            'GOOGLE_MAPS_API_KEY': {'min_length': 20, 'description': 'Google Maps API'},
            'OPENWEATHER_API_KEY': {'min_length': 15, 'description': 'OpenWeather API'}
        }
        
        # Validate required keys
        for key, config in required_keys.items():
            api_key = self.get_api_key(key, required=True, min_length=config['min_length'])
            if api_key:
                status[key] = f"✅ {config['description']} - Configured"
            else:
                status[key] = f"❌ {config['description']} - Missing or Invalid"
                all_valid = False
        
        # Validate optional keys
        for key, config in optional_keys.items():
            api_key = self.get_api_key(key, required=False, min_length=config['min_length'])
            if api_key:
                status[key] = f"✅ {config['description']} - Configured"
            else:
                status[key] = f"⚪ {config['description']} - Optional (Not Configured)"
        
        return all_valid, status
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive security status report.
        
        Returns:
            Dictionary containing security status information
        """
        all_valid, api_status = self.validate_all_api_keys()
        
        # Check file security
        file_security = {
            '.env_exists': Path('.env').exists(),
            '.env_example_exists': Path('.env.example').exists(),
            'gitignore_exists': Path('.gitignore').exists(),
        }
        
        # Configuration status
        config_status = {
            'debug_mode': self.get_config_value('DEBUG', False, bool),
            'app_env': self.get_config_value('APP_ENV', 'development'),
            'api_timeout': self.get_config_value('API_TIMEOUT', 30, int),
            'max_retries': self.get_config_value('API_MAX_RETRIES', 3, int),
        }
        
        return {
            'api_keys_valid': all_valid,
            'api_key_status': api_status,
            'file_security': file_security,
            'configuration': config_status,
            'recommendations': self._get_security_recommendations(all_valid, file_security)
        }
    
    def _get_security_recommendations(self, api_keys_valid: bool, 
                                    file_security: Dict[str, bool]) -> list:
        """Generate security recommendations based on current status."""
        recommendations = []
        
        if not api_keys_valid:
            recommendations.append("🔑 Configure missing required API keys in .env file")
        
        if not file_security.get('.env_example_exists'):
            recommendations.append("📝 Create .env.example file with template values")
        
        if not file_security.get('gitignore_exists'):
            recommendations.append("🚫 Create .gitignore file to exclude sensitive files")
        
        if file_security.get('.env_exists'):
            recommendations.append("✅ Ensure .env file is never committed to version control")
        
        recommendations.extend([
            "🔄 Rotate API keys regularly",
            "📊 Monitor API usage to avoid unexpected charges",
            "🔒 Use different API keys for different environments",
            "⚡ Consider using API key management services for production"
        ])
        
        return recommendations

# Global security manager instance
security_manager = SecurityManager()

# Convenience functions for backward compatibility
def get_api_key(key_name: str, required: bool = True) -> Optional[str]:
    """Get API key with validation."""
    return security_manager.get_api_key(key_name, required)

def validate_api_keys() -> Tuple[bool, Dict[str, str]]:
    """Validate all API keys."""
    return security_manager.validate_all_api_keys()

def get_config(key_name: str, default: Any = None, value_type: type = str) -> Any:
    """Get configuration value with fallback."""
    return security_manager.get_config_value(key_name, default, value_type)
