#!/usr/bin/env python3
"""
Solar AI Platform Status Checker
Quick script to verify the platform is running correctly
"""

import requests
import sys
import time
from pathlib import Path

def check_server_status():
    """Check if the Streamlit server is running"""
    try:
        response = requests.get('http://localhost:8503', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running at http://localhost:8503")
            return True
        else:
            print(f"⚠️ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("⚠️ Server is slow to respond (timeout)")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        'app_modern.py',
        '.streamlit/config.toml',
        'static/js/neural_3d.js',
        'static/css/neural_background.css',
        'test_images'
    ]
    
    print("\n📁 Checking required files:")
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.glob('*')))
                print(f"   ✅ {file_path}/ ({file_count} files)")
            else:
                print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if required Python packages are installed"""
    # Map package names to their import names
    packages = {
        'streamlit': 'streamlit',
        'opencv-python': 'cv2',
        'pillow': 'PIL',
        'numpy': 'numpy',
        'requests': 'requests',
        'reportlab': 'reportlab'
    }

    print("\n📦 Checking dependencies:")
    missing_packages = []

    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (not installed)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 To install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main status check"""
    print("🌞 Solar AI Platform Status Check")
    print("=" * 40)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check files
    files_ok = check_files()
    
    # Check server
    print("\n🌐 Checking server status:")
    server_ok = check_server_status()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Status Summary:")
    
    if deps_ok and files_ok and server_ok:
        print("✅ All systems operational!")
        print("🚀 Solar AI Platform is ready to use")
        print("🔗 Access at: http://localhost:8503")
    else:
        print("⚠️ Issues detected:")
        if not deps_ok:
            print("   • Missing dependencies")
        if not files_ok:
            print("   • Missing required files")
        if not server_ok:
            print("   • Server not running")
        
        print("\n💡 Suggested actions:")
        if not deps_ok:
            print("   1. Install missing dependencies")
        if not files_ok:
            print("   2. Ensure all project files are present")
        if not server_ok:
            print("   3. Start the server with: python start_solar_ai.py")
    
    print("=" * 40)

if __name__ == "__main__":
    main()
