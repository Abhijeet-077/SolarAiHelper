#!/usr/bin/env python3
"""
Solar AI Helper - Application Launcher
This script helps launch the Streamlit application with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    package_imports = {
        'streamlit': 'streamlit',
        'opencv-python': 'cv2',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'google-generativeai': 'google.generativeai',
        'requests': 'requests'
    }

    missing_packages = []
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False

    print("✅ All required dependencies are installed")
    return True

def check_environment():
    """Check environment variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found. Copy .env.example to .env and configure your API keys.")
        print("The application will work with limited functionality without API keys.")
    
    # Load environment variables from .env file if it exists
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check for API keys
    google_key = os.getenv('GOOGLE_LLM_API_KEY')
    nasa_key = os.getenv('NASA_API_KEY')
    
    if not google_key or google_key == 'your_google_gemini_api_key_here':
        print("⚠️  Google Gemini API key not configured. AI recommendations will be limited.")
    else:
        print("✅ Google Gemini API key configured")
    
    if not nasa_key or nasa_key == 'your_nasa_power_api_key_here':
        print("⚠️  NASA API key not configured. Will use fallback solar data.")
    else:
        print("✅ NASA API key configured")

def main():
    """Main function to launch the application"""
    print("🌞 Solar AI Helper - Starting Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    print("\n🚀 Launching Streamlit application...")
    print("The application will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the application")
    print("=" * 50)
    
    # Launch Streamlit
    try:
        # Try to launch the main app first
        if Path('app.py').exists():
            subprocess.run(['streamlit', 'run', 'app.py', '--server.port', '8501'], check=True)
        elif Path('app_enhanced.py').exists():
            subprocess.run(['streamlit', 'run', 'app_enhanced.py', '--server.port', '8501'], check=True)
        else:
            print("❌ No app.py or app_enhanced.py found!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it using: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
